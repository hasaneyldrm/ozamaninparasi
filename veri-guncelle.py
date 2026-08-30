#!/usr/bin/env python3
"""USD/TRY kuru ve ABD TUFE serisini kaynaklardan cekip data.js dosyasini uretir."""

import json
import re
import urllib.request
from collections import defaultdict
from datetime import date

BASLANGIC = "1999-01-04"
ECB = "https://api.frankfurter.dev/v1/{}..{}?base=USD&symbols=TRY"
BLS = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
TCMB = "https://www.tcmb.gov.tr/kurlar/{y}{m}/{d}{m}{y}.xml"


def getir(url, veri=None, basliklar=None):
    istek = urllib.request.Request(url, data=veri, headers=basliklar or {})
    with urllib.request.urlopen(istek, timeout=60) as yanit:
        return yanit.read()


def kurlari_al(bugun):
    """ECB gunluk kurlarindan aylik ortalama uretir."""
    ham = json.loads(getir(ECB.format(BASLANGIC, bugun)))
    kovalar = defaultdict(list)
    for gun, deger in ham["rates"].items():
        if "TRY" in deger:
            kovalar[gun[:7]].append(deger["TRY"])
    return {ay: round(sum(v) / len(v), 4) for ay, v in kovalar.items()}


def eski_kurlari_al():
    """1997-1998: TCMB gunluk kurlari (eski TL -> YTL)."""
    kurlar = {}
    for yil in ("1997", "1998"):
        for ay in range(1, 13):
            aa = f"{ay:02d}"
            for gun in (15, 16, 17, 18, 14, 13):
                try:
                    xml = getir(TCMB.format(y=yil, m=aa, d=f"{gun:02d}")).decode("iso-8859-9")
                except Exception:
                    continue
                eslesme = re.search(r'Kod="USD".*?<ForexBuying>([\d.,]+)</ForexBuying>', xml, re.S)
                if eslesme:
                    kurlar[f"{yil}-{aa}"] = round(float(eslesme.group(1).replace(",", "")) / 1_000_000, 6)
                    break
    return kurlar


def tufe_al(son_yil):
    """BLS v1 API 10 yillik dilimler halinde veri doner."""
    seri = {}
    baslangic = 1997
    while baslangic <= son_yil:
        bitis = min(baslangic + 9, son_yil)
        govde = json.dumps({"seriesid": ["CUUR0000SA0"], "startyear": str(baslangic), "endyear": str(bitis)}).encode()
        yanit = json.loads(getir(BLS, govde, {"Content-Type": "application/json"}))
        if yanit.get("status") != "REQUEST_SUCCEEDED":
            raise SystemExit(f"BLS hatasi ({baslangic}-{bitis}): {yanit.get('message')}")
        for s in yanit["Results"]["series"]:
            for satir in s["data"]:
                if satir["period"].startswith("M") and satir["period"] != "M13":
                    try:
                        seri[f"{satir['year']}-{satir['period'][1:]}"] = float(satir["value"])
                    except ValueError:
                        pass
        baslangic = bitis + 1
    return seri


def guncel_kurlar():
    """Bugunku USD/TRY ve EUR/TRY (footer seridi ve son adim icin)."""
    ham = json.loads(getir("https://api.frankfurter.dev/v1/latest?base=USD&symbols=TRY,EUR"))
    usd_try = ham["rates"]["TRY"]
    return {"tarih": ham["date"], "usd": round(usd_try, 4), "eur": round(usd_try / ham["rates"]["EUR"], 4)}


def main():
    bugun = date.today()
    kur = eski_kurlari_al()
    kur.update(kurlari_al(bugun.isoformat()))
    tufe = tufe_al(bugun.year)

    payload = {
        "guncelleme": bugun.isoformat(),
        "kaynak": {"kur": "ECB (1999+) / TCMB (1997-1998)", "tufe": "ABD BLS — CUUR0000SA0"},
        "guncel": guncel_kurlar(),
        "kur": dict(sorted(kur.items())),
        "tufe": dict(sorted(tufe.items())),
    }
    with open("data.js", "w", encoding="utf-8") as dosya:
        dosya.write("window.VERI = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"data.js guncellendi — kur {len(kur)} ay, tufe {len(tufe)} ay")


if __name__ == "__main__":
    main()
