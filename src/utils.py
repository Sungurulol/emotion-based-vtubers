"""Projenin ortak yardımcıları: sabit seed ve cihaz seçimi."""

import os
import random

import numpy as np
import torch

# Projenin tek seed'i. Aktör bölmesi, eğitim ve augmentation hepsi bunu kullanır.
SEED = 4206


def set_seed(seed: int = SEED) -> None:
    """Python, NumPy ve PyTorch (CPU, MPS, CUDA) rastgeleliğini sabitler.

    Not: MPS'te bazı işlemler deterministik değil, aynı seed ile çok küçük
    sayısal farklar çıkabilir. Sonuçlar bu yüzden tek koşuya değil CV'ye dayanıyor.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)  # CPU, MPS ve CUDA cihazlarının hepsini seed'ler
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def seed_worker(worker_id: int) -> None:
    """DataLoader worker'larının her birine farklı ama tekrarlanabilir seed verir.

    Kullanım: DataLoader(..., worker_init_fn=seed_worker, generator=make_generator())
    """
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def make_generator(seed: int = SEED) -> torch.Generator:
    g = torch.Generator()
    g.manual_seed(seed)
    return g


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")
