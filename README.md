# Reconciliation Automation Engine

## Overview

Reconciliation Automation Engine is a Python-based ETL application that automates reconciliation between two transaction datasets.

The project loads source and target datasets, normalizes inconsistent values, compares records, detects discrepancies, performs fuzzy customer matching using RapidFuzz, and generates reconciliation reports with summary analytics and visualization.

The application is designed as a batch-processing backend service and is prepared for Docker containerization.

---

## Technology Stack

- Python
- Pandas
- RapidFuzz
- Faker
- Matplotlib
- OpenPyXL
- Jupyter Notebook

---

## ETL Pipeline

```text
Generate Dataset
        │
        ▼
Load CSV Files
        │
        ▼
Normalize Data
        │
        ▼
Compare Records
        │
        ▼
Detect Mismatches
        │
        ▼
Generate Reports
        │
        ▼
Generate Summary
        │
        ▼
Generate Charts
```

---

## Matching Workflow

```text
Source Record
        │
        ▼
Exact Match
        │
        ▼
Amount Comparison
        │
        ▼
RapidFuzz Name Similarity
        │
        ▼
Duplicate Detection
        │
        ▼
Missing Record Detection
        │
        ▼
Final Reconciliation Status
```

---

## Features

### ETL Processing

- CSV dataset loading
- Data normalization
- Exact transaction matching
- Amount comparison
- Missing record detection
- Mismatch detection
- Duplicate detection
- RapidFuzz customer matching

### Dataset Generation

- Synthetic transaction generation using Faker
- Configurable dataset size
- Configurable mismatch rate

### Reporting

- Matched transactions report
- Missing transactions report
- Mismatched transactions report
- Summary report
- Analytics chart generation

### Configuration

- Environment-based configuration
- Configurable dataset paths
- Configurable reports directory
- Configurable dataset generation

---

## Project Structure

```text
reconciliation_engine/

├── data
│   ├── source.csv
│   └── target.csv
│
├── docs
│   ├── reconciliation_chart.png
│   └── summary.png
│
├── notebooks
│   └── reconciliation_demo.ipynb
│
├── reports
│   ├── charts
│   │   └── reconciliation_summary.png
│   ├── matched.csv
│   ├── mismatched.csv
│   ├── missing.csv
│   └── summary.csv
│
├── src
│   ├── core
│   │   └── config.py
│   │
│   ├── processing
│   │   ├── compare_data.py
│   │   ├── fuzzy_matcher.py
│   │   ├── load_data.py
│   │   ├── mismatch_detector.py
│   │   └── normalize_data.py
│   │
│   ├── reporting
│   │   ├── analytics.py
│   │   └── report_generator.py
│   │
│   ├── utils
│   │   └── dataset_generator.py
│   │
│   └── main.py
│
├── tests
│   ├── test_analytics.py
│   ├── test_compare.py
│   ├── test_fuzzy_match.py
│   ├── test_load.py
│   ├── test_mismatch.py
│   ├── test_normalize.py
│   └── test_reports.py
│
├── .env
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Configuration

Project configuration is managed through environment variables.

Example:

```env
SOURCE_FILE=data/source.csv
TARGET_FILE=data/target.csv

REPORTS_DIR=reports
CHARTS_DIR=reports/charts

DATASET_SIZE=1000
MISMATCH_RATE=0.05
```

Copy `.env.example` to `.env` before running the application.

---

## Running the Project

### Clone Repository

```bash
git clone <https://github.com/Abhiram-TK/reconciliation_engine>
```

### Navigate into Project

```bash
cd reconciliation_engine
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Copy:

```text
.env.example
```

to

```text
.env
```

Modify configuration if required.

---

## Generate Development Dataset

Generate synthetic datasets using Faker.

```bash
python src/dataset_generator.py
```

Configuration is controlled through:

- DATASET_SIZE
- MISMATCH_RATE

---

## Run Reconciliation

```bash
python src/main.py
```

The application automatically:

- Loads datasets
- Normalizes records
- Compares transactions
- Detects mismatches
- Generates reports
- Generates analytics
- Creates visualization charts

---

## Generated Reports

Running the pipeline produces:

```text
reports/

matched.csv

mismatched.csv

missing.csv

summary.csv

charts/
    reconciliation_summary.png
```

---

## Demonstration Notebook

The project includes a Jupyter notebook demonstrating the complete reconciliation workflow.

Location:

```text
notebooks/reconciliation_demo.ipynb
```

The notebook demonstrates:

- Dataset loading
- Data normalization
- Record comparison
- RapidFuzz similarity matching
- Mismatch detection
- Report generation
- Analytics
- Visualization

---

## Sample Workflow

```text
Dataset Generator
        │
        ▼
source.csv / target.csv
        │
        ▼
main.py
        │
        ▼
Normalize Data
        │
        ▼
Compare Records
        │
        ▼
Detect Mismatches
        │
        ▼
Generate Reports
        │
        ▼
Generate Analytics
        │
        ▼
Visualization
```

---

## Portfolio Scope

This project demonstrates:

- ETL Pipeline Design
- Batch Processing
- Configurable Application Design
- Data Cleaning
- Data Normalization
- Exact Record Matching
- Fuzzy String Matching
- Automated Report Generation
- Data Visualization
- Environment-Based Configuration
- Reusable Python Modules

---

## Current Status

Implemented

- ETL reconciliation pipeline
- Configurable environment
- Dataset generator
- RapidFuzz matching
- Report generation
- Analytics
- Visualization
- Demonstration notebook

Next Phase

- Docker containerization
- Docker Compose execution
