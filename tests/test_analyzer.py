import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.analyzer import (
    analyze_by_category,
    analyze_monthly_comparison,
    calculate_summary_metrics,
)
from src.database import add_record, get_all_records


def test_calculate_summary_metrics():
    """Toplam kWh, maliyet, aylık ortalama ve zirve dönem hesaplamasını test eder."""
    sample_records = [
        {"id": 1, "period": "2026-08", "category": "Genel Mesken", "kwh": 200.0, "unit_price": 2.5, "total_cost": 500.0, "created_at": ""},
        {"id": 2, "period": "2026-09", "category": "İklimlendirme", "kwh": 400.0, "unit_price": 2.5, "total_cost": 1000.0, "created_at": ""},
    ]
    metrics = calculate_summary_metrics(sample_records)

    assert metrics["total_kwh"] == 600.0
    assert metrics["total_cost"] == 1500.0
    assert metrics["avg_monthly_kwh"] == 300.0
    assert metrics["peak_period"] == "2026-09"


def test_analyze_monthly_comparison():
    """Ardışık aylar arasındaki kWh farkı ve yüzdesel değişim analizini test eder."""
    sample_records = [
        {"id": 1, "period": "2026-08", "category": "Genel Mesken", "kwh": 200.0, "unit_price": 2.0, "total_cost": 400.0, "created_at": ""},
        {"id": 2, "period": "2026-09", "category": "Genel Mesken", "kwh": 250.0, "unit_price": 2.0, "total_cost": 500.0, "created_at": ""},
    ]
    df = analyze_monthly_comparison(sample_records)

    assert len(df) == 2
    assert df.loc[1, "kwh_diff"] == 50.0
    assert df.loc[1, "pct_change"] == 25.0


def test_analyze_by_category():
    """Kategori bazlı toplam tüketim ve maliyet gruplamasını test eder."""
    sample_records = [
        {"id": 1, "period": "2026-08", "category": "Aydınlatma", "kwh": 50.0, "unit_price": 2.0, "total_cost": 100.0, "created_at": ""},
        {"id": 2, "period": "2026-09", "category": "Aydınlatma", "kwh": 70.0, "unit_price": 2.0, "total_cost": 140.0, "created_at": ""},
        {"id": 3, "period": "2026-09", "category": "Genel Mesken", "kwh": 300.0, "unit_price": 2.0, "total_cost": 600.0, "created_at": ""},
    ]
    cat_df = analyze_by_category(sample_records)

    assert cat_df.iloc[0]["category"] == "Genel Mesken"
    assert cat_df.iloc[0]["total_kwh"] == 300.0
    assert cat_df.iloc[1]["total_kwh"] == 120.0


def test_database_add_and_get_records(tmp_path):
    """Geçici SQLite veritabanına kayıt ekleme, maliyet hesaplama ve okuma işlemini test eder."""
    test_db = tmp_path / "test_energy.db"
    rec_id = add_record("2026-10", "Genel Mesken", 150.0, 3.0, db_path=str(test_db))

    assert rec_id == 1
    records = get_all_records(db_path=str(test_db))
    assert len(records) == 1
    assert records[0]["total_cost"] == 450.0

    with pytest.raises(ValueError):
        add_record("2026-10", "Genel Mesken", -10.0, 3.0, db_path=str(test_db))
