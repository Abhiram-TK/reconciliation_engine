import json

import pandas as pd

from app.reporting.analytics import (generate_summary, save_summary, generate_chart)

def build_final_reconciliation_result():

    return pd.DataFrame(
        [
            # --------
            # MATCHED
            # --------
            {
                "transaction_id": 101,
                "invoice_number": "INV-2026-000101",
                "status": "MATCHED",
                "mismatch_type": None,
                "quantity": 5,
                "reserved_quantity": 5,
                "reservation_count": 1
            },
            # ------------------
            # QUANTITY MISMATCH
            # ------------------
            {
                "transaction_id": 102,
                "invoice_number": "INV-2026-000102",
                "status": "MISMATCHED",
                "mismatch_type": "QUANTITY_MISMATCH",
                "quantity": 10,
                "reserved_quantity": 7,
                "reservation_count": 1
            },
            # ----------------------
            # DUPLICATE RESERVATION
            # ----------------------
            {
                "transaction_id": 103,
                "invoice_number": "INV-2026-000103",
                "status": "MISMATCHED",
                "mismatch_type": "DUPLICATE_RESERVATION",
                "quantity": 5,
                "reserved_quantity": 5,
                "reservation_count": 2,
                "reservation_ids": [503, 504],
                "reserved_quantities": [3, 2]
            },
            # --------------------
            # MISSING RESERVATION
            # --------------------
            {
                "transaction_id": 104,
                "invoice_number": "INV-2026-000104",
                "status": "MISSING",
                "mismatch_type": "MISSING_RESERVATION",
                "quantity": 3,
                "reserved_quantity": None,
                "reservation_count": 0
            },
            # -------------------
            # ORPHAN RESERVATION
            # -------------------
            {
                "transaction_id": 105,
                "invoice_number": None,
                "status": "MISMATCHED",
                "mismatch_type": "ORPHAN_RESERVATION",
                "quantity": None,
                "reserved_quantity": 6,
                "reservation_count": 1,
                "reservation_ids": [505],
                "reserved_quantities": [6]
            }])

def test_generate_summary_reflects_final_reconciliation_statuses():

    comparison_df = (build_final_reconciliation_result())

    summary_df = generate_summary(comparison_df)

    assert not summary_df.empty

    assert list(summary_df.columns) == ["category_type", "category", "count"]

    status_summary = summary_df[summary_df["category_type"] == "status"]

    assert dict(zip(status_summary["category"], status_summary["count"])) == {"MATCHED": 1,
                                                                              "MISMATCHED": 3,
                                                                              "MISSING": 1}

    assert status_summary["count"].sum() == len(comparison_df)

def test_generate_summary_includes_detailed_mismatch_categories():

    comparison_df = (build_final_reconciliation_result())

    summary_df = generate_summary(comparison_df)

    mismatch_summary = summary_df[summary_df["category_type"] == "mismatch_type"]

    assert dict(zip(mismatch_summary["category"], mismatch_summary["count"],)) == {"QUANTITY_MISMATCH": 1,
                                                                                   "DUPLICATE_RESERVATION": 1,
                                                                                   "MISSING_RESERVATION": 1,
                                                                                   "ORPHAN_RESERVATION": 1}

def test_generate_summary_does_not_double_count_final_results():

    comparison_df = (build_final_reconciliation_result())

    summary_df = generate_summary(comparison_df)

    status_summary = summary_df[summary_df["category_type"] == "status"]

    mismatch_summary = summary_df[summary_df["category_type"] == "mismatch_type"]

    # Primary status counts represent the final reconciliation result set exactly once.
    assert status_summary["count"].sum() == len(comparison_df)

    # Detailed mismatch categories are diagnostic classifications, not additional reconciliation records.
    assert mismatch_summary["count"].sum() == comparison_df["mismatch_type"].notna().sum()

def test_generate_summary_handles_results_without_mismatch_type():

    comparison_df = pd.DataFrame([
            {
                "transaction_id": 201,
                "status": "MATCHED"
            },
            {
                "transaction_id": 202,
                "status": "MISSING"
            }])

    summary_df = generate_summary(comparison_df)

    assert list(summary_df.columns) == ["category_type",
                                        "category",
                                        "count"]

    assert set(summary_df["category_type"]) == {"status"}

    assert dict(zip(summary_df["category"], summary_df["count"],)) == {"MATCHED": 1, "MISSING": 1}

def test_save_summary_writes_final_summary_to_temporary_directory(monkeypatch, tmp_path):

    reports_dir = (tmp_path / "reports")

    monkeypatch.setattr("app.reporting.analytics.settings.reports_dir", reports_dir)

    comparison_df = (build_final_reconciliation_result())

    summary_df = generate_summary(comparison_df)

    summary_path = save_summary(summary_df)

    expected_path = (reports_dir / "summary.csv")

    assert summary_path == expected_path
    assert summary_path.exists()

    saved_summary = pd.read_csv(summary_path)

    assert list(saved_summary.columns) == ["category_type",
                                           "category",
                                           "count"]

    saved_status_summary = (saved_summary[saved_summary["category_type"] == "status"])

    assert saved_status_summary["count"].sum() == len(comparison_df)

def test_generate_chart_uses_same_summary_data(monkeypatch, tmp_path):

    reports_dir = (tmp_path / "reports")

    charts_dir = (reports_dir / "charts")

    monkeypatch.setattr("app.reporting.analytics.settings.reports_dir", reports_dir)

    monkeypatch.setattr("app.reporting.analytics.settings.charts_dir", charts_dir)

    comparison_df = (build_final_reconciliation_result())

    summary_df = generate_summary(comparison_df)

    captured_chart_data = {}

    real_bar = (__import__("app.reporting.analytics", fromlist=["plt"],).plt.bar)

    def capture_bar(labels, counts, *args, **kwargs):

        captured_chart_data["labels"] = list(labels)

        captured_chart_data["counts"] = list(counts)

        return real_bar(labels, counts, *args, **kwargs)

    monkeypatch.setattr("app.reporting.analytics.plt.bar", capture_bar)

    chart_path = generate_chart(summary_df)

    assert chart_path == (charts_dir / "reconciliation_summary.png")

    assert chart_path.exists()

    expected_labels = (summary_df["category_type"] + ": " + summary_df["category"].astype(str)).tolist()

    expected_counts = (summary_df["count"].tolist())

    assert captured_chart_data["labels"] == expected_labels

    assert captured_chart_data["counts"] == expected_counts

def test_summary_saved_and_chart_generated_from_same_summary(monkeypatch, tmp_path):

    reports_dir = (tmp_path / "reports")

    charts_dir = (reports_dir / "charts")

    monkeypatch.setattr("app.reporting.analytics.settings.reports_dir", reports_dir)

    monkeypatch.setattr("app.reporting.analytics.settings.charts_dir", charts_dir)

    comparison_df = (build_final_reconciliation_result())

    summary_df = generate_summary(comparison_df)

    save_summary(summary_df)

    generate_chart(summary_df)

    saved_summary = pd.read_csv(reports_dir / "summary.csv")

    assert saved_summary.to_dict("records") == summary_df.to_dict("records")

    assert (charts_dir / "reconciliation_summary.png").exists()

def test_final_result_transaction_ids_are_not_lost_from_analytics_input():

    comparison_df = (build_final_reconciliation_result())

    summary_df = generate_summary(comparison_df)

    expected_transaction_ids = {101, 102, 103, 104, 105}

    assert set(comparison_df["transaction_id"]) == expected_transaction_ids

    # Analytics summarises the supplied final result; it does not reconstruct or retrieve another dataset.
    assert (summary_df[summary_df["category_type"] == "status"]["count"].sum() == len(comparison_df))