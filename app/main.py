from app.services.reconciliation_service import ReconciliationService

def main() -> None:
  
    service = ReconciliationService()

    service.run()

if __name__ == "__main__":
    main()