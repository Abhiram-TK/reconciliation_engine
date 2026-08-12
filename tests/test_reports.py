import json

import pandas as pd

from app.reporting.report_generator import ReportGenerator

def build_reconciliation_results():

    return [
        # ---------------
        # 1. Exact match
        # ---------------
        {"transaction_id": 101,
         "invoice_number": "INV-2026-000101",
         "status": "MATCHED",
         "mismatch_type": None,
         "quantity": 5,
         "reserved_quantity": 5,
         "reservation_count": 1,
         "reservation_id": 501,
         "batch_id": 20,
         "reservation_ids": [501],
         "batch_ids": [20],
         "reserved_quantities": [5],
         "reservation_statuses": ["RESERVED"],
         "reservation_timestamps": ["2026-08-08T09:01:00Z"],
         "reservations": [{"reservation_id": 501,
                           "batch_id": 20,
                           "reserved_quantity": 5,
                           "status": "RESERVED",
                           "reserved_at": "2026-08-08T09:01:00Z"}]},

        # ---------------------
        # 2. Quantity mismatch
        # ---------------------
        {"transaction_id": 102,
         "invoice_number": "INV-2026-000102",
         "status": "MISMATCHED",
         "mismatch_type": "QUANTITY_MISMATCH",
         "quantity": 10,
         "reserved_quantity": 7,
         "reservation_count": 1,
         "reservation_id": 502,
         "batch_id": 21,
         "reservation_ids": [502],
         "batch_ids": [21],
         "reserved_quantities": [7],
         "reservation_statuses": ["RESERVED"],
         "reservation_timestamps": ["2026-08-08T10:01:00Z"],
         "details": ("Sales transaction quantity does not match Inventory reserved quantity"),
         "reservations": [{"reservation_id": 502,
                           "batch_id": 21,
                           "reserved_quantity": 7,
                           "status": "RESERVED",
                           "reserved_at": "2026-08-08T10:01:00Z"}]},

        # -------------------------
        # 3. Duplicate reservation
        # -------------------------
        {"transaction_id": 103,
         "invoice_number": "INV-2026-000103",
         "status": "MISMATCHED",
         "mismatch_type": "DUPLICATE_RESERVATION",
         "quantity": 5,
         "reserved_quantity": 5,
         "reservation_count": 2,
         "reservation_id": None,
         "batch_id": None,
         "reservation_ids": [503, 504],
         "batch_ids": [22, 23],
         "reserved_quantities": [3, 2],
         "reservation_statuses": ["RESERVED", "RESERVED",],
         "reservation_timestamps": ["2026-08-08T11:01:00Z", "2026-08-08T11:02:00Z"],
         "details": ("Multiple Inventory reservations exist for the same transaction"),
         "reservations": [
                {
                    "reservation_id": 503,
                    "batch_id": 22,
                    "reserved_quantity": 3,
                    "status": "RESERVED",
                    "reserved_at": "2026-08-08T11:01:00Z"
                },
                {
                    "reservation_id": 504,
                    "batch_id": 23,
                    "reserved_quantity": 2,
                    "status": "RESERVED",
                    "reserved_at": "2026-08-08T11:02:00Z"}]},

        # ---------------------------------
        # 4. Missing Inventory reservation
        # ---------------------------------
        {"transaction_id": 104,
         "invoice_number": "INV-2026-000104",
         "status": "MISSING",
         "mismatch_type": "MISSING_RESERVATION",
         "quantity": 3,
         "reserved_quantity": None,
         "reservation_count": 0,
         "reservation_id": None,
         "batch_id": None,
         "reservation_ids": [],
         "batch_ids": [],
         "reserved_quantities": [],
         "reservation_statuses": [],
         "reservation_timestamps": [],
         "details": ("Sales transaction has no corresponding Inventory reservation"),
         "reservations": []},

        # --------------------------------
        # 5. Orphan Inventory reservation
        # --------------------------------
        {"transaction_id": 105,
         "invoice_number": None,
         "status": "MISMATCHED",
         "mismatch_type": "ORPHAN_RESERVATION",
         "quantity": None,
         "reserved_quantity": 6,
         "reservation_count": 1,
         "reservation_id": 505,
         "batch_id": 24,
         "reservation_ids": [505],
         "batch_ids": [24],
         "reserved_quantities": [6],
         "reservation_statuses": ["RESERVED"],
         "reservation_timestamps": ["2026-08-08T13:01:00Z"],
         "details": ("Inventory reservation references a transaction that does not exist in Sales"),
         "reservations": [{"reservation_id": 505,
                           "batch_id": 24,
                           "reserved_quantity": 6,
                           "status": "RESERVED",
                           "reserved_at": "2026-08-08T13:01:00Z"}]}]

def build_run_metadata():

    return {"run_id": "test-run-001",
            "execution_time": "2026-08-12T11:00:00",
            "source_system": "Project 3 — Sales Transaction Service",
            "source_endpoint": "/internal/transactions",
            "source_record_count": 5,
            "source_fields": ["transaction_id",
                              "invoice_number",
                              "product_id",
                              "quantity",
                              "status",
                              "created_at"],
            "target_system": "Project 2 — Inventory Dispatch System",
            "target_endpoint": "/reservations/reconciliation",
            "target_record_count": 5,
            "target_fields": ["transaction_id",
                              "reservation_id",
                              "batch_id",
                              "reserved_quantity",
                              "status",
                              "reserved_at"],
            "comparison_key": "transaction_id"}

def test_generate_reports_preserves_all_report_files(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    matched_path = (tmp_path / "matched.csv")

    mismatched_path = (tmp_path / "mismatched.csv")

    missing_path = (tmp_path / "missing.csv")

    assert matched_path.exists()
    assert mismatched_path.exists()
    assert missing_path.exists()

def test_generate_reports_total_rows_equal_input_results(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    matched_df = pd.read_csv(tmp_path / "matched.csv")

    mismatched_df = pd.read_csv(tmp_path / "mismatched.csv")

    missing_df = pd.read_csv(tmp_path / "missing.csv")

    total_reported_rows = (len(matched_df) + len(mismatched_df) + len(missing_df))

    assert total_reported_rows == len(results)

def test_generate_reports_classifies_detailed_mismatch_types(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    matched_df = pd.read_csv(tmp_path / "matched.csv")

    mismatched_df = pd.read_csv(tmp_path / "mismatched.csv")

    missing_df = pd.read_csv(tmp_path / "missing.csv")

    assert set(matched_df["transaction_id"]) == {101}

    assert set(mismatched_df["transaction_id"]) == {102, 103, 105}

    assert set(mismatched_df["mismatch_type"]) == {"QUANTITY_MISMATCH",
                                                   "DUPLICATE_RESERVATION",
                                                   "ORPHAN_RESERVATION"}

    assert set(missing_df["transaction_id"]) == {104}

    assert set(missing_df["mismatch_type"]) == {"MISSING_RESERVATION"}

def test_quantity_mismatch_details_survive_csv_generation(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    mismatched_df = pd.read_csv(tmp_path / "mismatched.csv")

    row = mismatched_df[mismatched_df["transaction_id"] == 102].iloc[0]

    assert row["mismatch_type"] == ("QUANTITY_MISMATCH")

    assert row["quantity"] == 10
    assert row["reserved_quantity"] == 7

    assert row["reservation_count"] == 1
    assert row["reservation_id"] == 502
    assert row["batch_id"] == 21

    assert json.loads(row["reservation_ids"]) == [502]

    assert json.loads(row["batch_ids"]) == [21]

    assert json.loads(row["reserved_quantities"]) == [7]

def test_duplicate_reservation_details_survive_csv_generation(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    mismatched_df = pd.read_csv(tmp_path / "mismatched.csv")

    row = mismatched_df[mismatched_df["transaction_id"] == 103].iloc[0]

    assert row["mismatch_type"] == ("DUPLICATE_RESERVATION")

    assert row["reservation_count"] == 2

    # No arbitrary reservation should become the primary reservation for a duplicate condition.
    assert pd.isna(row["reservation_id"])

    assert pd.isna(row["batch_id"])

    assert json.loads(row["reservation_ids"]) == [503, 504]

    assert json.loads(row["batch_ids"]) == [22, 23]

    assert json.loads(row["reserved_quantities"]) == [3, 2]

    reservations = json.loads(row["reservations"])

    assert len(reservations) == 2

    assert reservations[0]["reservation_id"] == 503

    assert reservations[1]["reservation_id"] == 504

def test_missing_reservation_details_survive_csv_generation(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    missing_df = pd.read_csv(tmp_path / "missing.csv")

    row = missing_df[missing_df["transaction_id"] == 104].iloc[0]

    assert row["mismatch_type"] == ("MISSING_RESERVATION")

    assert row["quantity"] == 3
    assert pd.isna(row["reserved_quantity"])

    assert row["reservation_count"] == 0

    assert pd.isna(row["reservation_id"])

    assert pd.isna(row["batch_id"])

    assert json.loads(row["reservation_ids"]) == []

    assert json.loads(row["batch_ids"]) == []

    assert json.loads(row["reserved_quantities"]) == []

def test_orphan_reservation_details_survive_csv_generation(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    mismatched_df = pd.read_csv(tmp_path / "mismatched.csv")

    row = mismatched_df[mismatched_df["transaction_id"] == 105].iloc[0]

    assert row["mismatch_type"] == ("ORPHAN_RESERVATION")

    assert pd.isna(row["invoice_number"])

    assert pd.isna(row["quantity"])

    assert row["reserved_quantity"] == 6
    assert row["reservation_count"] == 1

    assert row["reservation_id"] == 505
    assert row["batch_id"] == 24

    assert json.loads(row["reservation_ids"]) == [505]

    assert json.loads(row["batch_ids"]) == [24]

    assert json.loads(row["reserved_quantities"]) == [6]

def test_generate_reports_preserves_nested_reservation_objects(tmp_path, monkeypatch,):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_pat)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    mismatched_df = pd.read_csv(tmp_path / "mismatched.csv")

    duplicate_row = mismatched_df[mismatched_df["transaction_id"] == 103].iloc[0]

    reservations = json.loads(duplicate_row["reservations"])

    assert reservations == [
        {
            "reservation_id": 503,
            "batch_id": 22,
            "reserved_quantity": 3,
            "status": "RESERVED",
            "reserved_at": ("2026-08-08T11:01:00Z")
        },
        {
            "reservation_id": 504,
            "batch_id": 23,
            "reserved_quantity": 2,
            "status": "RESERVED",
            "reserved_at": ("2026-08-08T11:02:00Z")}]

def test_generate_reports_preserves_one_row_per_final_result(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    generator.generate_reports(results)

    all_reported_ids = []

    for filename in ["matched.csv", "mismatched.csv", "missing.csv"]: 

        dataframe = pd.read_csv(tmp_path / filename)

        all_reported_ids.extend(dataframe["transaction_id"].tolist())

    assert len(all_reported_ids) == len(results)

    assert set(all_reported_ids) == {101, 102, 103, 104, 105}

    assert len(all_reported_ids) == len(set(all_reported_ids))

def test_generate_reports_preserves_upstream_provenance(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    run_metadata = build_run_metadata()

    generator.generate_reports(results, run_metadata)

    matched_df = pd.read_csv(tmp_path / "matched.csv")
    mismatched_df = pd.read_csv(tmp_path / "mismatched.csv")
    missing_df = pd.read_csv(tmp_path / "missing.csv")

    for dataframe in [matched_df, mismatched_df, missing_df]:

        assert (dataframe["source_system"].eq("Project 3 — Sales Transaction Service").all())

        assert (dataframe["target_system"].eq("Project 2 — Inventory Dispatch System").all())

        assert dataframe["comparison_key"].eq("transaction_id").all()

def test_generate_reports_preserves_reconciliation_semantics(tmp_path, monkeypatch):

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", tmp_path)

    generator = ReportGenerator()

    results = build_reconciliation_results()

    run_metadata = build_run_metadata()

    generator.generate_reports(results, run_metadata)

    matched_df = pd.read_csv(tmp_path / "matched.csv")
    mismatched_df = pd.read_csv(tmp_path / "mismatched.csv")
    missing_df = pd.read_csv(tmp_path / "missing.csv")

    assert set(matched_df["status"]) == {"MATCHED"}

    assert set(mismatched_df["status"]) == {"MISMATCHED"}

    assert set(mismatched_df["mismatch_type"]) == {"QUANTITY_MISMATCH",
                                                   "DUPLICATE_RESERVATION",
                                                   "ORPHAN_RESERVATION"}

    assert set(missing_df["status"]) == {"MISSING"}

    assert set(missing_df["mismatch_type"]) == {"MISSING_RESERVATION"}