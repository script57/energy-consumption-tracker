from typing import Dict, List
import pandas as pd


def records_to_dataframe(records: List[Dict]) -> pd.DataFrame:
    """Kayıt listesini Pandas DataFrame yapısına dönüştürür."""
    columns = ["id", "period", "category", "kwh", "unit_price", "total_cost", "created_at"]
    if not records:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(records)
    df["kwh"] = pd.to_numeric(df["kwh"], errors="coerce").fillna(0.0)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    df["total_cost"] = pd.to_numeric(df["total_cost"], errors="coerce").fillna(0.0)
    return df


def calculate_summary_metrics(records: List[Dict]) -> Dict[str, float]:
    """Toplam kWh, toplam maliyet, aylık ortalama kWh ve en yüksek dönemi hesaplar."""
    df = records_to_dataframe(records)
    if df.empty:
        return {
            "total_kwh": 0.0,
            "total_cost": 0.0,
            "avg_monthly_kwh": 0.0,
            "peak_period": "-",
        }

    monthly = df.groupby("period", as_index=False)["kwh"].sum()
    peak_row = monthly.loc[monthly["kwh"].idxmax()]

    return {
        "total_kwh": round(float(df["kwh"].sum()), 2),
        "total_cost": round(float(df["total_cost"].sum()), 2),
        "avg_monthly_kwh": round(float(monthly["kwh"].mean()), 2),
        "peak_period": str(peak_row["period"]),
    }


def analyze_monthly_comparison(records: List[Dict]) -> pd.DataFrame:
    """Aylık toplam tüketim, maliyet ve bir önceki aya göre fark/yüzde değişimi hesaplar."""
    df = records_to_dataframe(records)
    if df.empty:
        return pd.DataFrame(
            columns=["period", "total_kwh", "total_cost", "kwh_diff", "pct_change"]
        )

    monthly = (
        df.groupby("period", as_index=False)
        .agg(total_kwh=("kwh", "sum"), total_cost=("total_cost", "sum"))
        .sort_values("period")
        .reset_index(drop=True)
    )

    monthly["kwh_diff"] = monthly["total_kwh"].diff().fillna(0.0).round(2)
    monthly["pct_change"] = (
        monthly["total_kwh"].pct_change().mul(100).fillna(0.0).round(2)
    )
    monthly["total_kwh"] = monthly["total_kwh"].round(2)
    monthly["total_cost"] = monthly["total_cost"].round(2)
    return monthly


def analyze_by_category(records: List[Dict]) -> pd.DataFrame:
    """Tüketim kategorilerine göre toplam kWh ve maliyet dağılımını döndürür."""
    df = records_to_dataframe(records)
    if df.empty:
        return pd.DataFrame(columns=["category", "total_kwh", "total_cost"])

    return (
        df.groupby("category", as_index=False)
        .agg(total_kwh=("kwh", "sum"), total_cost=("total_cost", "sum"))
        .sort_values("total_kwh", ascending=False)
        .reset_index(drop=True)
    )
