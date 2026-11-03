# Data

This project uses the **video-only speech** part of RAVDESS
(Zenodo record [1188976](https://doi.org/10.5281/zenodo.1188976), CC BY-NC-SA 4.0).
The videos are not part of this repository and have to be downloaded separately.

## 1. Download

Download the 24 files `Video_Speech_Actor_01.zip` … `Video_Speech_Actor_24.zip` (≈ 13.4 GB in total) into
`data/raw/zips/`. From the repository root:

```bash
mkdir -p data/raw/zips
for i in $(seq -w 1 24); do
  curl -L -C - -o data/raw/zips/Video_Speech_Actor_$i.zip \
    "https://zenodo.org/api/records/1188976/files/Video_Speech_Actor_$i.zip/content"
done
```

`-C -` resumes an interrupted download, so the loop can simply be run again.

## 2. Verify

The Zenodo record lists an MD5 checksum for every file. Compare them with:

```bash
md5 -r data/raw/zips/*.zip      # macOS
md5sum data/raw/zips/*.zip      # Linux
```

## 3. Extract the video-only files

Every zip contains both the audio-visual (`01-*`) and the video-only (`02-*`) version of each clip. They contain
the same frames, so only `02-*` is extracted:

```bash
for z in data/raw/zips/*.zip; do unzip -n -q "$z" "*/02-*" -d data/raw/; done
ls data/raw/Actor_*/*.mp4 | wc -l   # expected: 1440
```

After this step the zips are no longer needed.

## Layout

```
data/
├── raw/
│   ├── zips/                    downloaded archives
│   └── Actor_01 … Actor_24/     60 video-only clips per actor (02-*.mp4)
├── processed/                   face crops (created by preprocessing)
└── metadata/                    tracked in git
    ├── index.csv                one row per clip: path, actor, gender, emotion, label, intensity, …
    ├── splits.json              seed, six actor folds, fixed split, cross-validation rounds
    └── video_meta.csv           resolution, frame rate, frame count and duration of every clip
```

The metadata files are created by `src/build_index.py`, `src/splits.py` and `src/eda.py`
(see the main [README](../README.md)).

## RAVDESS file names

`02-01-06-01-02-01-12.mp4` = modality (02 video-only) - vocal channel (01 speech) - emotion (06 fearful) -
intensity (01 normal) - statement (02) - repetition (01) - actor (12; odd = male, even = female).

| Code | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 |
|---|---|---|---|---|---|---|---|---|
| Emotion | neutral | calm | happy | sad | angry | fearful | disgust | surprised |

In this project calm is merged into neutral, which gives seven classes.
