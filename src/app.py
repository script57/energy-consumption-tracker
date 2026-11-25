import logging
import sys
from pathlib import Path

import streamlit as st

# Proje kök dizinini import yolu olarak ekle
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.analyzer import (
    analyze_by_category,
    analyze_monthly_comparison,
    calculate_summary_metrics,
    records_to_dataframe,
)
from src.database import add_record, delete_record, get_all_records, init_db, seed_sample_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("energy-tracker")

st.set_page_config(
    page_title="Enerji Tüketim Takip Sistemi",
    page_icon="⚡",
    layout="wide",
)


def main() -> None:
    init_db()
    seed_sample_data()

    st.title("⚡ Enerji Tüketim Takip ve Analiz Sistemi")
    st.caption("YZM6443 - Modern Yazılım Mühendisliği: Bulut ve DevOps | Sağlık Durumu: 🟢 Aktif")

    # Yan Menü: Yeni Tüketim Kaydı Ekleme
    with st.sidebar:
        st.header("➕ Yeni Tüketim Kaydı")
        with st.form("add_record_form", clear_on_submit=True):
            period = st.text_input("Dönem (YYYY-AA)", value="2026-12", help="Örn: 2026-12")
            category = st.selectbox(
                "Tüketim Kategorisi",
                ["Genel Mesken", "İklimlendirme", "Isıtma / Kombi", "Aydınlatma", "Beyaz Eşya"],
            )
            kwh = st.number_input("Tüketim Miktarı (kWh)", min_value=0.0, value=250.0, step=10.0)
            unit_price = st.number_input("Birim Fiyat (TL/kWh)", min_value=0.0, value=2.65, step=0.05)
            submitted = st.form_submit_button("Kaydet", use_container_width=True)

            if submitted:
                if len(period.strip()) != 7 or "-" not in period:
                    st.error("Lütfen dönemi YYYY-AA formatında giriniz (Örn: 2026-12).")
                else:
                    rec_id = add_record(period, category, kwh, unit_price)
                    logger.info("Yeni tüketim kaydı eklendi: ID=%s, Dönem=%s, kWh=%s", rec_id, period, kwh)
                    st.success(f"Kayıt başarıyla eklendi! (ID: {rec_id})")
                    st.rerun()

    records = get_all_records()
    metrics = calculate_summary_metrics(records)
    monthly_df = analyze_monthly_comparison(records)
    category_df = analyze_by_category(records)

    # Üst Metrik Kartları
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Tüketim", f"{metrics['total_kwh']} kWh")
    col2.metric("Toplam Fatura Tutarı", f"{metrics['total_cost']} ₺")
    col3.metric("Aylık Ortalama", f"{metrics['avg_monthly_kwh']} kWh")
    col4.metric("En Yüksek Dönem", metrics["peak_period"])

    st.divider()

    # Grafikler: Aylık Karşılaştırma ve Kategori Dağılımı
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("📊 Aylık Elektrik Tüketimi (kWh)")
        if not monthly_df.empty:
            st.bar_chart(monthly_df.set_index("period")["total_kwh"])
        else:
            st.info("Henüz veri bulunmuyor.")

    with chart_col2:
        st.subheader("🏷️ Kategori Bazlı Tüketim (kWh)")
        if not category_df.empty:
            st.bar_chart(category_df.set_index("category")["total_kwh"])
        else:
            st.info("Henüz veri bulunmuyor.")

    # Aylık Karşılaştırma Analiz Tablosu
    st.subheader("📈 Aylık Karşılaştırma ve Değişim Analizi (Pandas)")
    if not monthly_df.empty:
        display_monthly = monthly_df.rename(
            columns={
                "period": "Dönem",
                "total_kwh": "Toplam Tüketim (kWh)",
                "total_cost": "Toplam Maliyet (TL)",
                "kwh_diff": "Önceki Aya Fark (kWh)",
                "pct_change": "Değişim (%)",
            }
        )
        st.dataframe(display_monthly, use_container_width=True, hide_index=True)

    # Tüm Kayıtlar ve Kayıt Silme
    st.subheader("📋 Tüm Tüketim Kayıtları")
    df_all = records_to_dataframe(records)
    if not df_all.empty:
        st.dataframe(
            df_all[["id", "period", "category", "kwh", "unit_price", "total_cost"]],
            use_container_width=True,
            hide_index=True,
        )
        with st.expander("🗑️ Kayıt Sil"):
            del_id = st.selectbox("Silinecek Kayıt ID", df_all["id"].tolist())
            if st.button("Seçili Kaydı Sil"):
                if delete_record(int(del_id)):
                    logger.info("Kayıt silindi: ID=%s", del_id)
                    st.warning(f"ID {del_id} kaydı silindi.")
                    st.rerun()


if __name__ == "__main__":
    main()
