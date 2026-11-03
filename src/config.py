"""Projenin bütün dosya yolları ve seed'i tek yerde.

Bir dosyanın yeri değişirse sadece burası güncellenir.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Projenin tek seed'i. Aktör bölmesi, eğitim ve augmentation hepsi bunu kullanır.
SEED = 4206

# Veri
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"              # RAVDESS videoları (git'te değil)
PROCESSED_DIR = DATA_DIR / "processed"  # yüz kırpmaları (git'te değil)
METADATA_DIR = DATA_DIR / "metadata"    # indeks, bölme, video bilgisi (git'te)

INDEX_PATH = METADATA_DIR / "index.csv"
SPLITS_PATH = METADATA_DIR / "splits.json"
META_PATH = METADATA_DIR / "video_meta.csv"

# Çıktılar
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"
TABLE_DIR = RESULTS_DIR / "tables"
MODELS_DIR = ROOT / "models"
