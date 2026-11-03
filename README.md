# Emotion-Driven VTuber Avatars

Facial emotion recognition from video, used to change the expression of a VTuber avatar automatically.
The project compares **frame-based** and **sequence-based** deep learning models on the video-only part of
[RAVDESS](https://doi.org/10.5281/zenodo.1188976), with seven classes: neutral (calm merged in), happy, sad,
angry, fearful, disgust and surprised.

Course project for *Introduction to Deep Learning*, Atatürk University (2026).

| Approach | Models |
|---|---|
| Baseline | Simple CNN trained from scratch |
| Frame-based | ResNet-18, MobileNetV2 (ImageNet-pretrained) |
| Sequence-based | ResNet-18 / MobileNetV2 + LSTM or Transformer |

## Status

| Stage | Status |
|---|---|
| Setup, data index, actor-wise split, dataset analysis | ✅ done |
| Preprocessing (face detection, frame sampling, cropping) | ⏳ in progress |
| Baseline and ResNet-18, progress report | ⏳ in progress |
| Sequence models, experiments, ablation, cross-validation | planned |
| Error analysis, Grad-CAM, webcam → VRM avatar demo | planned |

## Repository structure

```
├── data/
│   ├── README.md        how to download and prepare RAVDESS
│   ├── metadata/        clip index, actor folds, video properties (tracked)
│   ├── raw/             RAVDESS videos (not tracked)
│   └── processed/       face crops (not tracked)
├── src/
│   ├── config.py        all paths and the global seed
│   ├── utils.py         set_seed, DataLoader helpers, device selection
│   ├── build_index.py   clip index from the RAVDESS file names
│   ├── splits.py        gender-balanced actor folds, fixed split, test lock
│   └── eda.py           video properties, dataset summary table, figures
├── results/
│   ├── figures/
│   └── tables/
├── report/
│   ├── proposal/        project proposal (LaTeX + PDF)
│   └── progress/        progress report (LaTeX)
├── docs/notlar.md       working notes: problem log and decisions (Turkish)
├── notebooks/           exploratory notebooks
├── models/              checkpoints (not tracked)
└── avatar/              3D VTuber model (Blender, VRM)
```

## Setup

Requirements: Python 3.13 and ffmpeg (`ffprobe` is used to read video properties).
Developed on macOS with an Apple M5 GPU (PyTorch MPS backend); CPU and CUDA also work.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data

The videos are not part of this repository. Download and extract them as described in
[data/README.md](data/README.md).

## Reproducing the results

Run from the repository root:

```bash
python src/build_index.py   # data/metadata/index.csv
python src/splits.py        # data/metadata/splits.json
python src/eda.py           # data/metadata/video_meta.csv, results/tables/, results/figures/
```

Every script checks the expected counts (1,440 clips, 60 per actor, 288 neutral and 192 clips for every other
class, 2 male + 2 female actors per fold) and stops with an error if one of them does not hold.

To build the progress report:

```bash
cd report/progress && latexmk -pdf progress.tex
```

## Reproducibility

- **Seed:** 4206, defined once in `src/config.py`. `utils.set_seed()` fixes Python, NumPy and PyTorch.
- **Versions:** pinned in `requirements.txt`.
- **Actor-wise split:** six folds of four actors (two male, two female), stored in `data/metadata/splits.json`.
  During development the first round is used as a fixed split:

  | Set | Actors | Clips |
  |---|---|---|
  | Train | the remaining 16 actors | 960 |
  | Validation | 3, 12, 21, 24 | 240 |
  | Test | 4, 6, 7, 23 | 240 |

  The test actors are locked until model development is finished: `splits.load_split()` returns the test set
  only with `allow_test=True`.

## Dataset and licence

RAVDESS is released under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) and is used here
for non-commercial academic work only. The videos are not redistributed.

> S. R. Livingstone and F. A. Russo, "The Ryerson Audio-Visual Database of Emotional Speech and Song (RAVDESS):
> A dynamic, multimodal set of facial and vocal expressions in North American English," *PLoS ONE*, vol. 13,
> no. 5, e0196391, 2018.

The code in this repository is released under the [MIT License](LICENSE).

## Author

Ömer Sunguralp Bektaş, Artificial Intelligence and Data Engineering, Atatürk University
