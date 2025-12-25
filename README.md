Ashwam Exercise B — Language Detection Logic
Deterministic, explainable language + script detector for short, messy journaling text in English, Hindi (Devanagari), and Hinglish (Hindi in Latin script). Designed for the Ashwam journaling context.
​

🚩 Problem
Ashwam users write very short journal entries that can be:

English

Hindi in Devanagari

Hinglish (Hindi words in Latin script)

Mixed, with code‑switching, emojis, and slang
​

Downstream components need to know which language/script each snippet is in so they can route text to the right parsing pipeline.
​

Goal: For each text snippet, output a primary language, script, confidence score, and evidence signals, using a small deterministic system (no paid APIs, no training).
​

✅ Features
For each input row {"id": "...", "text": "..."}, the system outputs:

primary_language ∈ {en, hi, hinglish, mixed, unknown}
​

script ∈ {latin, devanagari, mixed, other}
​

confidence ∈ [0, 1] (deterministic, heuristics‑based)
​

evidence: small numeric signals that justify the decision (ratios, counts)
​

Example:

json
{
  "id": "t_001",
  "primary_language": "en",
  "script": "latin",
  "confidence": 0.8,
  "evidence": {
    "latin_ratio": 1.0,
    "devanagari_ratio": 0.0,
    "hi_lexicon_hits": 0,
    "en_word_hits": 3,
    "n_tokens": 4
  }
}
🧱 Architecture
Project layout:

text
ashwam_lang_detect/
├── lang_detect/
│   ├── __init__.py
│   ├── rules.py      # Lexicons, tokenizer
│   ├── core.py       # Script detection, language logic, confidence
│   └── cli.py        # CLI wrapper: --in / --out
├── tests/
│   └── test_core.py  # Unit tests for required scenarios
├── texts.jsonl       # Synthetic dataset from the exercise
└── README.md
Pipeline
For each text:

Script detection (char level)

Count Latin vs Devanagari vs other characters using Unicode ranges.
​

Compute latin_ratio and devanagari_ratio.

Decide script ∈ {latin, devanagari, mixed, other} using thresholds (e.g. >0.9).
​

Tokenization + lexicons (word level)

Tokenize with a regex that keeps both Latin and Devanagari letters.

Count:

hi_lexicon_hits: matches in a small Hinglish lexicon (aaj, kal, hai, nahi, yaar, mujhe, etc.).
​

en_word_hits: matches in a small English lexicon (today, headache, cramps, work, meeting, etc.).
​

Language decision (rule engine)

Use script label, script ratios, lexicon hits, and token count to choose:

en – English, mostly Latin

hi – Hindi, mostly Devanagari

hinglish – Hindi in Latin script

mixed – clear Hindi + English and/or mixed scripts

unknown – too short / numeric / noisy
​

Confidence + evidence

Confidence combines:

Script purity (max(latin_ratio, devanagari_ratio))

Lexicon coverage ((hi_lexicon_hits + en_word_hits) / n_tokens)

Evidence object includes ratios and counts so decisions are explainable.

🧪 Hinglish vs English: how it’s decided
Distinguishing Hinglish from English is done via lexicon dominance (Latin script alone is not enough).
​

In Latin script:

If Hindi‑Latin words clearly dominate (hi_lexicon_hits >= 2 and hi_lexicon_hits >= en_word_hits) ⇒ hinglish.

If English words clearly dominate (en_word_hits >= 2 and en_word_hits > hi_lexicon_hits) ⇒ en.

If there is one Hindi marker in a very short sentence (hi_lexicon_hits == 1 and n_tokens <= 4) ⇒ hinglish.

If both Hindi and English hits are present ⇒ mixed.

If no lexicon hits but normal length (n_tokens >= 2) ⇒ fallback to en; otherwise unknown.
​

Examples:

"mujhe cramps nahi hai" ⇒ many Hindi markers (mujhe, nahi, hai) ⇒ hinglish.

"Cramps today. Energy low." ⇒ English words only ⇒ en.

"yaar today was too much" ⇒ Hindi yaar + English today/was ⇒ mixed.
​

🧮 Confidence score
Confidence is deterministic and interpretable:

purity = max(latin_ratio, devanagari_ratio)

lex_frac = (hi_lexicon_hits + en_word_hits) / n_tokens (if n_tokens > 0)

Combined roughly as:

c
o
n
f
=
0.3
+
0.4
⋅
p
u
r
i
t
y
+
0.3
⋅
l
e
x
_
f
r
a
c
conf=0.3+0.4⋅purity+0.3⋅lex_frac
Slight downward adjustment for mixed labels (more ambiguity).

Clamped to [0, 1].

Intuition:

High confidence for clean, pure‑script texts with many recognized words.

Lower confidence for short, noisy, or heavily mixed texts.

🚀 Getting started
1. Install dependencies
The project uses only the Python standard library. Just ensure Python 3.8+ is installed.

2. Clone and enter
bash
git clone <your-repo-url>.git
cd ashwam_lang_detect
3. Prepare input file
Create texts.jsonl (if not already present) using the synthetic dataset from the exercise:
​

text
{"id":"t_001","text":"Cramps today. Energy low."}
{"id":"t_002","text":"Aaj headache hai, mood off hai yaar."}
...
{"id":"t_029","text":"Work was stressful today. Kal appointment hai at the clinic, hoping things get better."}
Each record must be on a single line of valid JSON.
​

4. Run the detector
bash
python -m lang_detect.cli --in texts.jsonl --out lang.jsonl
Output: lang.jsonl with one JSON object per input row, containing labels, confidence, and evidence.

5. Inspect results
bash
# Linux/macOS
head lang.jsonl

# Windows PowerShell
Get-Content .\lang.jsonl | Select-Object -First 5
🔍 Example outputs
English

Input:

json
{"id":"t_001","text":"Cramps today. Energy low."}
Output (abridged):

json
{
  "id": "t_001",
  "primary_language": "en",
  "script": "latin",
  "confidence": 0.8,
  "evidence": {
    "latin_ratio": 1.0,
    "devanagari_ratio": 0.0,
    "hi_lexicon_hits": 0,
    "en_word_hits": 3,
    "n_tokens": 4
  }
}
Mixed script & language

Input:

json
{"id":"t_008","text":"आज meeting thi but mood खराब था"}
Output (abridged):

json
{
  "id": "t_008",
  "primary_language": "mixed",
  "script": "mixed",
  "confidence": 0.6,
  "evidence": {
    "latin_ratio": 0.4,
    "devanagari_ratio": 0.6,
    "hi_lexicon_hits": 1,
    "en_word_hits": 1,
    "n_tokens": 6
  }
}
Unknown

Input:

json
{"id":"t_021","text":"12345 !!!"}
Output (abridged):

json
{
  "id": "t_021",
  "primary_language": "unknown",
  "script": "other",
  "confidence": 0.2,
  "evidence": {
    "latin_ratio": 0.0,
    "devanagari_ratio": 0.0,
    "hi_lexicon_hits": 0,
    "en_word_hits": 0,
    "n_tokens": 0
  }
}
✅ Tests
The repo includes unit tests for the behaviors the exercise cares about:
​

Correct Devanagari vs Latin handling

Correct Hinglish detection (Hindi words in Latin)

Correct mixed handling for mixed scripts / code‑switching

unknown handling for extremely short/noisy strings

Run:

bash
pytest -q
Example test snippets:

python
from lang_detect.core import detect_for_text

def test_devanagari_hi():
    res = detect_for_text("t_003", "आज बहुत थकान है 😩")
    assert res["script"] == "devanagari"
    assert res["primary_language"] == "hi"

def test_hinglish():
    res = detect_for_text("t_002", "Aaj headache hai, mood off hai yaar.")
    assert res["script"] == "latin"
    assert res["primary_language"] in ("hinglish", "mixed")

def test_mixed_script():
    res = detect_for_text("t_008", "आज meeting thi but mood खराब था")
    assert res["script"] == "mixed"
    assert res["primary_language"] == "mixed"

def test_unknown_short():
    res = detect_for_text("t_021", "12345 !!!")
    assert res["primary_language"] == "unknown"
You can also create a golden file of expected labels for t_001–t_029 and assert that primary_language and script remain stable over time.
​

⚖️ Design tradeoffs
Key tradeoffs made:

Deterministic > ML
Favor clear rules and explainable evidence over a trained model for this small, synthetic dataset.
​

Transparent evidence
Every decision exposes its raw signals (ratios, counts) to avoid black‑box behavior.
​

Conservative use of unknown
Extremely short or numeric‑only snippets are labeled unknown instead of forcing a guess.
​

Domain‑focused lexicons
Small, hand‑picked lexicons tuned to the journaling dataset rather than exhaustive vocabularies.
​

🧭 Limitations & future work
Known limitations

Lexicons are small; some rare slang or spelling variants might be missed.

Borderline cases between hinglish and mixed are sometimes subjective.

Only Hindi/English are modeled; other languages/scripts are lumped into other + unknown.
​

Potential improvements

Expand and tune lexicons based on a larger (real) dataset.

Add character n‑grams to improve Hinglish vs English separation.

Train a tiny classifier on top of the evidence features while keeping them visible.

Extend to more Indian languages and scripts in the same framework.
​

