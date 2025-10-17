#!/usr/bin/env python3
import os
import re
import sys
import argparse


def clean_srt_to_text(srt_content: str) -> str:
    """Remove SRT numbering, timestamps, and excessive blank lines."""
    # Remove timestamps (e.g., 00:00:01,000 --> 00:00:04,000)
    srt_content = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> .*", "", srt_content)
    # Remove subtitle numbering
    srt_content = re.sub(r"^\d+\s*$", "", srt_content, flags=re.MULTILINE)
    # Normalize blank lines
    srt_content = re.sub(r"\n+", "\n", srt_content)
    return srt_content.strip()


def split_text(text: str, max_length: int):
    """Split text into parts without cutting words or sentences."""
    parts = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_length, length)
        if end >= length:
            parts.append(text[start:].strip())
            break

        # Try to break at sentence-ending punctuation
        sentence_break = max(
            text.rfind(".", start, end),
            text.rfind("!", start, end),
            text.rfind("?", start, end)
        )

        if sentence_break != -1 and sentence_break > start + max_length * 0.6:
            split_point = sentence_break + 1
        else:
            # fallback: break at last space
            space_break = text.rfind(" ", start, end)
            split_point = space_break if space_break != -1 else end

        parts.append(text[start:split_point].strip())
        start = split_point + 1

    return parts


def main():
    parser = argparse.ArgumentParser(
        description="Convert an .srt subtitle file into clean text parts."
    )
    parser.add_argument("input_file", help="Path to the input .srt file")
    parser.add_argument(
        "-o", "--output_dir", default="parts",
        help="Directory to save output text parts (default: parts)"
    )
    parser.add_argument(
        "-m", "--max_length", type=int, default=9500,
        help="Maximum characters per text part (default: 9500)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"File not found: {args.input_file}")
        sys.exit(1)

    # Read and clean SRT file
    with open(args.input_file, "r", encoding="utf-8") as f:
        srt_content = f.read()
    clean_text = clean_srt_to_text(srt_content)

    # Split into parts
    parts = split_text(clean_text, args.max_length)

    # Write to files
    os.makedirs(args.output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(args.input_file))[0]

    for i, part in enumerate(parts, start=1):
        out_path = os.path.join(args.output_dir, f"{base_name}_part_{i:02d}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(part)
        print(f"Wrote {out_path} ({len(part)} chars)")

    avg_len = sum(len(p) for p in parts) // len(parts)
    print(f"\nDone: {len(parts)} parts total, average length ≈ {avg_len} chars.")


if __name__ == "__main__":
    main()
