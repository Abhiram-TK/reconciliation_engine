import pandas as pd

from app.services.reconciliation_service import ReconciliationService

class FakeSalesClient:

    def get_sales_records(self):

        return pd.DataFrame([{"invoice_id": "INV001",
                              "customer_name": "Abhiram",
                              "invoice_date": "01/01/2026",
                              "amount": 100.0}])

class FakeInventoryClient:

    def get_inventory_records(self):

        return pd.DataFrame([{"invoice_id": "INV001",
                              "customer_name": "Abhiram",
                              "invoice_date": "01/01/2026",
                              "amount": 100.0}])

class FakeReportGenerator:

    def __init__(self):

        self.called = False
        self.results = None

    def generate_reports(self, results):

        self.called = True
        self.results = results

def test_reconciliation_service_with_injected_dependencies():

    sales_client = FakeSalesClient()
    inventory_client = FakeInventoryClient()
    report_generator = FakeReportGenerator()

    service = ReconciliationService(sales_client=sales_client, inventory_client=inventory_client, report_generator=report_generator)

    output = service.run()

    assert output["source_df"] is not None
    assert output["target_df"] is not None

    assert len(output["comparison_results"]) == 1

    assert report_generator.called is True
    assert report_generator.results == output["comparison_results"]