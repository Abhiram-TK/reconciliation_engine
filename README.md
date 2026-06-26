# Reconciliation Automation Engine

A backend data processing project that automates reconciliation between two transaction datasets using an ETL (Extract, Transform, Load) pipeline.

The system identifies missing, duplicate, and mismatched transactions and generates reconciliation reports for analysis.

---

## Features

- CSV Data Import
- Data Normalization
- Transaction Matching
- Amount Tolerance Matching
- Duplicate Detection
- Missing Record Detection
- Fuzzy Customer Name Matching
- Discrepancy Report Generation
- Summary Report Generation
- Development Dataset Generation using Faker

---

## Technology Stack

- Python
- Pandas
- RapidFuzz
- Faker
- Matplotlib
- OpenPyXL

---

## ETL Workflow

```text
Input CSV Files
        ↓
Extract
        ↓
Normalize
        ↓
Compare Records
        ↓
Detect Discrepancies
        ↓
Generate Reports
        ↓
Visualization
```

---

## Matching Workflow

```text
Transaction A
        │
Transaction B
        │
────────┼────────
        ▼
Exact Match
        │
        ▼
Amount Tolerance Check
        │
        ▼
Fuzzy Customer Match
        │
        ▼
Duplicate Detection
        │
        ▼
Mismatch Report
```

---

## Project Structure

```text
project/
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── reports/
│
├── src/
│   ├── analytics/
│   ├── comparison/
│   ├── matching/
│   ├── reporting/
│   └── utils/
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

## Input

The reconciliation engine compares two transaction datasets.

Typical fields include:

- Transaction ID
- Customer Name
- Amount
- Transaction Date

---

## Output

The engine generates reports including:

- Exact Matches
- Missing Records
- Duplicate Records
- Amount Mismatches
- Customer Name Mismatches
- Reconciliation Summary

Generated reports are stored in the `reports/` directory.

---

## Development Data

The project uses Faker to generate realistic transaction datasets for development and testing.

Generated data includes:

- Customer Names
- Transaction IDs
- Transaction Dates
- Transaction Amounts

---

## Run Locally

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Execute Reconciliation

```bash
python src/main.py
```

---

## Jupyter Notebook

A demonstration notebook is available under:

```text
notebooks/
```

The notebook illustrates the reconciliation workflow, generated reports, and summary statistics.

---

## Portfolio Scope

This project demonstrates:

- ETL Pipeline Design
- Data Cleaning
- Data Normalization
- Record Matching
- Fuzzy String Matching
- Data Validation
- Report Generation
- Data Analysis
- Backend Automation
