# VLN speech-to-text and concepts extraction

*Testing automatic extraction of concepts from VLN videos.*

Videolectures.NET has videos accesible via slugs. We want to automatically perform speech-to-text for a given video and extract the concepts that lecture is presenting.

So for instance, in URL:

`https://videolectures.net/videos/rtk2017_kovacic_mobilni_telefoni` 

slug is `rtk2017_kovacic_mobilni_telefoni`.

## Prerequisites

```
sudo apt update && sudo apt install ffmpeg
pip install requests beautifulsoup4
pip install faster-whisper
```

You also need Torch, check if it is installed:

```
python3 -c "import torch; print(torch.__version__)"
```

For instance, answer `2.9.0+cu128` means that you have CUDA 12.8 support installed.

## Python script to extract audio and perform TTS

The Python script [sttvln.py](sttvln.py) does the following:
- input parameter is a slug;
- script opens VLN website and detects the location and parameters of MP4 video;
- video is downloaded;
- audio part is extracted in WAV file;
- `faster-whisper` (with automatic detection of GPU/CPU) is used to perform speech-to-text;
- the result is a .SRT (subtitles) file.

This file can be then sent to Wikifier web service, which will automatically extract concepts in a lecture.

Since Wikifier has a limitation of input (10.000 characters), you can use [split_srt.py](split_srt.py) script to convert .SRT subtitle file into ~9500-character parts in pure text, that can be uploaded to Wikifier service.
