# tests/test_core.py

from lang_detect.core import detect_for_text


def test_devanagari_hi():
    text = "आज बहुत थकान है 😩"
    res = detect_for_text("t_003", text)
    assert res["script"] == "devanagari"
    assert res["primary_language"] == "hi"


def test_english_en():
    text = "Cramps today. Energy low."
    res = detect_for_text("t_001", text)
    assert res["script"] == "latin"
    assert res["primary_language"] == "en"


def test_hinglish():
    text = "Aaj headache hai, mood off hai yaar."
    res = detect_for_text("t_002", text)
    assert res["script"] == "latin"
    assert res["primary_language"] in ("hinglish", "mixed")


def test_mixed_script():
    text = "आज meeting thi but mood खराब था"
    res = detect_for_text("t_008", text)
    assert res["script"] == "mixed"
    assert res["primary_language"] == "mixed"


def test_unknown_short():
    text = "12345 !!!"
    res = detect_for_text("t_021", text)
    assert res["primary_language"] == "unknown"
