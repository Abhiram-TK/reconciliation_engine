from app.dependencies.providers import get_reconciliation_service

def main() -> None:

    service = get_reconciliation_service()

    result = service.run()

    print("\n==============================================")
    print("RECONCILIATION EXECUTION COMPLETED")
    print("==============================================")

    if isinstance(result, dict):

        run_metadata = result.get("run_metadata", {})

        if run_metadata:

            print(f"Run ID: {run_metadata.get('run_id', 'N/A')}")
            print(f"Execution time: "
                  f"{run_metadata.get('execution_time', 'N/A')}")

            print(f"Source: "
                  f"{run_metadata.get('source_system', 'N/A')}")

            print(f"Target: "
                  f"{run_metadata.get('target_system', 'N/A')}")

            print(f"Comparison key: "
                  f"{run_metadata.get('comparison_key', 'N/A')}")

            print(f"Sales records: "
                  f"{run_metadata.get('source_record_count', 'N/A')}")

            print(f"Inventory records: "
                  f"{run_metadata.get('target_record_count', 'N/A')}")

    print("==============================================")
    print("Reports and analytics generated successfully.")
    print("==============================================\n")

if __name__ == "__main__":
    main()