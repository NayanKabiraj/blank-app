import importlib


def test_hindi_uses_the_english_token(monkeypatch):
    monkeypatch.setenv("YT_CLIENT_ID", "id")
    monkeypatch.setenv("YT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("YT_REFRESH_TOKEN", "main-token")
    monkeypatch.setenv("YT_REFRESH_TOKEN_HI", "stale-hindi-token")
    monkeypatch.delenv("YT_REFRESH_TOKEN_EN", raising=False)
    from shorts import config
    config = importlib.reload(config)
    assert config.YT_REFRESH_TOKENS == {"en": "main-token", "hi": "main-token"}
    monkeypatch.undo()
    importlib.reload(config)
