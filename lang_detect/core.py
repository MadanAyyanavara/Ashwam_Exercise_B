# lang_detect/core.py

import json
from .rules import HI_LATIN_WORDS, EN_WORDS, tokenize


def char_script_counts(text: str):
    latin = devanagari = other = 0
    for ch in text:
        code = ord(ch)
        if ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
            latin += 1
        elif 0x0900 <= code <= 0x097F:  # Devanagari block
            devanagari += 1
        elif ch.isspace() or ch.isdigit() or ch in ".,!?;:-_()[]{}'\"/\\+":
            # Neutral chars (ignored for script ratios)
            continue
        else:
            other += 1

    total_letters = latin + devanagari + other
    return {
        "latin": latin,
        "devanagari": devanagari,
        "other": other,
        "total_letters": total_letters,
    }


def decide_script(counts):
    total = counts["total_letters"]
    if total == 0:
        # No alphabetic content – treat script as 'other'
        return "other", 0.0, 0.0

    latin_ratio = counts["latin"] / total
    dev_ratio = counts["devanagari"] / total

    if latin_ratio > 0.9:
        script = "latin"
    elif dev_ratio > 0.9:
        script = "devanagari"
    elif counts["latin"] > 0 and counts["devanagari"] > 0:
        script = "mixed"
    else:
        script = "other"

    return script, latin_ratio, dev_ratio


def word_evidence(tokens):
    hi_hits = 0
    en_hits = 0
    for tok in tokens:
        if tok in HI_LATIN_WORDS:
            hi_hits += 1
        if tok in EN_WORDS:
            en_hits += 1
    return {
        "hi_lexicon_hits": hi_hits,
        "en_word_hits": en_hits,
        "n_tokens": len(tokens),
    }


def decide_primary_language(script, latin_ratio, dev_ratio, word_ev):
    n_tokens = word_ev["n_tokens"]
    hi_hits = word_ev["hi_lexicon_hits"]
    en_hits = word_ev["en_word_hits"]

    # 1. Very short or no tokens => unknown
    if n_tokens == 0:
        return "unknown"
    if n_tokens <= 1 and hi_hits == 0 and en_hits == 0:
        return "unknown"

    # 2. Dominantly Devanagari => hi
    if script == "devanagari" and dev_ratio > 0.9:
        return "hi"

    # 3. Mixed scripts or strong mix of hi + en => mixed
    if script == "mixed":
        return "mixed"
    if hi_hits > 0 and en_hits > 0:
        return "mixed"

    # 4. Latin-only logic
    if script == "latin":
        # Mainly Hindi words in Latin => hinglish
        if hi_hits >= 2 and hi_hits >= en_hits:
            return "hinglish"
        # Mainly English words => en
        if en_hits >= 2 and en_hits > hi_hits:
            return "en"
        # One Hindi word in very short sentence => hinglish
        if hi_hits == 1 and n_tokens <= 4:
            return "hinglish"
        # No lexicon hits
        if en_hits == 0 and hi_hits == 0:
            if n_tokens >= 2:
                return "en"
            return "unknown"

    # 5. Other script: try to infer from words, else unknown
    if script == "other":
        if en_hits > hi_hits and en_hits >= 1:
            return "en"
        if hi_hits > en_hits and hi_hits >= 1:
            return "hinglish"
        return "unknown"

    return "unknown"


def compute_confidence(primary_language, script, latin_ratio, dev_ratio, word_ev):
    n_tokens = word_ev["n_tokens"]
    hi_hits = word_ev["hi_lexicon_hits"]
    en_hits = word_ev["en_word_hits"]

    if primary_language == "unknown":
        return 0.2

    purity = max(latin_ratio, dev_ratio)
    recognized = hi_hits + en_hits
    lex_frac = recognized / n_tokens if n_tokens > 0 else 0.0

    # Simple deterministic combination
    conf = 0.3 + 0.4 * purity + 0.3 * lex_frac

    if primary_language in ("mixed",):
        # Mixed is inherently uncertain, slightly reduce
        conf -= 0.05

    # Clamp
    if conf < 0.0:
        conf = 0.0
    if conf > 1.0:
        conf = 1.0
    return conf


def detect_for_text(text_id, text):
    counts = char_script_counts(text)
    script, latin_ratio, dev_ratio = decide_script(counts)
    tokens = tokenize(text)
    word_ev = word_evidence(tokens)
    primary_language = decide_primary_language(script, latin_ratio, dev_ratio, word_ev)
    confidence = compute_confidence(
        primary_language, script, latin_ratio, dev_ratio, word_ev
    )

    evidence = {
        "latin_ratio": latin_ratio,
        "devanagari_ratio": dev_ratio,
        "hi_lexicon_hits": word_ev["hi_lexicon_hits"],
        "en_word_hits": word_ev["en_word_hits"],
        "n_tokens": word_ev["n_tokens"],
    }

    return {
        "id": text_id,
        "primary_language": primary_language,
        "script": script,
        "confidence": round(confidence, 2),
        "evidence": evidence,
    }
