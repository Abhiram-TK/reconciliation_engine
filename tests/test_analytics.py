import pandas as pd

from app.core.config import settings

from app.clients.sales_client import SalesClient
from app.clients.inventory_client import InventoryClient

from app.services.normalization_service import normalize_dataframe
from app.services.compare_service import compare_records

from app.reporting.analytics import (generate_summary, save_summary, generate_chart)

def test_analytics_pipeline(monkeypatch, tmp_path):

    assert settings.INVENTORY_SERVICE_TOKEN, ("INVENTORY_SERVICE_TOKEN must be configured for authenticated Inventory API access")

    sales_client = SalesClient()
    inventory_client = InventoryClient()

    source_df = sales_client.get_sales_records()
    target_df = inventory_client.get_inventory_records()

    assert isinstance(source_df, pd.DataFrame)

    assert isinstance(target_df, pd.DataFrame)

    assert not source_df.empty
    assert not target_df.empty

    source_df = normalize_dataframe(source_df)

    target_df = normalize_dataframe(target_df)

    comparison_results = compare_records(source_df, target_df)

    comparison_df = pd.DataFrame(comparison_results)

    assert not comparison_df.empty
    assert "status" in comparison_df.columns

    reports_dir = tmp_path / "reports"
    charts_dir = reports_dir / "charts"

    monkeypatch.setattr("app.reporting.analytics.settings.reports_dir", reports_dir)

    monkeypatch.setattr("app.reporting.analytics.settings.charts_dir", charts_dir)

    summary_df = generate_summary(comparison_df)

    assert not summary_df.empty

    assert list(summary_df.columns) == ["Status", "Count"]

    assert summary_df["Count"].sum() == len(comparison_df)

    save_summary(summary_df)

    generate_chart(summary_df)

    summary_file = (reports_dir / "summary.csv")

    chart_file = (charts_dir / "reconciliation_summary.png")

    assert summary_file.exists()
    assert chart_file.exists()

    saved_summary = pd.read_csv(summary_file)

    assert list(saved_summary.columns) == ["Status", "Count"]

    assert saved_summary["Count"].sum() == len(comparison_df)