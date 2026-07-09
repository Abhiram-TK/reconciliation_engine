from app.dependencies.providers import get_reconciliation_service

def main() -> None:
    
    service = get_reconciliation_service()
    service.run()

if __name__ == "__main__":
    main()