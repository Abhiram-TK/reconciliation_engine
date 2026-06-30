import random
import pandas as pd

from faker import Faker

from core.config import (SOURCE_FILE, TARGET_FILE, DATASET_SIZE, MISMATCH_RATE)

fake = Faker("en_IN")

def generate_dataset(records: int = 1000, mismatch_rate: float = 0.05):

    source = []
    target = []

    for i in range(1, records + 1):

        invoice_id = f"INV{i:06d}"

        customer_name = fake.name().upper()

        invoice_date = fake.date_between(start_date="-2y", end_date="today").strftime("%d/%m/%Y")

        amount = random.randint(500, 50000)

        source.append({"invoice_id": invoice_id, "customer_name": customer_name, "invoice_date": invoice_date, "amount": amount})

        target_invoice = invoice_id
        target_customer = customer_name
        target_date = invoice_date
        target_amount = amount

        if random.random() < mismatch_rate:

            mismatch = random.choice(["missing", "amount", "customer", "date"])

            if mismatch == "missing":
                continue

            elif mismatch == "amount":
                target_amount += random.randint(100, 1000)

            elif mismatch == "customer":
                target_customer = fake.name().upper()

            elif mismatch == "date":
                target_date = fake.date_between(start_date="-2y", end_date="today").strftime("%d/%m/%Y")

        target.append({"invoice_id": target_invoice, "customer_name": target_customer, "invoice_date": target_date, "amount": target_amount})

    source_df = pd.DataFrame(source)
    target_df = pd.DataFrame(target)

    SOURCE_FILE.parent.mkdir(parents=True, exist_ok=True)

    source_df.to_csv(SOURCE_FILE, index=False)

    target_df.to_csv(TARGET_FILE, index=False)

    print(f"Generated {len(source_df)} source records")
    print(f"Generated {len(target_df)} target records")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--records", type=int, default=None, help="Number of source records to generate")

    parser.add_argument("--mismatch-rate", type=float, default=None, help="Percentage of mismatched target records")

    args = parser.parse_args()

    generate_dataset(records=args.records or DATASET_SIZE, mismatch_rate=args.mismatch_rate or MISMATCH_RATE)