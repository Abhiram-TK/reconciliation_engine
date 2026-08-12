import pandas as pd

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

    def get_sales_records(self):

        return pd.DataFrame([
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

    def get_inventory_records(self):

        return pd.DataFrame([
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

class FakeReportGenerator:

    def __init__(self):

        self.called = False
        self.results = None
        self.run_metadata = None

    def generate_reports(self, results, run_metadata):

        self.called = True
        self.results = results
        self.run_metadata = run_metadata

def test_reconciliation_service_complete_step_2_pipeline(monkeypatch):

    sales_client = FakeSalesClient()
    inventory_client = FakeInventoryClient()
    report_generator = FakeReportGenerator()

    service = ReconciliationService(sales_client=sales_client, inventory_client=inventory_client, report_generator=report_generator)

    # --------------------
    # Track normalization
    # --------------------

    import app.services.reconciliation_service as reconciliation_module

    real_normalize_dataframe = (reconciliation_module.normalize_dataframe)

    normalization_calls = []

    def tracked_normalize_dataframe(dataframe):

        normalization_calls.append(dataframe.copy())

        return real_normalize_dataframe(dataframe)

    monkeypatch.setattr(reconciliation_module, "normalize_dataframe", tracked_normalize_dataframe,)

    # ------------------------
    # Capture analytics input
    # ------------------------

    analytics_inputs = []

    def fake_generate_summary(comparison_df,):

        analytics_inputs.append(comparison_df.copy())

        status_counts = (comparison_df["status"]
                         .value_counts()
                         .rename_axis("category")
                         .reset_index(name="count"))

        status_counts.insert(0, "category_type", "status")

        return status_counts[["category_type", "category", "count"]]

    monkeypatch.setattr(reconciliation_module, "generate_summary", fake_generate_summary)

    monkeypatch.setattr(reconciliation_module, "save_summary", lambda summary_df: None)

    monkeypatch.setattr(reconciliation_module, "generate_chart", lambda summary_df: None)

    # ----------------------------------
    # Execute complete service pipeline
    # ----------------------------------

    output = service.run()

    # ------------------
    # 1. Run provenance
    # ------------------

    run_metadata = output["run_metadata"]

    assert run_metadata["source_system"] == ("Project 3 — Sales Transaction Service")

    assert run_metadata["target_system"] == ("Project 2 — Inventory Dispatch System")

    assert run_metadata["source_record_count"] == len(output["source_df"])

    assert run_metadata["target_record_count"] == len(output["target_df"])

    assert run_metadata["comparison_key"] == "transaction_id"

    assert run_metadata["source_fields"] == ["transaction_id",
                                             "invoice_number",
                                             "product_id",
                                             "quantity",
                                             "status",
                                             "created_at"]

    assert run_metadata["target_fields"] == ["transaction_id",
                                             "reservation_id",
                                             "batch_id",
                                             "reserved_quantity",
                                             "status",
                                             "reserved_at"]

    assert run_metadata["source_endpoint"] == "/internal/transactions"

    assert run_metadata["target_endpoint"] == ("/reservations/reconciliation")

    # ------------------------
    # 2. Dependency injection
    # ------------------------

    assert service.sales_client is sales_client
    assert service.inventory_client is inventory_client
    assert service.report_generator is report_generator

    # -------------
    # 3. Retrieval
    # -------------

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

    # -----------------------------------
    # 4. Normalization actually occurred
    # -----------------------------------

    assert len(normalization_calls) == 2

    normalized_sales = normalization_calls[0]
    normalized_inventory = normalization_calls[1]

    assert pd.api.types.is_integer_dtype(normalized_sales["transaction_id"])

    assert pd.api.types.is_integer_dtype(normalized_inventory["transaction_id"])

    assert pd.api.types.is_numeric_dtype(normalized_sales["quantity"])

    assert pd.api.types.is_numeric_dtype(normalized_inventory["reserved_quantity"])

    assert (normalized_sales["status"].iloc[0] == "VALIDATED")

    assert (normalized_inventory["status"].iloc[0] == "RESERVED")

    assert pd.api.types.is_datetime64_any_dtype(normalized_sales["created_at"])

    assert pd.api.types.is_datetime64_any_dtype(normalized_inventory["reserved_at"])

    # -----------------------------------------------
    # 5. Authoritative cross-service transaction IDs
    # -----------------------------------------------

    assert set(output["source_df"]["transaction_id"]) == {101, 102, 103, 104}

    assert set(output["target_df"]["transaction_id"]) == {101, 102, 103, 105}

    # ----------------------------------------
    # 6. Detailed mismatch detection occurred
    # ----------------------------------------

    mismatches = output["mismatches"]

    mismatch_types = {mismatch["mismatch_type"] for mismatch in mismatches}

    assert mismatch_types == {"QUANTITY_MISMATCH",
                              "DUPLICATE_RESERVATION",
                              "MISSING_RESERVATION",
                              "ORPHAN_RESERVATION"}

    # ----------------------------
    # 7. Verify quantity mismatch
    # ----------------------------

    quantity_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 102]

    assert len(quantity_mismatches) == 1

    assert (quantity_mismatches[0]["mismatch_type"] == "QUANTITY_MISMATCH")

    assert quantity_mismatches[0]["sales_quantity"] == 10

    assert quantity_mismatches[0]["reserved_quantity"] == 7

    # ------------------------------
    # 8. Verify duplicate detection
    # ------------------------------

    duplicate_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 103]

    assert len(duplicate_mismatches) == 1

    duplicate = duplicate_mismatches[0]

    assert duplicate["mismatch_type"] == "DUPLICATE_RESERVATION"

    assert duplicate["reservation_count"] == 2

    assert duplicate["reservation_ids"] == [503, 504]

    assert duplicate["reserved_quantities"] == [3, 2]

    # Duplicate condition must not produce a second quantity mismatch for transaction 103.
    assert not any(mismatch["transaction_id"] == 103 and mismatch["mismatch_type"] == "QUANTITY_MISMATCH" for mismatch in mismatches)

    # ------------------------------
    # 9. Verify missing reservation
    # ------------------------------

    missing_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 104]

    assert len(missing_mismatches) == 1

    assert missing_mismatches[0]["mismatch_type"] == "MISSING_RESERVATION"

    assert missing_mismatches[0]["sales_quantity"] == 3

    assert missing_mismatches[0]["reserved_quantity"] is None

    # -----------------------------
    # 10. Verify orphan reservation
    # -----------------------------

    orphan_mismatches = [mismatch for mismatch in mismatches if mismatch["transaction_id"] == 105]

    assert len(orphan_mismatches) == 1

    assert orphan_mismatches[0]["mismatch_type"] == "ORPHAN_RESERVATION"

    assert orphan_mismatches[0]["reserved_quantity"] == 6

    # -----------------------------------------------------
    # 11. ReportGenerator received FINAL reconciled output
    # -----------------------------------------------------

    assert report_generator.called is True

    assert report_generator.run_metadata == run_metadata

    reported_results = (report_generator.results)

    assert reported_results is not None

    assert (reported_results == output["comparison_results"])

    # The report generator must receive the enriched result, not merely the original simplified comparison records.
    reported_by_transaction = {result["transaction_id"]: result for result in reported_results}

    assert reported_by_transaction[101]["status"] == "MATCHED"

    assert reported_by_transaction[102]["mismatch_type"] == "QUANTITY_MISMATCH"

    assert reported_by_transaction[103]["mismatch_type"] == "DUPLICATE_RESERVATION"

    assert reported_by_transaction[104]["mismatch_type"] == "MISSING_RESERVATION"

    assert reported_by_transaction[105]["mismatch_type"] == "ORPHAN_RESERVATION"

    # --------------------------------------------------------
    # 12. Final result contains all five reconciliation cases
    # --------------------------------------------------------

    final_results = output[ "comparison_results"]

    assert len(final_results) == 5

    final_by_transaction = {result["transaction_id"]: result for result in final_results}

    assert set(final_by_transaction.keys()) == {101, 102, 103, 104, 105}

    assert final_by_transaction[101]["status"] == "MATCHED"

    assert final_by_transaction[102]["status"] == "MISMATCHED"

    assert final_by_transaction[103]["status"] == "MISMATCHED"

    assert final_by_transaction[104]["status"] == "MISSING"

    assert final_by_transaction[105]["status"] == "MISMATCHED"

    # ---------------------------------------------
    # 13. Analytics received the SAME final result
    # ---------------------------------------------

    assert len(analytics_inputs) == 1

    analytics_input = (analytics_inputs[0])

    assert len(analytics_input) == len(final_results)

    analytics_by_transaction = {row["transaction_id"]: row for _, row in analytics_input.iterrows()}

    assert set(analytics_by_transaction.keys()) == {101, 102, 103, 104, 105}

    # Analytics must see the detailed mismatch fields.
    assert (analytics_input["mismatch_type"].notna().sum() == 4)

    # ---------------------------------------------------
    # 14. Summary reflects final reconciliation statuses
    # ---------------------------------------------------

    summary_df = output["summary_df"]

    status_counts = dict(zip(summary_df["category"], summary_df["count"]))

    assert status_counts["MATCHED"] == 1

    assert status_counts["MISMATCHED"] == 3

    assert status_counts["MISSING"] == 1

    # The primary status counts must reconcile exactly to the five final result records.
    assert sum(status_counts.values()) == len(final_results)