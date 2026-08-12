import pandas as pd

from app.reporting.report_generator import ReportGenerator
from app.services.reconciliation_service import ReconciliationService

class FakeSalesClient:

    def __init__(self):

        self.retrieval_metadata = {"source_system": "Project 3 — Sales Transaction Service",
                                   "endpoint": "/internal/transactions",
                                   "record_count": 4,
                                   "fields": ["transaction_id",
                                              "invoice_number",
                                              "product_id",
                                              "quantity",
                                              "status",
                                              "created_at"]}

        self.data = pd.DataFrame([
            {
                "transaction_id": "101",
                "invoice_number": "INV-2026-000101",
                "product_id": "10",
                "quantity": "5",
                "status": "validated",
                "created_at": "2026-08-08T09:00:00Z"
            },
            {
                "transaction_id": "102",
                "invoice_number": "INV-2026-000102",
                "product_id": "11",
                "quantity": "10",
                "status": "completed",
                "created_at": "2026-08-08T10:00:00Z"
            },
            {
                "transaction_id": "103",
                "invoice_number": "INV-2026-000103",
                "product_id": "12",
                "quantity": "5",
                "status": "validated",
                "created_at": "2026-08-08T11:00:00Z"
            },
            {
                "transaction_id": "104",
                "invoice_number": "INV-2026-000104",
                "product_id": "13",
                "quantity": "3",
                "status": "validated",
                "created_at": "2026-08-08T12:00:00Z"
            }])

    def get_sales_records(self):

        return self.data.copy(deep=True)

class FakeInventoryClient:

    def __init__(self):

        self.retrieval_metadata = {"source_system": "Project 2 — Inventory Dispatch System",
                                   "endpoint": "/reservations/reconciliation",
                                   "authentication": "X-Internal-Service-Token",
                                   "record_count": 5,
                                   "fields": ["transaction_id",
                                              "reservation_id",
                                              "batch_id",
                                              "reserved_quantity",
                                              "status",
                                              "reserved_at"]}

        self.data = pd.DataFrame([
            # 101 — exact match
            {
                "transaction_id": "101",
                "reservation_id": "501",
                "batch_id": "20",
                "reserved_quantity": "5",
                "status": "reserved",
                "reserved_at": "2026-08-08T09:01:00Z"
            },
            # 102 — quantity mismatch
            {
                "transaction_id": "102",
                "reservation_id": "502",
                "batch_id": "21",
                "reserved_quantity": "7",
                "status": "reserved",
                "reserved_at": "2026-08-08T10:01:00Z"
            },
            # 103 — duplicate reservations
            {
                "transaction_id": "103",
                "reservation_id": "503",
                "batch_id": "22",
                "reserved_quantity": "3",
                "status": "reserved",
                "reserved_at": "2026-08-08T11:01:00Z"
            },
            {
                "transaction_id": "103",
                "reservation_id": "504",
                "batch_id": "23",
                "reserved_quantity": "2",
                "status": "reserved",
                "reserved_at": "2026-08-08T11:02:00Z"
            },
            # 105 — orphan Inventory reservation
            # No corresponding Sales transaction exists.
            {
                "transaction_id": "105",
                "reservation_id": "505",
                "batch_id": "24",
                "reserved_quantity": "6",
                "status": "reserved",
                "reserved_at": "2026-08-08T13:01:00Z"
            }])

    def get_inventory_records(self):

        return self.data.copy(deep=True)

def test_reconciliation_service_complete_independent_pipeline(monkeypatch, tmp_path):

    sales_client = FakeSalesClient()
    inventory_client = FakeInventoryClient()

    # Use the real production ReportGenerator.
    # This keeps the independent test completely local while still exercising the real reporting stage.
    report_generator = ReportGenerator()

    service = ReconciliationService(sales_client=sales_client,
                                    inventory_client=inventory_client,
                                    report_generator=report_generator)

    # -----------------------------------------------------------------------------------------------------------------------
    # Redirect all generated reports/charts to pytest's temporary directory so this independent test does not modify the real
    # Project 4 reports directory.
    # -----------------------------------------------------------------------------------------------------------------------

    reports_dir = tmp_path / "reports"
    charts_dir = reports_dir / "charts"

    monkeypatch.setattr("app.reporting.report_generator.settings.reports_dir", reports_dir)

    monkeypatch.setattr("app.reporting.analytics.settings.reports_dir", reports_dir)

    monkeypatch.setattr("app.reporting.analytics.settings.charts_dir", charts_dir)

    # --------------------
    # Track normalization
    # --------------------

    import app.services.reconciliation_service as reconciliation_module

    real_normalize_dataframe = (reconciliation_module.normalize_dataframe)

    normalization_calls = []

    def tracked_normalize_dataframe(dataframe):

        normalization_calls.append(dataframe.copy(deep=True))

        return real_normalize_dataframe(dataframe)

    monkeypatch.setattr(reconciliation_module,
                        "normalize_dataframe",
                        tracked_normalize_dataframe)

    # -----------------------------------------------------------
    # Preserve original upstream fake data for non-mutation test
    # -----------------------------------------------------------

    original_sales_data = sales_client.data.copy(deep=True)

    original_inventory_data = inventory_client.data.copy(deep=True)

    # --------------------------------------------------
    # Execute the complete Project 4 pipeline.
    #
    # No Authentication Service.
    # No Inventory Service.
    # No Sales Transaction Service.
    # No HTTP communication.
    #
    # Only the injected fake upstream adapters are used.
    # --------------------------------------------------

    output = service.run()

    # ===============================
    # 1. Verify run-level provenance
    # ===============================

    run_metadata = output["run_metadata"]

    assert run_metadata["run_id"].startswith("REC-")

    assert run_metadata["execution_time"]

    source_metadata = run_metadata["source"]

    target_metadata = run_metadata["target"]

    reconciliation_metadata = run_metadata["reconciliation"]

    assert source_metadata["project"] == ("Project 3 — Sales Transaction Service")

    assert source_metadata["service"] == ("Sales Transaction Service")

    assert source_metadata["endpoint"] == ("/internal/transactions")

    assert source_metadata["records_retrieved"] == 4

    assert source_metadata["fields"] == ["transaction_id",
                                         "invoice_number",
                                         "product_id",
                                         "quantity",
                                         "status",
                                         "created_at"]

    assert target_metadata["project"] == ("Project 2 — Inventory Dispatch System")

    assert target_metadata["service"] == ("Inventory Dispatch System")

    assert target_metadata["endpoint"] == ("/reservations/reconciliation")

    assert target_metadata["records_retrieved"] == 5

    assert target_metadata["fields"] == ["transaction_id",
                                         "reservation_id",
                                         "batch_id",
                                         "reserved_quantity",
                                         "status",
                                         "reserved_at"]

    assert reconciliation_metadata["comparison_key"] == ("transaction_id")

    assert reconciliation_metadata["source_system"] == ("Project 3 — Sales Transaction Service")

    assert reconciliation_metadata["target_system"] == ("Project 2 — Inventory Dispatch System")

    # ===============================
    # 2. Verify dependency injection
    # ===============================

    assert service.sales_client is sales_client

    assert service.inventory_client is inventory_client

    assert service.report_generator is report_generator

    # ======================================================
    # 3. Verify fake-client retrieval metadata is preserved
    # ======================================================

    assert sales_client.retrieval_metadata["source_system"] == ("Project 3 — Sales Transaction Service")

    assert sales_client.retrieval_metadata["endpoint"] == ("/internal/transactions")

    assert sales_client.retrieval_metadata["record_count"] == 4

    assert inventory_client.retrieval_metadata["source_system"] == ("Project 2 — Inventory Dispatch System")

    assert inventory_client.retrieval_metadata["endpoint"] == ("/reservations/reconciliation")

    assert inventory_client.retrieval_metadata["authentication"] == ("X-Internal-Service-Token")

    assert inventory_client.retrieval_metadata["record_count"] == 5

    # ======================================================
    # 4. Verify upstream-shaped data was actually retrieved
    # ======================================================

    assert len(output["source_df"]) == 4

    assert len(output["target_df"]) == 5

    assert list(output["source_df"].columns) == ["transaction_id",
                                                 "invoice_number",
                                                 "product_id",
                                                 "quantity",
                                                 "status",
                                                 "created_at"]

    assert list(output["target_df"].columns) == ["transaction_id",
                                                 "reservation_id",
                                                 "batch_id",
                                                 "reserved_quantity",
                                                 "status",
                                                 "reserved_at"]

    # ==========================================
    # 5. Verify normalization actually occurred
    # ==========================================

    assert len(normalization_calls) == 2

    normalized_sales = normalization_calls[0]

    normalized_inventory = normalization_calls[1]

    assert pd.api.types.is_integer_dtype(normalized_sales["transaction_id"])

    assert pd.api.types.is_integer_dtype(normalized_inventory["transaction_id"])

    assert pd.api.types.is_numeric_dtype(normalized_sales["quantity"])

    assert pd.api.types.is_numeric_dtype(normalized_inventory["reserved_quantity"])

    assert normalized_sales["status"].iloc[0] == "VALIDATED"

    assert normalized_inventory["status"].iloc[0] == "RESERVED"

    assert pd.api.types.is_datetime64_any_dtype(normalized_sales["created_at"])

    assert pd.api.types.is_datetime64_any_dtype(normalized_inventory["reserved_at"])

    # =======================================
    # 6. Verify authoritative comparison key
    # =======================================

    assert set(output["source_df"]["transaction_id"]) == {101, 102, 103, 104}

    assert set(output["target_df"]["transaction_id"]) == {101, 102, 103, 105}

    # =============================
    # 7. Verify mismatch detection
    # =============================

    mismatches = output["mismatches"]

    mismatch_types = {mismatch["mismatch_type"] for mismatch in mismatches}

    assert mismatch_types == {"QUANTITY_MISMATCH",
                              "DUPLICATE_RESERVATION",
                              "MISSING_RESERVATION",
                              "ORPHAN_RESERVATION"}

    # ============================
    # 8. Verify quantity mismatch
    # ============================

    quantity_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 102]

    assert len(quantity_mismatches) == 1

    quantity_mismatch = quantity_mismatches[0]

    assert quantity_mismatch["mismatch_type"] == ("QUANTITY_MISMATCH")

    assert quantity_mismatch["sales_quantity"] == 10

    assert quantity_mismatch["reserved_quantity"] == 7

    # ================================
    # 9. Verify duplicate reservation
    # ================================

    duplicate_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 103]

    assert len(duplicate_mismatches) == 1

    duplicate = duplicate_mismatches[0]

    assert duplicate["mismatch_type"] == ("DUPLICATE_RESERVATION")

    assert duplicate["reservation_count"] == 2

    assert duplicate["reservation_ids"] == [503, 504]

    assert duplicate["reserved_quantities"] == [3, 2]

    assert not any(mismatch["transaction_id"] == 103 and mismatch["mismatch_type"] == "QUANTITY_MISMATCH" for mismatch in mismatches)

    # ===============================
    # 10. Verify missing reservation
    # ===============================

    missing_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 104]

    assert len(missing_mismatches) == 1

    missing = missing_mismatches[0]

    assert missing["mismatch_type"] == ("MISSING_RESERVATION")

    assert missing["sales_quantity"] == 3

    assert missing["reserved_quantity"] is None

    # ==============================
    # 11. Verify orphan reservation
    # ==============================

    orphan_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 105]

    assert len(orphan_mismatches) == 1

    orphan = orphan_mismatches[0]

    assert orphan["mismatch_type"] == ("ORPHAN_RESERVATION")

    assert orphan["reserved_quantity"] == 6

    # ================================================
    # 12. Verify complete final reconciliation result
    # ================================================

    final_results = output["comparison_results"]

    assert len(final_results) == 5

    final_by_transaction = {result["transaction_id"]: result for result in final_results}

    assert set(final_by_transaction.keys()) == {101, 102, 103, 104, 105}

    assert final_by_transaction[101]["status"] == "MATCHED"

    assert final_by_transaction[102]["status"] == "MISMATCHED"

    assert final_by_transaction[103]["status"] == "MISMATCHED"

    assert final_by_transaction[104]["status"] == "MISSING"

    assert final_by_transaction[105]["status"] == "MISMATCHED"

    # ======================================
    # 13. Verify semantic comparison fields
    # ======================================

    for result in final_results:

        assert result["source_system"] == ("Project 3 — Sales Transaction Service")

        assert result["target_system"] == ("Project 2 — Inventory Dispatch System")

        assert result["comparison_key"] == "transaction_id"

        assert "sales_record_present" in result

        assert "inventory_record_present" in result

    # ==================================================================================================
    # 14. Verify actual report generation
    #
    # Real ReportGenerator is used.
    # Therefore this proves the service reaches the production reporting layer during an independent run.
    # ===================================================================================================

    assert (reports_dir / "matched.csv").exists()

    assert (reports_dir / "mismatched.csv").exists()

    assert (reports_dir / "missing.csv").exists()

    assert (reports_dir / "reconciliation_report.txt").exists()

    # ====================================
    # 15. Verify generated CSV provenance
    # ====================================

    matched_df = pd.read_csv(reports_dir / "matched.csv")

    mismatched_df = pd.read_csv(reports_dir / "mismatched.csv")

    missing_df = pd.read_csv(reports_dir / "missing.csv")

    for dataframe in [matched_df, mismatched_df, missing_df]:

        assert dataframe["source_system"].eq("Project 3 — Sales Transaction Service").all()

        assert dataframe["target_system"].eq("Project 2 — Inventory Dispatch System").all()

        assert dataframe["comparison_key"].eq("transaction_id").all()

        assert "status" in dataframe.columns

        assert "mismatch_type" in dataframe.columns

    # =======================================
    # 16. Verify CSV semantic classification
    # =======================================

    assert set(matched_df["status"]) == {"MATCHED"}

    assert set(mismatched_df["status"]) == {"MISMATCHED"}

    assert set(mismatched_df["mismatch_type"]) == {"QUANTITY_MISMATCH",
                                                   "DUPLICATE_RESERVATION",
                                                   "ORPHAN_RESERVATION"}

    assert set(missing_df["status"]) == {"MISSING"}

    assert set(missing_df["mismatch_type"]) == {"MISSING_RESERVATION"}

    # ======================================
    # 17. Verify reconciliation report text
    # ======================================

    report_text = (reports_dir / "reconciliation_report.txt").read_text(encoding="utf-8")

    assert "RECONCILIATION RUN" in report_text

    assert "SOURCE DATA" in report_text

    assert "TARGET DATA" in report_text

    assert "Project 3 — Sales Transaction Service" in report_text

    assert "Project 2 — Inventory Dispatch System" in report_text

    assert "/internal/transactions" in report_text

    assert "/reservations/reconciliation" in report_text

    assert "transaction_id" in report_text

    assert "MATCHED:" in report_text

    assert "MISMATCHED:" in report_text

    assert "MISSING:" in report_text

    assert "QUANTITY_MISMATCH:" in report_text

    assert "DUPLICATE_RESERVATION:" in report_text

    assert "MISSING_RESERVATION:" in report_text

    assert "ORPHAN_RESERVATION:" in report_text

    # ===================================
    # 18. Verify analytics was generated
    # ===================================

    assert "summary_df" in output

    summary_df = output["summary_df"]

    assert not summary_df.empty

    status_summary = summary_df[summary_df["category_type"] == "status"]

    status_counts = dict(zip(status_summary["category"], status_summary["count"]))

    assert status_counts["MATCHED"] == 1

    assert status_counts["MISMATCHED"] == 3

    assert status_counts["MISSING"] == 1

    assert status_summary["count"].sum() == 5

    assert (reports_dir / "summary.csv").exists()

    assert (charts_dir / "reconciliation_summary.png").exists()

    # =======================================================
    # 19. Verify supplied fake upstream data was NOT mutated
    # =======================================================

    pd.testing.assert_frame_equal(sales_client.data, original_sales_data)

    pd.testing.assert_frame_equal(inventory_client.data, original_inventory_data)