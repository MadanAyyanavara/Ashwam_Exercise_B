ASHWAM – LANGUAGE DETECTION LOGIC (EXERCISE B)

Lightweight deterministic language and script detection for short messy
Hinglish journaling text.

This project detects: English, Hindi (Devanagari), Hinglish, Mixed and
Unknown texts. It also detects script type, provides confidence and
transparent evidence signals.

WHY THIS EXISTS Ashwam journals are very short, emoji-heavy,
code-switched and mixed script. Traditional detectors fail here.

WHAT THIS DETECTS Primary Language Labels: en, hi, hinglish, mixed,
unknown

Script Labels: latin, devanagari, mixed, other

APPROACH 
1. Script detection using Unicode ranges
2. Hindi Roman lexicon hits
3. English stopword hits
4. Deterministic rule based classification
5. Confidence computed from ratios and token counts

CLI USAGE lang_detect –in texts.jsonl –out lang.jsonl

TESTING Includes tests for Hinglish, Devanagari, Mixed, Unknown and
Other script handling.

KNOWN LIMITATIONS Some borderline Hinglish vs English cases may be
misclassified.

FUTURE IMPROVEMENTS Add more languages, phonetic normalization and ML
fallback models.
