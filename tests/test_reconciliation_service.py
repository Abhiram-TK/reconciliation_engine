import pandas as pd

from app.services.reconciliation_service import ReconciliationService

class FakeSalesClient:

    def get_sales_records(self):

        return pd.DataFrame([{"transaction_id": 101,
                              "invoice_number": "INV-2026-000101",
                              "product_id": 10,
                              "quantity": 5,
                              "status": "VALIDATED",
                              "created_at": pd.Timestamp("2026-08-08T09:00:00Z")}])

class FakeInventoryClient:

    def get_inventory_records(self):

        return pd.DataFrame([{"transaction_id": 101,
                              "reservation_id": 501,
                              "batch_id": 20,
                              "reserved_quantity": 5,
                              "status": "RESERVED",
                              "reserved_at": pd.Timestamp("2026-08-08T09:01:00Z")}])

class FakeReportGenerator:

    def __init__(self):

        self.called = False
        self.results = None

    def generate_reports(self, results):

        self.called = True
        self.results = results

def test_reconciliation_service_with_injected_dependencies(monkeypatch):

    sales_client = FakeSalesClient()
    inventory_client = FakeInventoryClient()
    report_generator = FakeReportGenerator()

    service = ReconciliationService(sales_client=sales_client, inventory_client=inventory_client, report_generator=report_generator)

    # Prevent this unit test from writing report files or charts.
    monkeypatch.setattr("app.services.reconciliation_service.generate_summary",
                        lambda comparison_df: pd.DataFrame({"Status": ["MATCHED"], "Count": [1]}))

    monkeypatch.setattr("app.services.reconciliation_service.save_summary",
                        lambda summary_df: None)

    monkeypatch.setattr("app.services.reconciliation_service.generate_chart",
                        lambda summary_df: None,)

    output = service.run()

    # Dependency injection remains intact.
    assert service.sales_client is sales_client
    assert service.inventory_client is inventory_client
    assert service.report_generator is report_generator

    # Sales contract.
    assert list(output["source_df"].columns) == ["transaction_id",
                                                 "invoice_number",
                                                 "product_id",
                                                 "quantity",
                                                 "status",
                                                 "created_at"]

    # Inventory contract.
    assert list(output["target_df"].columns) == ["transaction_id",
                                                 "reservation_id"
                                                 "batch_id",
                                                 "reserved_quantity",
                                                 "status",
                                                 "reserved_at"]

    # Authoritative cross-service key.
    assert output["source_df"].iloc[0]["transaction_id"] == 101
    assert output["target_df"].iloc[0]["transaction_id"] == 101

    # Quantity reconciliation.
    assert output["source_df"].iloc[0]["quantity"] == 5
    assert output["target_df"].iloc[0]["reserved_quantity"] == 5

    # Comparison result.
    assert len(output["comparison_results"]) == 1

    assert output["comparison_results"][0]["transaction_id"] == 101
    assert output["comparison_results"][0]["status"] == "MATCHED"

    # Report generator received the same comparison result.
    assert report_generator.called is True
    assert report_generator.results == output["comparison_results"]

    # Analytics output exists.
    assert output["summary_df"] is not None
    assert output["summary_df"].iloc[0]["Status"] == "MATCHED"
    assert output["summary_df"].iloc[0]["Count"] == 1