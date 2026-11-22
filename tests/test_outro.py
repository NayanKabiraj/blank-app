from shorts import outro
from shorts.plan import Chapter, DocScript, LangScript, Scene


def _short(lang="en"):
    return LangScript(title="t", description="d", tags=["a"], hook_text="h", scenes=[Scene(text="One."), Scene(text="Two?")])


def test_short_gets_outro_once():
    for lang in ("en", "hi"):
        s = outro.with_outro(_short(), lang)
        assert len(s.scenes) == 3 and s.scenes[-1].text == outro.OUTRO_TEXT[lang]
        assert s.scenes[-1].keyword in s.scenes[-1].text
        assert outro.with_outro(s, lang) is s   # idempotent


def test_documentary_outro_goes_in_last_chapter():
    d = DocScript(title="t", description="d", tags=["a"],
                  chapters=[Chapter(title="A", scenes=[Scene(text="a")]), Chapter(title="B", scenes=[Scene(text="b")])])
    out = outro.with_outro(d, "en")
    assert len(out.chapters) == 2 and len(out.chapters[0].scenes) == 1
    assert out.scenes[-1].text == outro.OUTRO_TEXT["en"]


def test_text_and_hindi_script():
    assert "like, share and subscribe" in outro.OUTRO_TEXT["en"].lower()
    assert any("ऀ" <= c <= "ॿ" for c in outro.OUTRO_TEXT["hi"])
    assert len(outro.OUTRO_HEADLINE["en"]) <= 28 and len(outro.OUTRO_HEADLINE["hi"]) <= 28
