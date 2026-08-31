# Sayaç Worker'ı

`sayac.js`, `ozamaninparasiyla.com/api/sayac` adresinde çalışan ziyaret sayacıdır.

- **Tekilleştirme:** IP + tarayıcı imzasının hash'i Cache API'de 24 saat tutulur; aynı ziyaretçi tekrar sayılmaz.
- **KV yazımı:** yalnız toplam sayı yazılır ve biriktirilerek (20 ziyarette bir ya da 5 dakikada bir),
  böylece ücretsiz plandaki 1.000 yazma/gün limiti dolmaz.
- **KV namespace:** `ozamaninparasiyla-sayac`
- **Yanıt:** `{"toplam": 1234, "yeni": true}`

## Yeniden yüklemek

```bash
TOKEN=$(cat ~/.cf_token); ACC=<account_id>
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -F 'metadata=@metadata.json;type=application/json' \
  -F 'sayac.js=@sayac.js;type=application/javascript+module' \
  "https://api.cloudflare.com/client/v4/accounts/$ACC/workers/scripts/sayac"
```
