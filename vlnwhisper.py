#!/usr/bin/env python3
import os
import re
import sys
import json
import requests
import subprocess
from pathlib import Path
from tqdm import tqdm
from faster_whisper import WhisperModel

# ---------------- CONFIG SECTION ----------------
SLICE_PADDING = 1000        # milliseconds before/after slide
DELETE_MP4 = True           # delete MP4 after extraction
DELETE_WAV = True           # delete WAV after slicing
WHISPER_MODEL = "small"     # faster-whisper model
OUTPUT_DIR = None           # default: slug name
# ------------------------------------------------

# ---------------- Parse Arguments ----------------
if len(sys.argv) < 2:
    print("Usage: python3 vlnwhisper.py <slug> [language]")
    sys.exit(1)

slug = sys.argv[1]
language = sys.argv[2] if len(sys.argv) > 2 else None

output_dir = Path(OUTPUT_DIR or slug)
output_dir.mkdir(exist_ok=True)

# ---------------- Detect CPU/GPU ----------------
try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    device = "cpu"
print(f"No GPU detected, using CPU" if device=="cpu" else f"GPU detected, using CUDA")

# ---------------- Download Video ----------------
video_page_url = f"https://videolectures.net/videos/{slug}"
print(f"Opening video page: {video_page_url}")

json_url = f"https://backend.videolectures.net/api/v2/videos/slug/{slug}"
print(f"Fetching metadata: {json_url}")
resp = requests.get(json_url)
resp.raise_for_status()
metadata = resp.json()

# Get first part's video URL
parts = metadata.get("parts", [])
if not parts:
    raise ValueError("No video parts found in metadata!")

video_url = parts[0].get("video_url")
if not video_url:
    raise ValueError("Video URL not found!")

video_path = output_dir / f"{slug}.mp4"
print(f"Downloading video to {video_path} ...")
with requests.get(video_url, stream=True) as r:
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    with open(video_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc="Downloading") as pbar:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))

# ---------------- Extract Audio ----------------
audio_path = output_dir / f"{slug}.wav"
print("Extracting audio with ffmpeg ...")

# Get video duration for progress bar
import math
def ffmpeg_with_progress(input_file, output_file, extra_args=None):
    cmd = ["ffmpeg", "-y", "-i", str(input_file)]
    if extra_args:
        cmd += extra_args
    cmd += [str(output_file)]
    # Use PIPE to suppress ffmpeg console output
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ffmpeg_with_progress(video_path, audio_path, ["-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2"])

if DELETE_MP4:
    os.remove(video_path)

# ---------------- Prepare Slides ----------------
slides = []
presentations = parts[0].get("presentations", [])
if presentations:
    for pres in presentations:
        for slide in pres.get("slides", []):
            if slide.get("timestamps"):
                slides.append({
                    "title": slide.get("title", ""),
                    "start": slide["timestamps"][0],
                    "image": slide.get("image", "")
                })

if slides:
    # Sort slides by start time
    slides.sort(key=lambda x: x["start"])
    # Add start/end padding
    duration = parts[0]["duration"]
    for i in range(len(slides)):
        start = max(0, slides[i]["start"] - SLICE_PADDING/1000)
        if i < len(slides) - 1:
            end = slides[i + 1]["start"] + SLICE_PADDING/1000
        else:
            end = duration
        slides[i]["start_pad"] = start
        slides[i]["end_pad"] = min(end, duration)
else:
    print("No slides with timestamps found. Using entire audio as single slice.")
    slides = [{"title": slug, "start_pad": 0, "end_pad": parts[0]["duration"]}]

# ---------------- Load Whisper Model ----------------
model_name = WHISPER_MODEL
if language == "en":
    model_name += ".en"

print(f"Loading faster-whisper model '{model_name}' on {device} ...")
model = WhisperModel(model_name, device=device, compute_type="auto")

# ---------------- Transcribe Slides ----------------
def safe_filename(name: str) -> str:
    # Replace invalid characters with underscores
    return re.sub(r'[^a-zA-Z0-9_\-]+', '_', name.strip())

for idx, slide in enumerate(tqdm(slides, desc="Slides", unit="slide")):
    safe_title = safe_filename(slide["title"])
    s_path = output_dir / f"{idx+1:03d}_{safe_title}.wav"
    txt_path = output_dir / f"{idx+1:03d}_{safe_title}.txt"

    # Slice audio
    start_sec = slide["start_pad"]
    end_sec = slide["end_pad"]
    ffmpeg_slice_cmd = [
        "ffmpeg", "-y", "-i", str(audio_path),
        "-ss", str(start_sec), "-to", str(end_sec),
        str(s_path)
    ]
    try:
        subprocess.run(ffmpeg_slice_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"FFmpeg failed for slide {idx+1}: {slide['title']}")
        continue

    # Transcribe with per-slide progress
    print(f"\nTranscribing slide {idx+1}/{len(slides)}: {slide['title']}")
    segments, _ = model.transcribe(str(s_path), language=language)
    with open(txt_path, "w", encoding="utf-8") as f:
        for segment in tqdm(segments, desc="Writing segments", leave=False):
            f.write(segment.text.strip() + "\n")

    if DELETE_WAV:
        os.remove(s_path)

if DELETE_WAV:
    os.remove(audio_path)

print(f"\nPipeline complete! All files saved in: {output_dir}")
