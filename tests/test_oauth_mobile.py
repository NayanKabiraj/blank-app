"""Phone-first Google sign-in (shorts/ytauth.py): error classification, pending authorization, callback checks, token storage."""
import datetime as dt
import json
import urllib.parse

import pytest

from shorts import config, pending, ytauth


class Resp:
    def __init__(self, status=200, body=None):
        self.status_code, self._b, self.content = status, body or {}, b"x"

    def json(self):
        return self._b


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "YT_CLIENT_ID", "client-id")
    monkeypatch.setattr(config, "YT_CLIENT_SECRET", "client-secret")
    monkeypatch.setattr(config, "YT_REFRESH_TOKENS", {"en": "", "hi": ""})
    monkeypatch.setattr(ytauth, "PENDING", tmp_path / "oauth_pending.json")
    monkeypatch.setattr(ytauth, "STATUS", tmp_path / "oauth_status.json")
    monkeypatch.setattr(ytauth, "_queued", lambda: ["2026-11-24_short_en"])
    for k in pending._state:
        pending._state[k] = False
    return tmp_path


class FakeHttp(Exception):
    def __init__(self, status, reason, msg=""):
        super().__init__(msg or reason)
        self.resp = type("R", (), {"status": status})()
        self.content = json.dumps({"error": {"errors": [{"reason": reason}], "message": msg}}).encode()


@pytest.mark.parametrize("exc,kind", [
    (Exception("invalid_grant: Token has been expired or revoked."), "auth"),
    (ytauth.AuthRequired("x"), "auth"),
    (FakeHttp(403, "quotaExceeded"), "quota"),
    (FakeHttp(400, "uploadLimitExceeded"), "quota"),
    (FakeHttp(403, "rateLimitExceeded"), "rate"),
    (FakeHttp(429, ""), "rate"),
    (FakeHttp(403, "insufficientPermissions"), "scope"),
    (Exception("Request had insufficient authentication scopes."), "scope"),
    (FakeHttp(503, "backendError"), "retry"),
    (TimeoutError("timed out"), "retry"),
    (ValueError("something else"), "other"),
])
def test_error_classes(exc, kind):
    assert ytauth.classify(exc) == kind


def test_only_auth_errors_ask_for_authorization(env):
    for exc in (FakeHttp(403, "quotaExceeded"), FakeHttp(403, "insufficientPermissions"), FakeHttp(503, ""), TimeoutError()):
        assert pending._on_error(exc, "x") != "auth"
    assert not ytauth.PENDING.exists()
    assert pending._on_error(Exception("invalid_grant: Token has been expired or revoked."), "x") == "auth"
    assert ytauth.PENDING.exists() and pending._state["auth"]


def test_authorization_request_is_https_pkce_and_secret_free(env):
    rec = ytauth.request_authorization("Refresh token expired or was revoked (invalid_grant).")
    u = urllib.parse.urlparse(rec["auth_url"])
    q = urllib.parse.parse_qs(u.query)
    assert u.scheme == "https" and u.netloc == "accounts.google.com"
    assert q["redirect_uri"][0].startswith("https://") and "localhost" not in rec["auth_url"]
    assert q["access_type"] == ["offline"] and q["code_challenge_method"] == ["S256"] and q["state"] == [rec["state"]]
    text = ytauth.PENDING.read_text() + ytauth.banner(rec)
    assert "client-secret" not in text and "code_verifier" not in text
    b = ytauth.banner(rec)
    assert b.startswith("🔐 Google authorization required") and "Reason: Refresh token expired or was revoked." in b
    assert "Tap here to authorize YTConnect" in b and rec["auth_url"] in b and "2026-11-24_short_en" in b
    assert ytauth.request_authorization("again")["state"] == rec["state"]            # an outstanding request is reused, not duplicated


def _post(monkeypatch, scope="https://www.googleapis.com/auth/youtube.upload", refresh="new-refresh"):
    calls = []

    def post(url, data=None, timeout=0):
        calls.append(dict(data))
        if data["grant_type"] == "authorization_code":
            body = {"access_token": "a", "scope": scope}
            if refresh:
                body["refresh_token"] = refresh
            return Resp(200, body)
        return Resp(200, {"access_token": "b"})
    monkeypatch.setattr(ytauth.requests, "post", post)
    return calls


def test_callback_success_stores_encrypted_token_and_clears_pending(env, monkeypatch):
    rec = ytauth.request_authorization("invalid_grant")
    calls = _post(monkeypatch)
    ok, msg = ytauth.complete("the-code", rec["state"])
    assert ok and "new-refresh" not in msg and "the-code" not in msg
    assert calls[0]["code_verifier"] and calls[0]["redirect_uri"] == rec["redirect_uri"]
    assert b"new-refresh" not in ytauth.token_file("en").read_bytes()               # encrypted at rest
    assert ytauth.load_saved_token("en") == "new-refresh" and not ytauth.PENDING.exists()
    assert json.loads(ytauth.STATUS.read_text())["status"] == "restored"


def test_callback_rejects_wrong_state_expired_and_replay(env, monkeypatch):
    rec = ytauth.request_authorization("invalid_grant")
    _post(monkeypatch)
    assert not ytauth.complete("c", "not-the-state")[0] and not ytauth.token_file("en").exists()
    old = json.loads(ytauth.PENDING.read_text())
    old["expires_at"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)).isoformat(timespec="seconds")
    ytauth.PENDING.write_text(json.dumps(old))
    ok, msg = ytauth.complete("c", rec["state"])
    assert not ok and "expired" in msg and not ytauth.token_file("en").exists()
    assert not ytauth.banner()                                                        # an expired request is not shown
    rec2 = ytauth.request_authorization("invalid_grant")
    assert rec2["state"] != rec["state"]
    assert ytauth.complete("c", rec2["state"])[0]
    assert not ytauth.complete("c", rec2["state"])[0]                                 # single use


def test_missing_upload_permission_is_a_scope_problem(env, monkeypatch):
    rec = ytauth.request_authorization("invalid_grant")
    _post(monkeypatch, scope="https://www.googleapis.com/auth/youtube.readonly")
    ok, msg = ytauth.complete("c", rec["state"])
    assert not ok and "permission" in msg and not ytauth.token_file("en").exists()


def test_existing_token_is_kept_when_google_returns_no_new_one(env, monkeypatch):
    rec = ytauth.request_authorization("x")
    _post(monkeypatch, refresh="")
    monkeypatch.setattr(ytauth, "credentials", lambda lang="en", scopes=None: object())
    ok, msg = ytauth.complete("c", rec["state"])
    assert ok and "kept" in msg and not ytauth.token_file("en").exists()
    rec = ytauth.request_authorization("x")

    def dead(lang="en", scopes=None):
        raise ytauth.AuthRequired("dead")
    monkeypatch.setattr(ytauth, "credentials", dead)
    assert not ytauth.complete("c", rec["state"])[0]


def test_callback_text_parsing_and_no_secret_output():
    assert ytauth._parse_callback('{"state": "s1", "code": "4/abc"}') == ("4/abc", "s1")
    assert ytauth._parse_callback("https://x.github.io/o?code=4%2Fabc&state=s1&scope=y") == ("4/abc", "s1")


def test_stored_token_is_tried_first_then_the_secret(env, monkeypatch):
    monkeypatch.setattr(config, "YT_REFRESH_TOKENS", {"en": "secret-token", "hi": "secret-token"})
    ytauth.token_file("en").write_bytes(ytauth._fernet().encrypt(b"file-token"))
    assert ytauth.candidates("en") == ["file-token", "secret-token"]


def test_credentials_falls_back_then_raises_auth_required(env, monkeypatch):
    from google.auth.exceptions import RefreshError
    monkeypatch.setattr(config, "YT_REFRESH_TOKENS", {"en": "secret-token", "hi": ""})
    ytauth.token_file("en").write_bytes(ytauth._fernet().encrypt(b"file-token"))
    seen = []

    class C:
        def __init__(self, tok, **kw):
            self.tok = tok

        def refresh(self, req):
            seen.append(self.tok)
            if self.tok == "file-token":
                raise RefreshError("invalid_grant: Token has been expired or revoked.", {"error": "invalid_grant"})
    monkeypatch.setattr("google.oauth2.credentials.Credentials", lambda t, refresh_token=None, **kw: C(refresh_token))
    assert ytauth.credentials("en").tok == "secret-token" and seen == ["file-token", "secret-token"]
    seen.clear()
    monkeypatch.setattr("google.oauth2.credentials.Credentials", lambda t, refresh_token=None, **kw: type("D", (), {"refresh": lambda s, r: (_ for _ in ()).throw(RefreshError("invalid_grant", {}))})())
    with pytest.raises(ytauth.AuthRequired):
        ytauth.credentials("en")


def test_flush_stops_and_keeps_the_queue_when_authorization_is_needed(env, monkeypatch):
    from shorts import upload
    q = env / "videos"
    monkeypatch.setattr(config, "VIDEOS_DIR", q)
    monkeypatch.setattr(pending, "QUEUE", q / "unpublished")
    for n in ("a", "b"):
        d = q / "unpublished" / n
        d.mkdir(parents=True)
        (d / "video.mp4").write_bytes(b"v")
        (d / "meta.json").write_text(json.dumps({"lang": "en", "short": True, "date": "2026-11-24", "title": "t", "description": "d",
                                                  "tags": [], "privacy": "private", "attempts": 0, "last_error": ""}))
    calls = []

    def boom(*a, **k):
        calls.append(1)
        raise ytauth.AuthRequired("Refresh token expired or was revoked (invalid_grant).")
    monkeypatch.setattr(upload, "upload", boom)
    r = pending.flush()
    assert r["auth_required"] and r["left"] == 2 and len(calls) == 1                  # the second video is not even tried
    assert (q / "unpublished" / "a" / "video.mp4").exists() and ytauth.banner()
    assert json.loads((q / "unpublished" / "a" / "meta.json").read_text())["attempts"] == 0


def test_trending_digest_and_hindi_vox_helpers():
    from shorts import channel_trends as ct
    from generated_animations.shared import vox
    rows = [{"id": str(i), "title": t, "channel": "c", "views": 1000 * (i + 1), "seconds": s, "published": "2026-11-20", "tags": []}
            for i, (t, s) in enumerate([("Why does ice float? Science", 45), ("How planes fly in 3 steps", 600), ("Why does ice float on water", 50), ("Why does ice melt", 55)])]
    d = ct.trending_digest({"generated": "x", "charts": {"US/Education": rows, "IN/Education": {"error": "no chart"}}})
    assert d["available"] and d["videos"] == 4 and d["share_questions"] == 0.25 and d["share_under_60s"] == 0.75 and "ice" in d["recurring_words"]
    assert not ct.trending_digest({"charts": {}})["available"]
    assert ct._seconds("PT1M5S") == 65 and ct._seconds("PT2H") == 7200
    ctx = type("C", (), {"lang": "hi"})()
    assert vox.L(ctx, "JUST GUESSING?", "सिर्फ़ अंदाज़ा?") == "सिर्फ़ अंदाज़ा?" and vox.L(type("C", (), {"lang": "en"})(), "A", "B") == "A"
    from shorts import plan
    assert not plan._pack_is_bilingual("chatgpt_vox")


def test_hindi_is_back_and_stories_are_labelled_fiction(monkeypatch):
    import json
    from pathlib import Path
    from shorts import config as cfg, niches, plan as P
    assert "hi" in cfg.LANGS.split(",")
    assert "Horror & Suspense" in niches.NAMES
    p = P.Plan.model_validate(json.loads((Path(P.__file__).parent / "sample_plan.json").read_text(encoding="utf-8")))
    en_only = p.model_copy(update={"hindi": None})
    assert any("`hindi` block" in x for x in P._lang_and_fiction_problems(en_only))
    monkeypatch.setattr(cfg, "LANGS", "en")
    assert not P._lang_and_fiction_problems(en_only)
    story = p.model_copy(update={"niche": "Horror & Suspense", "hindi": None})
    assert any("fiction" in x for x in P._lang_and_fiction_problems(story))
    assert P.INTRO_CUE.search("Tonight: one hotel, one rule and a bell that rings by itself.")
