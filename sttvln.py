import os
import sys
import re
import html
import requests
import subprocess
import torch
from faster_whisper import WhisperModel

def process_video(slug):
    base_url = "https://videolectures.net/videos/"
    page_url = f"{base_url}{slug}"
    print(f"[INFO] Fetching page: {page_url}")

    # --- Step 1: Fetch page and extract MP4 link ---
    response = requests.get(page_url)
    if response.status_code != 200:
        raise Exception(f"Failed to open {page_url} (status {response.status_code})")

    match = re.search(r'https://[^\s"]+\.mp4\?[^"\s]+', response.text)
    if match:
        mp4_url = html.unescape(match.group(0))
    else:
        raise Exception("MP4 link not found on the page.")

    print(f"[INFO] Found MP4 URL: {mp4_url[:80]}...")

    # --- Step 2: Download MP4 ---
    mp4_filename = f"{slug}.mp4"
    print(f"[INFO] Downloading video -> {mp4_filename}")
    with requests.get(mp4_url, stream=True) as r:
        r.raise_for_status()
        with open(mp4_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"[INFO] Download complete: {mp4_filename}")

    # --- Step 3: Extract audio with ffmpeg ---
    wav_filename = f"{slug}.wav"
    ffmpeg_cmd = [
        "ffmpeg", "-i", mp4_filename,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "44100", "-ac", "2", wav_filename, "-y"
    ]
    print(f"[INFO] Extracting audio -> {wav_filename}")
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"[INFO] Audio extraction complete")

    # --- Step 4: (Optional) Delete MP4 ---
    # os.remove(mp4_filename)

    # --- Step 5: Run Whisper directly in Python ---
    print("[INFO] Running Whisper transcription via faster-whisper...")

    # Detect device automatically
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Using device: {device}")

    model_size = "medium"  # choose small, medium, or large
    model = WhisperModel(model_size, device=device)

    segments, info = model.transcribe(wav_filename, language="en")

    srt_filename = f"{slug}.srt"
    with open(srt_filename, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, start=1):
            start = segment.start
            end = segment.end
            text = segment.text.strip()

            def format_time(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                s = int(seconds % 60)
                ms = int((seconds - int(seconds)) * 1000)
                return f"{h:02}:{m:02}:{s:02},{ms:03}"

            srt_file.write(f"{i}\n")
            srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
            srt_file.write(f"{text}\n\n")

    print(f"[INFO] Whisper transcription complete -> {srt_filename}")

    # --- Step 6: (Optional) Delete WAV ---
    # os.remove(wav_filename)

    print(f"[DONE] All steps completed successfully for slug: {slug}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sttvln.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    process_video(slug)
