# O Zamanın Parası

Geçmiş bir yıldaki TL tutarının bugünkü karşılığını hesaplayan tek sayfalık site.

**Yöntem:** tutar → o dönemin ortalama dolar kuruyla dolara çevrilir → ABD tüketici fiyat
endeksiyle (TÜFE) bugüne taşınır → güncel kurla tekrar TL'ye döner.

Örnek: *2007'de 50.000 ₺ → 38.269 $ → dolar enflasyonuyla 61.630 $ → bugün ≈ 2,97 milyon ₺*

## Dosyalar

| Dosya | İşlev |
|---|---|
| `index.html` | Tüm arayüz ve hesap mantığı (bağımlılık yok) |
| `data.js` | Aylık USD/TRY kuru + ABD TÜFE serisi (1997–bugün) + güncel USD/EUR kurları |
| `veri-guncelle.py` | Verileri kaynaklardan yeniden çekip `data.js`'i üretir |

## Veri kaynakları

- **Kur:** ECB referans kurları (1999+, günlüklerin aylık ortalaması), TCMB (1997–1998)
- **ABD TÜFE:** BLS `CUUR0000SA0` (mevsimsellikten arındırılmamış)
- Sayfa açılışında güncel USD/TRY ve EUR/TRY kurunu `frankfurter.dev` üzerinden tazelemeye
  çalışır; başarısız olursa `data.js` içindeki son kapanış değerleriyle devam eder.

## Notlar

- 2005'te paradan 6 sıfır atıldığı için 2005 öncesi yıllarda "Eski TL" kutusu görünür;
  işaretliyken girilen tutar 1.000.000'e bölünür.
- Ay seçilmezse o yılın 12 aylık ortalaması kullanılır.
- Paylaşılabilir bağlantı: `#50000-2007-6` (tutar-yıl-ay), eski TL için sonuna `-eski`.

## Veriyi güncelleme

```bash
python3 veri-guncelle.py
```

## Yayın

GitHub Pages: repo ayarlarından Pages → Branch `main` / `root`.
