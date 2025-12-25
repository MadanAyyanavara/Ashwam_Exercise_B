ASHWAM – LANGUAGE DETECTION LOGIC (EXERCISE B) DETAILED TECHNICAL EXPLANATION

INTRODUCTION Ashwam receives highly informal mental-health journal
entries written in English, Hindi, Hinglish and mixed scripts. These
entries are short (often under 10 words), emoji-rich and contain
spelling variations. Most language detection models are trained on clean
formal text and fail in such environments. Hence this system is designed
to be deterministic, explainable and privacy-safe.

DESIGN PRINCIPLES 
1. Deterministic – same input always gives same output.
2. Lightweight – no ML model, no paid APIs.
3. Explainable – every prediction exposes evidence.
4. Robust to noise – handles emojis, numbers, spelling errors.
5. Safe for healthcare – no external data transfer.

SCRIPT DETECTION Each character is scanned and classified using Unicode
ranges: Latin: U+0000–U+007F, U+0080–U+024F Devanagari: U+0900–U+097F
Other: any non-Latin and non-Devanagari (Korean, etc.)

Ratios are computed: latin_ratio = latin_chars / total_chars
devanagari_ratio = dev_chars / total_chars other_ratio = other_chars /
total_chars

SCRIPT CLASSIFICATION If only Latin → latin If only Devanagari →
devanagari If both Latin and Devanagari → mixed If other dominates →
other

LEXICAL SIGNALS Two dictionaries are used: Roman Hindi Lexicon (haan,
nahi, mujhe, aaj, kal, thoda, yaar, etc.) English Stopword List (the,
is, was, and, but, to, etc.)

Tokens are normalized and matched to these lists.

LANGUAGE DECISION LOGIC Rule based aggregation:

If devanagari_ratio > 0.6 → hi Else if latin_ratio > 0.6 and
hi_lexicon_hits >= 1 → hinglish Else if latin_ratio > 0.6 and
en_stopword_hits >= 1 → en Else if hi_lexicon_hits >= 1 and
en_stopword_hits >= 1 → mixed Else if mixed scripts present → mixed Else
if n_tokens <= 2 or mostly symbols → unknown

CONFIDENCE COMPUTATION Confidence is computed using: confidence = (0.5 *
max_script_ratio) + (0.3 * lexical_strength) + (0.2 *
token_volume_score)

Where: lexical_strength = min((hi_hits + en_hits)/n_tokens, 1)
token_volume_score = min(n_tokens/10, 1)

Confidence is clamped between 0 and 1.

EVIDENCE OBJECT Each output includes: latin_ratio devanagari_ratio
other_ratio hi_lexicon_hits en_stopword_hits n_tokens

This ensures every classification is transparent.

UNKNOWN HANDLING Used when: Only numbers/punctuation Very short tokens
(ok, hi, fine) Emoji-only text

OTHER SCRIPT HANDLING If majority characters are from unknown scripts
(Korean, Chinese), label: script = other primary_language = unknown

LIMITATIONS 
1. Overlapping words between English and Hindi.
2. Slang and unseen spellings.
3. No sentence-level segmentation.

FUTURE IMPROVEMENTS 
1. Larger phonetic lexicons.
2. Per-sentence detection.
3. ML fallback classifier.
4. Support for regional Indian languages.
