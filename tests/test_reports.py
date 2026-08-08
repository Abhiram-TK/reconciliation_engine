import pandas as pd

from app.clients.sales_client import SalesClient
from app.clients.inventory_client import InventoryClient

from app.services.normalization_service import normalize_dataframe
from app.services.compare_service import compare_records

from app.reporting.report_generator import ReportGenerator

def test_report_generation_pipeline(monkeypatch, tmp_path):

    sales_client = SalesClient()
    inventory_client = InventoryClient()

    # Retrieve authoritative upstream data.
    source_df = sales_client.get_sales_records()
    target_df = inventory_client.get_inventory_records()

    assert isinstance(source_df, pd.DataFrame)
    assert isinstance(target_df, pd.DataFrame)

    assert not source_df.empty
    assert not target_df.empty

    # Normalize the actual upstream contracts.
    source_df = normalize_dataframe(source_df)
    target_df = normalize_dataframe(target_df)

    # Produce comparison results from normalized upstream data.
    comparison_results = compare_records(source_df, target_df)

    assert isinstance(comparison_results, list)

    assert comparison_results

    for result in comparison_results:

        assert "transaction_id" in result
        assert "status" in result

    # Redirect report output to pytest's temporary directory.
    reports_dir = tmp_path / "reports"

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", reports_dir)

    report_generator = ReportGenerator()

    report_generator.generate_reports(comparison_results)

    matched_file = (reports_dir / "matched.csv")

    mismatched_file = (reports_dir / "mismatched.csv")

    missing_file = (reports_dir / "missing.csv")

    assert matched_file.exists()
    assert mismatched_file.exists()
    assert missing_file.exists()

    matched_df = pd.read_csv(matched_file)

    mismatched_df = pd.read_csv(mismatched_file)

    missing_df = pd.read_csv(missing_file)

    generated_count = (len(matched_df) + len(mismatched_df) + len(missing_df))

    assert generated_count == len(comparison_results)