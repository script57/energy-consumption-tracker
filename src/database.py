import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "energy_data.db"


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """SQLite veritabanı bağlantısı döndürür."""
    target = str(db_path) if db_path else str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """energy_records tablosunu yoksa oluşturur."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS energy_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL,
                category TEXT NOT NULL,
                kwh REAL NOT NULL CHECK(kwh >= 0),
                unit_price REAL NOT NULL CHECK(unit_price >= 0),
                total_cost REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def add_record(
    period: str,
    category: str,
    kwh: float,
    unit_price: float,
    db_path: Optional[str] = None,
) -> int:
    """Yeni bir elektrik tüketim kaydı ekler ve kayıt ID'sini döndürür."""
    if kwh < 0 or unit_price < 0:
        raise ValueError("kWh ve birim fiyat negatif olamaz.")
    total_cost = round(float(kwh) * float(unit_price), 2)
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO energy_records (period, category, kwh, unit_price, total_cost)
            VALUES (?, ?, ?, ?, ?)
            """,
            (period.strip(), category.strip(), float(kwh), float(unit_price), total_cost),
        )
        conn.commit()
        return int(cursor.lastrowid)


def get_all_records(db_path: Optional[str] = None) -> List[Dict]:
    """Tüm elektrik tüketim kayıtlarını dönem sırasına göre listeler."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, period, category, kwh, unit_price, total_cost, created_at
            FROM energy_records
            ORDER BY period ASC, id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def delete_record(record_id: int, db_path: Optional[str] = None) -> bool:
    """Belirtilen ID'ye sahip kaydı siler."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM energy_records WHERE id = ?", (record_id,))
        conn.commit()
        return cursor.rowcount > 0


def seed_sample_data(db_path: Optional[str] = None) -> None:
    """Veritabanı boşsa demo amaçlı örnek aylık veriler ekler."""
    if not get_all_records(db_path):
        samples = [
            ("2026-08", "Genel Mesken", 310.0, 2.40),
            ("2026-08", "İklimlendirme", 145.0, 2.40),
            ("2026-09", "Genel Mesken", 295.0, 2.50),
            ("2026-09", "İklimlendirme", 90.0, 2.50),
            ("2026-10", "Genel Mesken", 330.0, 2.60),
            ("2026-10", "Aydınlatma", 65.0, 2.60),
            ("2026-11", "Genel Mesken", 385.0, 2.60),
            ("2026-11", "Isıtma / Kombi", 120.0, 2.60),
        ]
        for period, cat, kwh, price in samples:
            add_record(period, cat, kwh, price, db_path=db_path)
