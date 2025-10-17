# VLN speech-to-text and concepts extraction

*Testing automatic extraction of concepts from VLN videos.*

Videolectures.NET has videos accesible via slugs. We want to automatically perform speech-to-text for a given video and extract the concepts that lecture is presenting. And we want to do that *per slides*.

So for instance, in URL `https://videolectures.net/videos/lawandethics2017_kovacic_kosmerlj_anonymisation`, slug is `lawandethics2017_kovacic_kosmerlj_anonymisation`.

## Prerequisites

Assuming you have Ubuntu/Debian OS.

```
sudo apt update && sudo apt install ffmpeg
pip install requests pydub faster-whisper tqdm torch
```

## Python script to extract audio and perform TTS for each slide

The Python script [vlnwhisper.py](vlnwhisper.py) does the following:
- input parameter is a slug and optionally a language (only `en` is supported, because you can use model for all languages or English-optimized model);
- script opens VLN website and detects the location and S3 parameters of MP4 video;
- video is downloaded;
- audio part is extracted
- script downloads JSON file with timing of the slides (if they are no timings present, it assumes there is just one "slide");
- audio is sliced to slides (+1 second at the beginning and the end by default - see config section)
- `faster-whisper` (with automatic detection of GPU/CPU) is used to perform speech-to-text for each slide;
- the result is a series of .TXT file with transcriptions for each slide separately.

This files can be then sent to Wikifier web service, which will automatically extract concepts mentioned in each slide of a lecture with a given slug.

### Config

There is a small config section in the Python script:
```
# ---------------- CONFIG SECTION ----------------
SLICE_PADDING = 1000        # milliseconds before/after slide
DELETE_MP4 = True           # delete MP4 after extraction
DELETE_WAV = True           # delete WAV after slicing
WHISPER_MODEL = "small"     # faster-whisper model
OUTPUT_DIR = None           # default: slug name
# ------------------------------------------------
```
`WHISPER_MODEL` parameter can have the following values:
- `tiny`: Very fast, low accuracy
- `tiny.en`: English-only version of tiny
- `base`: Slightly better accuracy, still fast
- `base.en`: English-only version of base
- `small`: Good accuracy, moderate speed
- `small.en`: English-only version of small
- `medium`: High accuracy, slower
- `medium.en`: English-only version of medium
- `large-v1`: Highest accuracy, very slow
- `large-v2`: Whisper v2 model, very accurate, very slow

## Running the script

How to run: `python3 vlnwhisper.py lawandethics2017_kovacic_kosmerlj_anonymisation en`:

```
No GPU detected, using CPU
Opening video page: https://videolectures.net/videos/lawandethics2017_kovacic_kosmerlj_anonymisation
Fetching metadata: https://backend.videolectures.net/api/v2/videos/slug/lawandethics2017_kovacic_kosmerlj_anonymisation
Downloading video to lawandethics2017_kovacic_kosmerlj_anonymisation/lawandethics2017_kovacic_kosmerlj_anonymisation.mp4 ...
Downloading: 100%|███████████████████████████████████████████████████████████████████████████████████| 171M/171M [00:00<00:00, 321MB/s]
Extracting audio with ffmpeg ...
Loading faster-whisper model 'small.en' on cpu ...
Slides:   0%|                                                                                                | 0/20 [00:00<?, ?slide/s]
Transcribing slide 1/20: Tacita Court decisions anonymizer
Slides:   5%|████▍                                                                                   | 1/20 [00:03<01:07,  3.56s/slide]
Transcribing slide 2/20: Court decision anonymisation
Slides:  10%|████████▊                                                                               | 2/20 [00:10<01:42,  5.68s/slide]
Transcribing slide 3/20: Data            
Slides:  15%|█████████████▏                                                                          | 3/20 [00:22<02:24,  8.51s/slide]
Transcribing slide 4/20: Approach        
Slides:  20%|█████████████████▌                                                                      | 4/20 [00:28<01:57,  7.36s/slide]
Transcribing slide 5/20: Approach - classification
Slides:  25%|██████████████████████                                                                  | 5/20 [00:34<01:46,  7.13s/slide]
Transcribing slide 6/20: Features - basic
Slides:  30%|██████████████████████████▍                                                             | 6/20 [00:53<02:36, 11.16s/slide]
Transcribing slide 7/20: Features – context - 2
Slides:  35%|██████████████████████████████▊                                                         | 7/20 [00:55<01:45,  8.09s/slide]
Transcribing slide 8/20: Features – context
Slides:  40%|███████████████████████████████████▏                                                    | 8/20 [00:59<01:20,  6.69s/slide]
Transcribing slide 9/20: Features – context - 3
Slides:  45%|███████████████████████████████████████▌                                                | 9/20 [01:03<01:05,  5.97s/slide]
Transcribing slide 10/20: Features – features of neighbours
Slides:  50%|███████████████████████████████████████████▌                                           | 10/20 [01:06<00:48,  4.86s/slide]
Transcribing slide 11/20: Rate of success
Slides:  55%|███████████████████████████████████████████████▊                                       | 11/20 [01:14<00:54,  6.03s/slide]
Transcribing slide 12/20: Examples       
Slides:  60%|████████████████████████████████████████████████████▏                                  | 12/20 [01:21<00:48,  6.12s/slide]
Transcribing slide 13/20: Examples – successfull anonymisation
Slides:  65%|████████████████████████████████████████████████████████▌                              | 13/20 [01:24<00:37,  5.30s/slide]
Transcribing slide 14/20: Examples – successfull detection of errors
Slides:  70%|████████████████████████████████████████████████████████████▉                          | 14/20 [01:28<00:28,  4.76s/slide]
Transcribing slide 15/20: Examples – unneccessary anonymisation
Slides:  75%|█████████████████████████████████████████████████████████████████▎                     | 15/20 [01:30<00:19,  3.95s/slide]
Transcribing slide 16/20: Examples – our mistakes during anonymisation
Slides:  80%|█████████████████████████████████████████████████████████████████████▌                 | 16/20 [01:31<00:12,  3.23s/slide]
Transcribing slide 17/20: Performance   
Slides:  85%|█████████████████████████████████████████████████████████████████████████▉             | 17/20 [01:37<00:11,  3.89s/slide]
Transcribing slide 18/20: Functioning of the system
Slides:  90%|██████████████████████████████████████████████████████████████████████████████▎        | 18/20 [01:41<00:08,  4.12s/slide]
Transcribing slide 19/20: User interface
Slides:  95%|██████████████████████████████████████████████████████████████████████████████████▋    | 19/20 [01:52<00:06,  6.23s/slide]
Transcribing slide 20/20: Questions...   
Slides: 100%|███████████████████████████████████████████████████████████████████████████████████████| 20/20 [01:55<00:00,  5.77s/slide]
                                        
Pipeline complete! All files saved in: lawandethics2017_kovacic_kosmerlj_anonymisation
```

Or without slides - `python3 vlnwhisper.py eccs07_noble_psb en`:

```
No GPU detected, using CPU
Opening video page: https://videolectures.net/videos/eccs07_noble_psb
Fetching metadata: https://backend.videolectures.net/api/v2/videos/slug/eccs07_noble_psb
Downloading video to eccs07_noble_psb/eccs07_noble_psb.mp4 ...
Downloading: 100%|███████████████████████████████████████████████████████████████████████████████████| 342M/342M [00:01<00:00, 333MB/s]
Extracting audio with ffmpeg ...
No slides with timestamps found. Using entire audio as single slice.
Loading faster-whisper model 'small.en' on cpu ...
Slides:   0%|                                                                                                 | 0/1 [00:00<?, ?slide/s]
Transcribing slide 1/1: eccs07_noble_psb
Slides: 100%|████████████████████████████████████████████████████████████████████████████████████████| 1/1 [05:44<00:00, 344.76s/slide]
                                          
Pipeline complete! All files saved in: eccs07_noble_psb
```

Example for lecture in slovenian language (without `en` parameter) - `python3 vlnwhisper.py daninfovarnosti2017_kovacic_mobilne_komunikacije`.

## Wikifier concepts

Example for lecture [Anonymisation of judicial decisions with machine learning](https://videolectures.net/videos/lawandethics2017_kovacic_kosmerlj_anonymisation), slide `Features - basic` at `05:29`.

<img width="1157" height="708" alt="image" src="https://github.com/user-attachments/assets/75b4c9cb-8b5a-4dfa-a385-62e8adc8a7fc" />

Example for lecture [Varnost mobilnih komunikacij](https://videolectures.net/videos/daninfovarnosti2017_kovacic_mobilne_komunikacije), slide `CallerID spoofing - 1` at `01:08`. Transcription was done with medium `model`, but it is not very accurate, however concepts are detected quite well.   

<img width="1148" height="545" alt="image" src="https://github.com/user-attachments/assets/a27e0037-447c-40b1-8705-7b99e0bddc01" />
