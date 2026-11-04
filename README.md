# Atatürk AI — tarihî kaynak asistanı

Bu Python prototipi, Atatürk Araştırma Merkezi (ATAM) sayfalarına bağlantı veren sınırlı bir kaynak koleksiyonunda arama yapar. Henüz bir dil modeli kullanmaz; Atatürk'ün günümüzdeki görüşlerini temsil ettiğini iddia etmez.

## Positron'da çalıştırma

1. Bu klasörü Positron'da açın.
2. Positron terminalinde `python3 app.py` komutunu çalıştırın.
3. Tarayıcıda `http://127.0.0.1:8501` adresini açın.

Uygulama Python'un standart kütüphanesini kullanır; ek paket kurmanız gerekmez. Durdurmak için terminalde Ctrl+C tuşlarına basın.

## Kaynak ekleme

`data/sources.json` dosyasına her belge için aşağıdaki alanlarla kayıt ekleyin:

```json
{
  "title": "Belgenin başlığı",
  "date": "Tarih",
  "type": "Konuşma, mektup, kitap vb.",
  "source": "Yayın veya arşiv künyesi",
  "content": "Doğrulanmış metin veya kısa alıntı",
  "tags": ["konu"],
  "url": "https://..."
}
```

Kaynakları yayımlamadan önce güvenilirliği, bağlamı ve kullanım haklarını doğrulayın. Örnek JSON kaydı yalnızca biçimi gösterir; gerçek tarihî alıntı değildir.

## İnternette yayımlama

Bu proje `render.yaml` ile Render Blueprint dağıtımına hazırlanmıştır. Proje dosyalarını GitHub deposuna yükledikten sonra Render panelinde **New → Blueprint** seçin ve depoyu bağlayın. Render bir `onrender.com` adresi üretir; bu adres başkalarıyla paylaşılabilir. Ücretsiz web hizmetleri boş kaldığında uykuya geçebilir.

## Sonraki geliştirme adımları

- Arşiv kaynakları için katalog ve kaynak güven puanlaması
- Sayfa ve paragraf düzeyinde atıf, OCR kalite kontrolü
- Uzmanlarca hazırlanmış değerlendirme soruları ve doğruluk ölçümü
- Yalnızca kaynaklı yanıt veren arama-üretim sistemi
- Ses/avatar gibi sunum özellikleri için açık simülasyon etiketi
