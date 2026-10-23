"""Aktör bazlı, cinsiyet dengeli 6 fold tanımlar ve results/splits.json olarak kaydeder.

Her fold 4 aktör (2E + 2K). CV fold k için:
    test  = fold k
    val   = fold (k + 1) % 6
    train = kalan 4 fold (16 aktör)
Sabit bölme (geliştirme sırasında kullanılan) CV fold 0 ile aynıdır.

Çalıştırma (proje kökünden):
    python src/splits.py
"""

import json
import random
from pathlib import Path

import pandas as pd

from utils import SEED

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "results" / "index.csv"
SPLITS_PATH = ROOT / "results" / "splits.json"

N_FOLDS = 6
FIXED_FOLD = 0


def make_folds(seed: int = SEED) -> list[list[int]]:
    rng = random.Random(seed)
    males = [a for a in range(1, 25) if a % 2 == 1]
    females = [a for a in range(1, 25) if a % 2 == 0]
    rng.shuffle(males)
    rng.shuffle(females)
    per = len(males) // N_FOLDS
    return [
        sorted(males[k * per:(k + 1) * per] + females[k * per:(k + 1) * per])
        for k in range(N_FOLDS)
    ]


def cv_split(folds: list[list[int]], k: int) -> dict[str, list[int]]:
    test = folds[k]
    val = folds[(k + 1) % N_FOLDS]
    train = sorted(a for i, f in enumerate(folds) if i not in (k, (k + 1) % N_FOLDS) for a in f)
    return {"train": train, "val": val, "test": test}


def load_split(fold: int = FIXED_FOLD, allow_test: bool = False) -> dict[str, pd.DataFrame]:
    """İndeksi train/val(/test) olarak böler.

    Test aktörleri model geliştirme bitene kadar kilitli: allow_test=True verilmedikçe
    test kümesi döndürülmez.
    """
    split = json.loads(SPLITS_PATH.read_text())["cv"][fold]
    df = pd.read_csv(INDEX_PATH)
    parts = ["train", "val"] + (["test"] if allow_test else [])
    return {p: df[df["actor"].isin(split[p])].reset_index(drop=True) for p in parts}


def check(folds: list[list[int]], cv: list[dict], df: pd.DataFrame) -> None:
    all_actors = sorted(a for f in folds for a in f)
    assert all_actors == list(range(1, 25)), "her aktör tam bir fold'da olmalı"
    for f in folds:
        assert sum(a % 2 for a in f) == 2, f"fold {f} 2E + 2K değil"
    for s in cv:
        assert len(s["train"]) == 16 and len(s["val"]) == 4 and len(s["test"]) == 4
        assert not set(s["train"]) & set(s["val"]), "train ve val çakışıyor"
        assert not set(s["train"]) & set(s["test"]), "train ve test çakışıyor"
        assert not set(s["val"]) & set(s["test"]), "val ve test çakışıyor"
    # Her CV turunda her fold bir kez test olur.
    assert sorted(a for s in cv for a in s["test"]) == list(range(1, 25))

    # Her aktörde bütün duygular eşit sayıda olduğu için fold'lar sınıf olarak da dengeli.
    for f in folds:
        counts = df[df["actor"].isin(f)]["emotion"].value_counts()
        assert counts["neutral"] == 48 and (counts.drop("neutral") == 32).all()


def main() -> None:
    df = pd.read_csv(INDEX_PATH)
    folds = make_folds()
    cv = [cv_split(folds, k) for k in range(N_FOLDS)]
    check(folds, cv, df)

    out = {
        "seed": SEED,
        "folds": folds,
        "fixed_fold": FIXED_FOLD,
        "fixed": cv[FIXED_FOLD],
        "cv": cv,
    }
    SPLITS_PATH.write_text(json.dumps(out, indent=2))

    print(f"seed = {SEED} -> {SPLITS_PATH.relative_to(ROOT)}\n")
    for k, f in enumerate(folds):
        genders = "".join("E" if a % 2 else "K" for a in f)
        print(f"fold {k}: aktörler {f} ({genders})")
    fixed = cv[FIXED_FOLD]
    print(f"\nSabit bölme (CV fold {FIXED_FOLD}):")
    for part in ("train", "val", "test"):
        n = df["actor"].isin(fixed[part]).sum()
        print(f"  {part:5s}: {len(fixed[part]):2d} aktör, {n:4d} klip  {fixed[part]}")


if __name__ == "__main__":
    main()
