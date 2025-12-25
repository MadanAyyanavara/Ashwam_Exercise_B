# lang_detect/cli.py

import argparse
import json
from .core import detect_for_text


def main():
    parser = argparse.ArgumentParser(description="Ashwam language detector")
    parser.add_argument(
        "--in", dest="input_path", required=True, help="Input JSONL file (texts.jsonl)"
    )
    parser.add_argument(
        "--out", dest="output_path", required=True, help="Output JSONL file"
    )
    args = parser.parse_args()

    with open(args.input_path, "r", encoding="utf-8") as fin, \
         open(args.output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            res = detect_for_text(obj["id"], obj["text"])
            fout.write(json.dumps(res, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
