"""RAVDESS dosya adlarından klip indeksi çıkarır ve results/index.csv olarak kaydeder.

Dosya adı: MM-VV-EE-II-SS-RR-AA.mp4
    MM modality, VV vocal channel, EE emotion, II intensity,
    SS statement, RR repetition, AA actor (tek = erkek, çift = kadın)

Çalıştırma (proje kökünden):
    python src/build_index.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_PATH = ROOT / "results" / "index.csv"

EMOTIONS_8 = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised",
}

# Calm, neutral ile birleştiriliyor (8 → 7 sınıf).
MERGE = {"calm": "neutral"}

# Etiket sırası sabit: label sütunu bu listedeki indekstir.
CLASSES = ["neutral", "happy", "sad", "angry", "fearful", "disgust", "surprised"]

INTENSITY = {"01": "normal", "02": "strong"}


def parse_name(path: Path) -> dict:
    modality, channel, emo, intensity, statement, repetition, actor = path.stem.split("-")
    emotion8 = EMOTIONS_8[emo]
    emotion = MERGE.get(emotion8, emotion8)
    actor_id = int(actor)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "actor": actor_id,
        "gender": "M" if actor_id % 2 == 1 else "F",
        "emotion8": emotion8,
        "emotion": emotion,
        "label": CLASSES.index(emotion),
        "intensity": INTENSITY[intensity],
        "statement": int(statement),
        "repetition": int(repetition),
        "modality": modality,
        "channel": channel,
    }


def check(df: pd.DataFrame) -> None:
    assert len(df) == 1440, f"toplam klip {len(df)}, beklenen 1440"
    assert (df["modality"] == "02").all(), "video-only olmayan dosya var"
    assert (df["channel"] == "01").all(), "speech olmayan dosya var"
    assert df["actor"].nunique() == 24
    assert (df.groupby("actor").size() == 60).all(), "her aktörde 60 klip olmalı"
    assert (df.groupby("gender")["actor"].nunique() == 12).all(), "12E + 12K olmalı"

    counts = df["emotion"].value_counts()
    assert counts["neutral"] == 288, f"neutral {counts['neutral']}, beklenen 288"
    for c in CLASSES[1:]:
        assert counts[c] == 192, f"{c} {counts[c]}, beklenen 192"

    # Neutral'da strong yoğunluk yok.
    assert not ((df["emotion8"] == "neutral") & (df["intensity"] == "strong")).any()
    assert df["path"].is_unique


def main() -> None:
    paths = sorted(RAW_DIR.glob("Actor_*/*.mp4"))
    df = pd.DataFrame([parse_name(p) for p in paths])
    check(df)

    df = df.drop(columns=["modality", "channel"])
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"{len(df)} klip -> {OUT_PATH.relative_to(ROOT)}")
    print("\n8 sınıf (birleştirmeden önce):")
    print(df["emotion8"].value_counts().reindex(EMOTIONS_8.values()).to_string())
    print("\n7 sınıf (birleştirmeden sonra):")
    print(df["emotion"].value_counts().reindex(CLASSES).to_string())


if __name__ == "__main__":
    main()
