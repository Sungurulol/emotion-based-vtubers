"""Veri seti analizi: video metadata, özet tablo, sınıf dağılımı grafiği.

Çıktılar:
    results/video_meta.csv               her klip için çözünürlük, fps, kare sayısı, süre
    results/dataset_summary.md / .tex    veri seti özet tablosu
    results/figures/class_distribution.pdf / .png

Çalıştırma (proje kökünden, önce build_index.py ve splits.py):
    python src/eda.py
"""

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from build_index import CLASSES

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG_DIR = RESULTS / "figures"
INDEX_PATH = RESULTS / "index.csv"
SPLITS_PATH = RESULTS / "splits.json"
META_PATH = RESULTS / "video_meta.csv"

# Grafik renkleri (dataviz referans paleti, slot 1 ve 2; renk körlüğü kontrolünden geçti).
COLOR_ORIGINAL = "#2a78d6"
COLOR_MERGED = "#eb6834"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"


# ---------------------------------------------------------------- metadata

def probe(rel_path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,avg_frame_rate,nb_frames,duration,codec_name",
         "-of", "json", str(ROOT / rel_path)],
        capture_output=True, text=True, check=True,
    )
    s = json.loads(out.stdout)["streams"][0]
    return {
        "path": rel_path,
        "codec": s["codec_name"],
        "width": int(s["width"]),
        "height": int(s["height"]),
        "fps": float(Fraction(s["avg_frame_rate"])),
        "n_frames": int(s["nb_frames"]),
        "duration_s": float(s["duration"]),
    }


def load_meta(df: pd.DataFrame) -> pd.DataFrame:
    """ffprobe 1440 klipte ~1 dk sürer; sonucu cache'ler."""
    if META_PATH.exists():
        meta = pd.read_csv(META_PATH)
        if set(meta["path"]) == set(df["path"]):
            return meta
    with ThreadPoolExecutor(max_workers=8) as ex:
        meta = pd.DataFrame(list(ex.map(probe, df["path"])))
    meta.to_csv(META_PATH, index=False)
    return meta


# ---------------------------------------------------------------- özet tablo

def summary_rows(df: pd.DataFrame, meta: pd.DataFrame) -> list[tuple[str, str]]:
    splits = json.loads(SPLITS_PATH.read_text())["fixed"]
    res = meta.groupby(["width", "height"]).size()
    fps = meta["fps"].round(2).unique()
    counts = df["emotion"].value_counts()

    def n_clips(part: str) -> int:
        return int(df["actor"].isin(splits[part]).sum())

    def actors(part: str) -> str:
        return ", ".join(str(a) for a in splits[part])

    # Satırlar iki sütunlu raporda tek sütuna sığacak kadar kısa tutuldu.
    return [
        ("Source", "RAVDESS, Zenodo record 1188976"),
        ("Licence", "CC BY-NC-SA 4.0"),
        ("Subset", "Video-only (modality 02), speech"),
        ("Actors", f"{df['actor'].nunique()} ({(df.drop_duplicates('actor')['gender'] == 'M').sum()} male, "
                   f"{(df.drop_duplicates('actor')['gender'] == 'F').sum()} female)"),
        ("Clips", f"{len(df):,} ({df.groupby('actor').size().iloc[0]} per actor)"),
        ("Resolution", ", ".join(f"{w}×{h}" for (w, h) in res.index) + ", H.264"),
        ("Frame rate", ", ".join(f"{f:.2f} fps" for f in fps)),
        ("Clip length", f"{meta['duration_s'].min():.2f}–{meta['duration_s'].max():.2f} s "
                        f"(median {meta['duration_s'].median():.2f} s)"),
        ("Frames per clip", f"{meta['n_frames'].min()}–{meta['n_frames'].max()} "
                            f"(median {meta['n_frames'].median():.0f})"),
        ("Classes", f"{len(CLASSES)} (calm merged into neutral)"),
        ("Clips per class", f"neutral {counts['neutral']}, others {counts.drop('neutral').iloc[0]} each"),
        ("Training set", f"{len(splits['train'])} actors ({n_clips('train')} clips)"),
        ("Validation set", f"actors {actors('val')} ({n_clips('val')} clips)"),
        ("Test set", f"actors {actors('test')} ({n_clips('test')} clips)"),
    ]


def write_summary(rows: list[tuple[str, str]]) -> None:
    md = ["| Property | Value |", "|---|---|"] + [f"| {k} | {v} |" for k, v in rows]
    (RESULTS / "dataset_summary.md").write_text("\n".join(md) + "\n")

    def tex(s: str) -> str:
        return s.replace("×", r"$\times$").replace("–", "--")

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Summary of the dataset used in this project.}",
        r"\label{tab:dataset}",
        r"\small",
        r"\begin{tabular}{@{}ll@{}}",
        r"\toprule",
        r"Property & Value \\",
        r"\midrule",
        *[f"{tex(k)} & {tex(v)} \\\\" for k, v in rows],
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    (RESULTS / "dataset_summary.tex").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------- grafik

def plot_class_distribution(df: pd.DataFrame) -> None:
    orig = df["emotion8"].value_counts()
    # Her sınıf için kendi orijinal etiketinden gelen klipler; neutral'ın üstüne calm eklenir.
    base = [orig[c] for c in CLASSES]
    merged = [orig["calm"] if c == "neutral" else 0 for c in CLASSES]

    # Raporda tek sütun genişliği (~3,4 in). Yatay çubuklar: sınıf adları dönmeden okunuyor.
    plt.rcParams.update({"font.size": 8, "font.family": "sans-serif"})
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    y = range(len(CLASSES))
    height = 0.62
    ax.barh(y, base, height=height, color=COLOR_ORIGINAL, label="Original label", zorder=3)
    ax.barh(y, merged, left=base, height=height, color=COLOR_MERGED,
            label="Merged from calm", zorder=3)
    # İki parça arasında ince bir boşluk, renk dışında da ayrılsınlar.
    ax.vlines(base[0], -height / 2, height / 2, color="white", linewidth=1.2, zorder=4)

    # Sadece birleştirilen çubuk etiketli; diğerlerinin değeri x ekseninden okunuyor.
    ax.text(base[0] / 2, 0, f"neutral {base[0]}", ha="center", va="center",
            color="white", fontsize=7, zorder=4)
    ax.text(base[0] + merged[0] / 2, 0, f"calm {merged[0]}", ha="center", va="center",
            color="white", fontsize=7, zorder=4)

    ax.set_yticks(list(y), CLASSES)
    ax.invert_yaxis()
    ax.set_xticks([0, 96, 192, 288])
    ax.set_xlim(0, 300)
    ax.set_xlabel("Clips", color=TEXT_SECONDARY)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.tick_params(colors=TEXT_SECONDARY, length=0)
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(TEXT_SECONDARY)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2,
              fontsize=7, handlelength=1.2, columnspacing=1.2, borderaxespad=0.2)

    fig.tight_layout()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"class_distribution.{ext}", dpi=300)
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(INDEX_PATH)
    meta = load_meta(df)

    rows = summary_rows(df, meta)
    write_summary(rows)
    plot_class_distribution(df)

    print(f"{META_PATH.relative_to(ROOT)}")
    print("results/dataset_summary.md, results/dataset_summary.tex")
    print("results/figures/class_distribution.pdf, .png\n")
    for k, v in rows:
        print(f"{k:28s} {v}")


if __name__ == "__main__":
    main()
