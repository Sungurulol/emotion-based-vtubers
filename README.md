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
├── notebooks/           exploratory notebooks
├── models/              checkpoints (not tracked)
└── avatar/
    ├── README.md        what the files are, plan for rig and expressions
    ├── vtuber_avatar.blend   low-poly model (Blender 5.2), T-pose
    └── previews/        front and side renders
```

## Demo avatar

<img src="avatar/previews/front.png" alt="Front view of the low-poly avatar in T-pose" width="220" align="right">

The live demo needs a 3D model whose expression can be switched by the classifier. The model is built from scratch
in Blender and will be exported as **VRM**, the common format of 3D VTuber software. VTube Studio, mentioned in the
proposal, supports only 2D (Live2D) models, so the avatar will be shown in a small web viewer based on
[`three-vrm`](https://github.com/pixiv/three-vrm) instead. Each of the seven predicted classes triggers one avatar
expression. See [avatar/README.md](avatar/README.md).

<br clear="right">

## Setup

Requirements: Python 3.13 and ffmpeg (`ffprobe` is used to read video properties; on macOS
`brew install ffmpeg`). Developed on macOS with an Apple M5 GPU (PyTorch MPS backend); without MPS the code falls
back to CUDA or the CPU.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data

The project uses the **Ryerson Audio-Visual Database of Emotional Speech and Song (RAVDESS)**, Zenodo record
[1188976](https://doi.org/10.5281/zenodo.1188976). Only the **video-only speech** clips are used; the audio, the
song recordings and the audio-visual copies of the same clips are left out.

| | |
|---|---|
| Actors | 24 professional actors, 12 male and 12 female |
| Content | Two fixed sentences ("Kids are talking by the door", "Dogs are sitting by the door"), spoken with different emotions at normal and strong intensity (neutral only at normal) |
| Clips | 1,440 (60 per actor) |
| Video | 1280×720, 29.97 fps, 2.9–5.3 s per clip (88–158 frames) |
| Emotions | 8 in the dataset; calm is merged into neutral because the two are very similar, giving 7 classes |
| Class sizes | neutral 288, every other class 192 |

The videos are not part of this repository. Download and extract them as described in
[data/README.md](data/README.md).

## Dataset and licence

RAVDESS is released under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) and is used here
for non-commercial academic work only. The videos are not redistributed.

> S. R. Livingstone and F. A. Russo, "The Ryerson Audio-Visual Database of Emotional Speech and Song (RAVDESS):
> A dynamic, multimodal set of facial and vocal expressions in North American English," *PLoS ONE*, vol. 13,
> no. 5, e0196391, 2018.

The code in this repository is released under the [MIT License](LICENSE).

## Author

Ömer Sunguralp Bektaş, Artificial Intelligence and Data Engineering, Atatürk University
