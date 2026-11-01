# Enerji Tuketim Takip Sistemi (Energy Consumption Tracker)

**Ders:** YZM6443 - Modern Yazilim Muhendisligi: Bulut ve DevOps
**Ogrenci:** Anil Mevlut Caliskan (2304040302)
**Is Alani:** Enerji (Energy & Utilities)

## Proje Tanimi
Elektrik tuketim verilerinin (kWh) kaydedilmesini, maliyetlerinin hesaplanmasini, Pandas ile aylik karsilastirmali analizinin yapilmasini ve Streamlit uzerinden grafiksel olarak gorsellestirilmesini saglayan bulut tabanli uygulamadir.

## Temel Fonksiyonlar
1. **Tuketim Kaydi Ekleme ve Listeleme:** Donem, kategori, tuketim miktari (kWh) ve birim fiyat (TL/kWh) kaydi.
2. **Otomatik Maliyet Hesaplama:** Toplam fatura tutari ve ortalama aylik tuketim analizi.
3. **Aylik Karsilastirma Analizi (Pandas):** Aylar arasi tuketim farklari ve yuzdesel degisim analizi.
4. **Gorsel Analiz ve Grafikler:** Streamlit uzerinde aylik tuketim trend grafikleri.

## Kullanilan Teknolojiler
* Python 3.11, Streamlit, Pandas, SQLite, Pytest, Git, GitHub Actions, Docker

## Kurulum ve Calistirma
`ash
pip install -r requirements.txt
streamlit run src/app.py
pytest tests/
``r

## Baglantilar
* **GitHub Repository:** https://github.com/script57/energy-consumption-tracker
