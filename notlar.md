# Proje Notları

Progress Report'taki "Problems encountered" ve "Preprocessing" bölümleri buradan yazılacak.

## Sorunlar günlüğü

Her satır: tarih, sorun, çözüm.

| Tarih | Sorun | Çözüm |
|---|---|---|
| 2026-10-17 | GPU hesapları için NumPy yerine CuPy kullanmak düşünüldü. CuPy NVIDIA CUDA istiyor, Apple M5'te CUDA yok. | GPU'ya giden işler PyTorch (MPS) ile yapılacak. NumPy sadece CPU'daki hafif işler için (indeks, metrik, grafik). |
| 2026-10-17 | `.venv`'e kurulan PyTorch 2.14.1, sistemdeki sürüm 2.12.1. | Proje `.venv` içindeki 2.14.1'i kullanıyor. README ve `requirements.txt`'e bu sürüm yazılacak. |
| 2026-10-18 | Her zip'te aynı `Actor_XX/` klasöründe hem `01-*` (ses+görüntü) hem `02-*` (sadece görüntü) var. İkisi aynı görüntü, birlikte alınırsa her klip iki kez sayılır. | Zip'lerden sadece `02-*` çıkarıldı. Sonuç: 1440 klip, her aktörde 60. |
| 2026-10-18 | Proposal'da "30 fps" yazıyor, ffprobe ile ölçülen değer bütün kliplerde 29.97 fps (30000/1001, NTSC). | Raporlarda 29.97 yazılacak. Kare örneklemede fark etmez, çünkü eşit aralıkla kare indeksi seçiliyor, zaman damgası kullanılmıyor. |
| 2026-10-23 | Üst klasörün adı `- Proje` → `Derin Ogrenme - Proje` olunca `.venv` bozuldu: `activate` ve `pip` eski yolu gösteriyor. `source .venv/bin/activate` sonrası `python` sessizce sistem Python'una (torch 2.12.1) düşüyor. | `.venv` silinip `requirements.txt` ile yeniden kurulacak. Bundan sonra klasör adları değişmeyecek; değişirse `.venv` yeniden kurulur. |
| 2026-10-18 | Disk: zip'ler 12 GB, çıkarılmış `02-*` klipleri 6,3 GB. Zip'lerin yarısı (01-*) hiç kullanılmayacak. | Şimdilik zip'ler duruyor. Çıkarma doğrulandıktan sonra silinebilir, gerekirse Zenodo'dan tekrar indirilir (MD5'ler belli). |

## Kararlar

| Tarih | Karar | Gerekçe |
|---|---|---|
| 2026-10-17 | Sadece modality 02 (video-only) ve speech kullanılıyor. Song yok. | Proje sadece görsel modaliteyle çalışıyor. 01 aynı görüntüyü içerdiği için veri iki kez sayılırdı. |
| 2026-10-17 | Veri, Zenodo record 1188976'dan indirildi, 24 zip'in MD5'i doğrulandı. | Resmi kaynak, CC BY-NC-SA 4.0. Doğrulama tekrarlanabilirlik için. |
| 2026-10-18 | Calm ve neutral tek sınıf (`neutral`) olarak birleştirildi: 8 → 7 sınıf. | İkisi yüzde görsel olarak çok benzer. VTuber modelinde de ayrı ifadeleri yok. |
| 2026-10-18 | İndeks `src/build_index.py` ile dosya adlarından çıkarılıyor, `results/index.csv`'ye yazılıyor. Etiket sırası sabit: neutral=0, happy=1, sad=2, angry=3, fearful=4, disgust=5, surprised=6. | Tüm modeller ve metrikler aynı etiket sırasını kullansın. Sayı kontrolleri script içinde `assert` ile yapılıyor, hepsi geçti. |
| 2026-10-18 | Aktörler 6 fold'a ayrıldı (`src/splits.py` → `results/splits.json`). Her fold 2E + 2K. CV fold k: test = fold k, val = fold k+1, train = kalan 16 aktör. Sabit bölme = CV fold 0 (960 / 240 / 240 klip). Güncel aktör listesi aşağıdaki 2026-10-20 satırında. | Aktör bazlı bölme, model test sırasında hiç görmediği yüzlerle karşılaşsın diye. Cinsiyet dengesi, val/test sonuçları tek cinsiyete kaymasın diye. Sabit bölmenin bir CV fold'u olması, geliştirme sonuçlarını final CV ile karşılaştırılabilir yapıyor. |
| 2026-10-18 | Test aktörleri kilitli: `load_split()` varsayılan olarak sadece train/val döndürüyor, test için `allow_test=True` gerekiyor. | §5: test kümesi model geliştirme sırasında kullanılmamalı. Yanlışlıkla kullanmayı kod seviyesinde engellemek için. |
| 2026-10-20 | Projenin tek seed'i **4206** (`src/utils.py` → `SEED`). `set_seed()` Python, NumPy ve PyTorch'u (CPU/MPS) sabitliyor; DataLoader için `seed_worker` ve `make_generator` var. Aktör bölmesi de bu seed'den üretiliyor. | Tekrarlanabilirlik (§15). Tek yerde tanımlı olması, bölme ile eğitimin farklı seed kullanmasını engelliyor. |
| 2026-10-20 | Seed 42 → 4206 değişince aktör bölmesi yeniden üretildi. Yeni fold'lar: 0 {4, 6, 7, 23}, 1 {3, 12, 21, 24}, 2 {1, 8, 13, 16}, 3 {11, 18, 19, 22}, 4 {10, 15, 17, 20}, 5 {2, 5, 9, 14}. Sabit bölme: **test {4, 6, 7, 23}**, **val {3, 12, 21, 24}**, train kalan 16 aktör. | Henüz hiçbir model eğitilmediği ve test aktörlerine bakılmadığı için bölmeyi değiştirmek güvenli. Bundan sonra bölme sabit, değiştirilmeyecek. |
| 2026-10-23 | Raporlar LaTeX'te, proposal'la aynı şablonda (`report/progress/progress.tex`, iki sütun). Her bölüm `report/progress/sections/` altında ayrı dosya. Şekil ve tablolar doğrudan `results/`'tan okunuyor. | Sayılar değişirse `src/eda.py` yeniden çalışır, rapor kendiliğinden güncellenir; elle kopyalama hatası olmaz. |
| 2026-10-23 | Sınıf dağılımı grafiği tek sütun genişliğinde (3,4 in) yatay çubuk olarak yeniden çizildi; özet tablodaki bölme satırı train/val/test olarak üçe ayrıldı. | Geniş grafik iki sütunlu rapora küçültülünce yazılar ~5 pt'ye iniyordu; tablo satırı sütuna sığmıyordu. |
| 2026-10-23 | **Takvim değişikliği:** Hafta 5 tamamen 3D modele (tasarım → rig) ayrıldı. Hafta 5'in DL işleri (preprocessing, EDA görselleri, baseline başlangıcı) Hafta 6'ya, ResNet-18 Hafta 7'nin başına, 3D ifadeler + VRM dışa aktarma Hafta 6'dan Hafta 8'e kaydı. Progress Report teslimi (Hafta 7) aynı. | Rig'i tek seferde, bölünmeden bitirmek için. İfadeler Hafta 8'e alındı ki Hafta 6–7 sadece DL ve rapora kalsın. Risk: Hafta 6–7 yoğun; önlem olarak eğitim kodu model bağımsız yazılacak, ResNet-18 yetişmezse donuk omurgayla ilk sonuç raporlanacak. Revised methodology bölümüne girecek. |
| 2026-10-20 | Paket sürümleri `requirements.txt`'de sabitlendi (Python 3.13.13, torch 2.14.1, torchvision 0.29.1 …). | Sonradan "hangi sürümle eğitmiştim" sorusu çıkmasın; README'de de bu dosyaya referans verilecek. |

## Veri seti gözlemleri (Dataset analysis için)

- Neutral'da sadece normal yoğunluk var, strong yok. Bu yüzden aktör başına neutral 4 klip, diğer her duygu 8 klip (2 yoğunluk × 2 cümle × 2 tekrar). 4 + 7 × 8 = 60.
- Toplamda neutral 96, calm 192 klip. Birleşince neutral 288, diğer altı sınıfın her biri 192. Sınıflar dengesiz, bu yüzden ana metrik macro-F1.
- Aktörlerin tek numaralıları erkek, çift numaralıları kadın (12E + 12K).
- Her aktörde bütün duygular aynı sayıda olduğu için her fold sınıf olarak da otomatik dengeli: 4 aktör = 240 klip, neutral 48, diğer her sınıf 32. Ayrıca sınıf bazlı stratifikasyon gerekmedi.
- Bütün klipler h264, 1280×720, 29.97 fps (`results/video_meta.csv`).
- Klip başına kare sayısı 88–158 (medyan 110), süre 2.94–5.27 s (medyan 3.67 s). En kısa klipte bile 88 kare var, yani T = 8, 16, 32 için yeterli kare var; T = 32'de bile kareler arası ≈ 3 kare boşluk kalıyor.

## Şekil ve tablolar

| Dosya | İçerik | Nerede kullanılacak |
|---|---|---|
| `results/figures/class_distribution.pdf` | 7 sınıfın klip sayısı; neutral çubuğu orijinal neutral (96) + calm'dan gelen (192) olarak ikiye bölünmüş | Progress Report §1, Final Report §5 |
| `results/dataset_summary.tex` / `.md` | Veri seti özet tablosu (kaynak, klip/aktör sayısı, çözünürlük, fps, kare sayısı, süre, sınıflar, bölme) | Progress Report §1, Final Report §5 |
| `report/progress/sections/dataset.tex` | Dataset analysis taslağı (İngilizce, ~1 sayfa) | Progress Report §1 |

## Preprocessing notları (ne ve neden)

Hafta 5'te tam metne dönüşecek.

- (henüz yok)
