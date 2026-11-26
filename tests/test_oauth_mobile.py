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
    assert "Horror & Suspense" not in niches.NAMES
    p = P.Plan.model_validate(json.loads((Path(P.__file__).parent / "sample_plan.json").read_text(encoding="utf-8")))
    en_only = p.model_copy(update={"hindi": None})
    assert any("`hindi` block" in x for x in P._lang_and_fiction_problems(en_only))
    monkeypatch.setattr(cfg, "LANGS", "en")
    assert not P._lang_and_fiction_problems(en_only)
    assert P.INTRO_CUE.search("Tonight: one hotel, one rule and a bell that rings by itself.")


def test_monetization_scoreboard():
    from shorts import channel_trends as ct
    d = {"days": 28, "channel": {"subscriberCount": 47}, "split": [{"creatorContentType": "shorts", "views": 1789}],
         "analytics": [{"estimatedMinutesWatched": 240, "views": 900, "subscribersGained": 1}, {"estimatedMinutesWatched": 60, "views": 900, "subscribersGained": 1}],
         "videos": [{"title": "a", "privacy": "public"}, {"title": "b", "privacy": "private"}]}
    m = ct.monetization(d)
    assert m["to_1000"] == 953 and m["to_500"] == 453 and m["watch_hours_last_28d"] == 5.0 and m["watch_hours_if_pace_holds_12m"] == 65
    assert m["shorts_views_last_28d"] == 1789 and m["videos_not_public"] == 1 and m["subscribers_per_1000_views"] == 1.11


def test_progress_report_milestones_and_uploads(tmp_path, monkeypatch):
    import datetime as dt
    from shorts import progress as pr
    today = dt.date(2026, 11, 29)
    hist = [{"date": "2026-11-28", "videos": {"en": {"video_id": "a"}, "hi": {"video_id": "b"}}},
            {"date": "2026-11-29", "videos": {"en": {"video_id": "c"}}},
            {"date": "2026-11-29", "videos": {"en": {"video_id": "c"}}}]                     # a re-run repeats the id: counted once
    up = pr.upload_stats(hist, [{"date": "2026-11-27", "videos": {"en": {"video_id": "d"}}}], today)
    assert up["week"] == {"short": 3, "documentary": 1, "en": 3, "hi": 1} and up["streak"] == 3
    data = {"available": True, "days": 28, "channel": {"subscriberCount": 120, "viewCount": 9000, "videoCount": 30},
            "split": [{"creatorContentType": "shorts", "views": 5000, "averageViewPercentage": 55.0}],
            "analytics": [{"views": 1200, "estimatedMinutesWatched": 600, "subscribersGained": 6}],
            "totals_365d": {"minutes": 9000, "shorts_minutes": 600}, "shorts_90d": {"views": 20000}, "videos": []}
    snap = pr.snapshot(data, hist, [], today)
    assert snap["subscribers"] == 120 and snap["watch_hours_365d"] == 150.0 and snap["shorts_views_90d"] == 20000 and snap["best_video_views"] == 1200
    ladders = pr._load(pr.MILESTONES, {})["ladders"]
    reached = {"subscribers>=50": "2026-11-20"}
    st = pr.evaluate(snap, ladders, reached)
    subs = next(m for m in st if m["key"] == "subscribers")
    assert [r["step"] for r in subs["reached"]] == [50, 100] and subs["reached"][0]["date"] == "2026-11-20" and subs["reached"][1]["date"] == "2026-11-29"
    assert subs["next"]["step"] == 250 and 0 < subs["next"]["progress"] < 100
    na = pr.evaluate({**snap, "watch_hours_365d": None}, ladders, {})
    assert next(m for m in na if m["key"] == "watch_hours_365d")["reached"] == []                  # n/a never reaches a milestone
    text = pr.render(snap, {"subscribers": 100, "date": "2026-11-22"}, st, {"available": False, "reason": "x"}, {})
    assert "Weekly progress report - 2026-11-29" in text and "+20 vs last report" in text and "Reached this week" in text


def test_every_description_gets_a_one_tap_subscribe_link():
    from shorts import strategy
    d = strategy.with_subscribe("A video. #Shorts")
    assert "https://www.youtube.com/@nayankabiraj?sub_confirmation=1" in d and strategy.with_subscribe(d) == d
    assert "सब्सक्राइब" in strategy.with_subscribe("वीडियो", "hi")


def test_seo_tools_pure_parts(monkeypatch):
    from shorts import seo
    ex = seo.expansions("how does gps work")
    assert ex[0] == "how does gps work" and "why how does gps work" in ex and not any(x.startswith("how how") for x in ex) and "how does gps work a" in ex
    assert seo.parse_suggest(["q", ["a b", "c"], {}]) == ["a b", "c"] and seo.parse_suggest("junk") == []
    r = seo.rank([["gps in phone", "gps for kids"], ["gps in phone", "unrelated thing"]], "gps")
    assert r[0]["phrase"] == "gps in phone" and all("unrelated" not in x["phrase"] for x in r)

    class Resp:
        def json(self):
            return ["q", ["gps how it works", "gps accuracy"]]
    monkeypatch.setattr("requests.get", lambda *a, **k: Resp())
    monkeypatch.setattr(seo.time, "sleep", lambda s: None)
    assert seo.suggest("gps")[0]["phrase"] in ("gps how it works", "gps accuracy")
    ent = [{"title": "How GPS works?", "channel": "A", "view_count": 500000, "channel_follower_count": 10000, "upload_date": "20260101", "duration": 45, "tags": ["gps", "tech"]},
           {"title": "GPS explained", "channel": "B", "view_count": 3000, "channel_follower_count": 2000000, "upload_date": "20250101", "duration": 600, "tags": ["gps"]},
           {"title": "GPS in your phone", "channel": "C", "view_count": 90000, "channel_follower_count": 40000, "upload_date": "20260301", "duration": 55, "tags": ["gps"]}, None]
    d = seo.outlier_digest(ent, today_ord=__import__("datetime").date(2026, 6, 1).toordinal())
    assert d["videos"] == 3 and d["outliers"][0]["channel"] == "A" and d["outliers"][0]["ratio"] == 50.0 and d["share_shorts"] == 0.67 and d["common_tags"] == ["gps"]
    assert not seo.outlier_digest([None, {"title": "x"}])["available"]


def test_report_lists_search_terms():
    from shorts import progress as pr
    snap = {"date": "2026-11-29", "available": True, "uploads_7d_detail": {}}
    text = pr.render(snap, None, [], {"available": True, "search_terms": [{"term": "how gps works", "views": 12, "minutes": 3.5}]}, {})
    assert '"how gps works": 12 views' in text
    assert "no search traffic" in pr.render(snap, None, [], {"available": True}, {})


def test_seo_outliers_use_the_data_api_for_numbers(monkeypatch):
    from shorts import seo
    vids = [{"id": "a", "snippet": {"title": "How GPS works?", "channelTitle": "A", "channelId": "c1", "publishedAt": "2026-01-01T00:00:00Z", "tags": ["gps"]},
             "statistics": {"viewCount": "500000"}, "contentDetails": {"duration": "PT45S"}}]
    e = seo.to_entries(vids, {"c1": 10000})[0]
    assert e["view_count"] == 500000 and e["channel_follower_count"] == 10000 and e["upload_date"] == "20260101" and e["duration"] == 45
    d = seo.outlier_digest([e], today_ord=__import__("datetime").date(2026, 6, 1).toordinal())
    assert d["outliers"][0]["ratio"] == 50.0
    monkeypatch.setattr(seo, "search_ids", lambda q, n=15: [])
    assert seo.outliers("x") == {"available": False, "reason": "no search results returned"}


def test_preview_contact_sheet_and_run_brief(tmp_path):
    import subprocess
    from generated_animations.authoring import preview
    v = tmp_path / "t.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=540x960:rate=10:duration=4", "-pix_fmt", "yuv420p", str(v)], check=True)
    out = preview.contact_sheet(v, tmp_path / "sheet.png", n=6, width=90, cols=3)
    from PIL import Image
    assert Image.open(out).size[0] == 270
    from shorts import runbrief
    text = runbrief.brief()
    assert text.startswith("# Run brief") and "Channel check:" in text and "research_summary must contain" in text
    assert "6 uploads" in runbrief.target(runbrief.ROOT / "strategy" / "learnings.md")
    assert runbrief.check_line({}, {"available": False, "reason": "x"}, __import__("datetime").date(2026, 11, 25)).startswith("Channel check: NOT AVAILABLE")


def test_eligibility_section():
    import datetime as dt
    from shorts import progress as pr
    today = dt.date(2026, 11, 29)
    data = {"available": True, "channel_status": {"isLinked": True, "longUploadsStatus": "longUploadsUnspecified"},
            "videos": [{"privacy": "public", "published": "2026-11-20T00:00:00Z"}, {"privacy": "private", "published": "2026-11-21T00:00:00Z"}, {"privacy": "public", "published": "2026-01-01T00:00:00Z"}]}
    snap = {"subscribers": 47, "watch_hours_365d": 8.2, "shorts_views_90d": 2000}
    txt = "\n".join(pr.eligibility(data, snap, today))
    assert "47 of 500 (9.4 %) - not met" in txt and "Public uploads in the last 90 days: 1 of 3" in txt and "Eligible by these numbers: NO" in txt and "isLinked=True" in txt
    big = {"subscribers": 1200, "watch_hours_365d": 4100, "shorts_views_90d": 0}
    assert "Eligible by these numbers: YES" in "\n".join(pr.eligibility(data, big, today))
    assert "NOT AVAILABLE" in pr.eligibility({"available": False}, snap, today)[0]
    assert "## Partner Program eligibility" in pr.render({"date": "2026-11-29", "available": True, "uploads_7d_detail": {}}, None, [], {"available": False}, {}, elig=["x"])


def test_tier_progress_and_brief_line():
    from shorts import progress as pr
    tp = pr.tier_progress({"subscribers": 250, "watch_hours_365d": 1500, "shorts_views_90d": 100})
    assert tp == {"fan": 50.0, "ads": 25.0}                                     # subs 50 % / 25 %, hours 50 % / 37.5 %: the slowest decides
    assert pr.tier_progress({"subscribers": None, "watch_hours_365d": 1, "shorts_views_90d": 1})["fan"] is None
    from shorts import runbrief
    assert "Partner Program eligibility" in runbrief.brief()


def test_patterns_follow_what_works():
    import datetime as dt
    from shorts import patterns as pt
    today = dt.date(2026, 11, 30)
    def vid(i, title, views, age, sec=50):
        d = (today - dt.timedelta(days=age)).isoformat()
        return {"id": f"v{i}", "title": title, "views": views, "published": d + "T00:00:00Z", "duration": f"PT{sec}S", "privacy": "public"}
    vs = [vid(1, "Why does a phone get hot?", 400, 4), vid(2, "How does GPS work?", 300, 5), vid(3, "Haunted hotel story #horrorstory", 900, 3), vid(4, "The mystery village #horrorstory", 700, 4),
          vid(5, "Why do stars twinkle?", 20, 6), vid(6, "What if the Moon vanished?", 30, 7), vid(7, "Brand new video", 5, 1), vid(8, "Old video", 5000, 90)]
    hist = [{"date": "x", "niche": "How Tech Works", "videos": {"en": {"video_id": "v1"}}, "follow_ups": ["next one"]}, {"date": "x", "niche": "Space & Universe", "videos": {"en": {"video_id": "v5"}}},
            {"date": "x", "niche": "Space & Universe", "videos": {"en": {"video_id": "v6"}}}, {"date": "x", "niche": "How Tech Works", "videos": {"en": {"video_id": "v2"}}}]
    p = pt.analyse({"available": True, "videos": vs, "analytics": []}, hist, [], today)
    assert p["available"] and p["videos"] == 6                                   # the 1-day-old and the 90-day-old video are not judged
    fams = {f["name"]: f for f in p["families"]}
    assert fams["story"]["lift"] > fams["space+nature"]["lift"] and fams["story"]["n"] == 2 and fams["story"]["confidence"] == "low (n<3)"
    assert "story" not in {x["family"] for x in p["recommended_slots"]} and len(p["recommended_slots"]) >= 2      # the story family is retired: analysed, never recommended
    assert p["part2_candidates"] and p["part2_candidates"][0]["title"].startswith(("Haunted", "The mystery"))
    assert "RECOMMENDED SLOTS TODAY" in pt.digest(p)
    assert not pt.analyse({"available": True, "videos": vs[:2], "analytics": []}, hist, [], today)["available"]               # too little data: no pattern claimed
    assert pt.title_shape("Why does ice float?") == "question/why" and pt.length_bucket(38) == "short <=40s" and pt.family(None, "A haunted tale") == "story"


def test_story_family_is_retired_and_doc_days(monkeypatch):
    import datetime as dt
    from shorts import patterns as pt, runbrief
    assert "story" in pt.RETIRED
    assert "DOCUMENTARY DAY (Sunday)" in runbrief.brief(dt.datetime(2026, 11, 29, 9, 0, tzinfo=runbrief.IST))
    assert "DOCUMENTARY DAY (Wednesday)" in runbrief.brief(dt.datetime(2026, 12, 9, 9, 0, tzinfo=runbrief.IST))
    assert "3 Short topics" in runbrief.brief(dt.datetime(2026, 12, 2, 9, 0, tzinfo=runbrief.IST))            # Wednesday before 9 Dec


def test_explore_slot_goes_to_the_thinnest_remaining_family():
    import datetime as dt
    from shorts import patterns as pt
    today = dt.date(2026, 11, 30)
    def vid(i, title, views, age=5):
        return {"id": f"v{i}", "title": title, "views": views, "published": (today - dt.timedelta(days=age)).isoformat() + "T00:00:00Z", "duration": "PT50S", "privacy": "public"}
    vs, hist = [], []
    for i, (niche, views) in enumerate([("How Tech Works", 300), ("How Tech Works", 200), ("How Tech Works", 100), ("Space & Universe", 500), ("Space & Universe", 400), ("Space & Universe", 300), ("Brain & Psychology", 900)]):
        vs.append(vid(i, f"Why test {i}?", views))
        hist.append({"date": "x", "niche": niche, "videos": {"en": {"video_id": f"v{i}"}}})
    p = pt.analyse({"available": True, "videos": vs, "analytics": []}, hist, [], today)
    fam = [s["family"] for s in p["recommended_slots"]]
    assert fam[:2] == ["space+nature", "tech"] and fam[2] == "mind+body" and "explore" in p["recommended_slots"][2]["why"]   # 1 video of mind+body: only the explore slot, despite its high score
