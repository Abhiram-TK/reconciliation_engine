from app.clients.inventory_client import InventoryClient
from app.clients.sales_client import SalesClient

from app.reporting.report_generator import ReportGenerator

from app.services.reconciliation_service import ReconciliationService

def get_sales_client() -> SalesClient:

    return SalesClient()

def get_inventory_client() -> InventoryClient:

    return InventoryClient()

def get_report_generator() -> ReportGenerator:

    return ReportGenerator()

def get_reconciliation_service() -> ReconciliationService:

    return ReconciliationService(sales_client=get_sales_client(),
                                 inventory_client=get_inventory_client(),
                                 report_generator=get_report_generator())