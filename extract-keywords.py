#!/usr/bin/env python3
"""
Extract keywords from all .txt files in a given directory using a local LLM (Ollama),
and save results into a structured JSON file + raw model output log.

Keywords are extracted as plain text (comma-separated), not JSON.

Usage:
    python extract_keywords_json.py /path/to/text/files
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# === Configuration ===
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"  # You can switch to 'llama3', 'phi3', etc.


# === Core Function ===
def extract_keywords(text: str, model: str = MODEL, log_file: Path = None, file_name: str = ""):
    """
    Sends text to Ollama model and extracts raw comma-separated keywords (no JSON parsing).
    Logs raw responses for debugging.
    """
    prompt = (
        "Extract the 3-10 most relevant keywords from the following text. "
        "Return ONLY a comma-separated list of keywords. "
        "Skip stop words, numbers and general words. "
        "Preferred keywords are Wikipedia concepts. "
        "If text is not in English, return keywords in English. "
        "Do not use numbered lists, explanations, or JSON.\n\n"
        f"Text:\n{text}"
    )

    payload = {"model": model, "prompt": prompt}
    raw_response = ""

    try:
        # Handle streamed responses from Ollama (JSONL)
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=180) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    event = json.loads(line.decode("utf-8"))
                    raw_response += event.get("response", "")
                except json.JSONDecodeError:
                    continue

        raw = raw_response.strip()

        # Log the raw model output
        if log_file:
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"\n--- {file_name} ---\n{raw}\n")

        # Clean keywords
        # Split by comma, semicolon, or newline — filter empties
        parts = [p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()]
        return parts

    except Exception as e:
        # Log even on failure
        if log_file:
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"\n--- {file_name} (ERROR) ---\n{str(e)}\n")
        print(f"[ERROR] Failed to extract keywords for {file_name}: {e}")
        return []


# === Directory Processing ===
def process_directory(directory: str):
    """
    Processes all .txt files in sorted order and saves structured JSON + raw log.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        print(f"[ERROR] Directory not found: {directory}")
        sys.exit(1)

    txt_files = sorted([f for f in dir_path.iterdir() if f.suffix == ".txt"])
    if not txt_files:
        print(f"[INFO] No .txt files found in {directory}")
        sys.exit(0)

    # Prepare output files
    results = {dir_path.name: {}}
    log_file = dir_path / f"ollama_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    output_path = dir_path / "keywords.json"

    print(f"Processing directory: {dir_path.name}")
    print(f"Logging raw model responses to: {log_file}")

    for file in txt_files:
        print(f"\nProcessing: {file.name}")
        text = file.read_text(encoding="utf-8")

        keywords = extract_keywords(text, model=MODEL, log_file=log_file, file_name=file.name)
        key = file.stem
        results[dir_path.name][key] = keywords

        print(f"{key}: {keywords}")

    # Save structured JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nKeywords JSON saved to: {output_path}")
    print(f"Raw responses logged in: {log_file}")


# === Entry Point ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_keywords_json.py /path/to/text/files")
        sys.exit(1)

    input_dir = sys.argv[1]
    process_directory(input_dir)
