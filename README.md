# Project 4 - Reconciliation Automation Engine

> Portfolio Project 4

Financial reconciliation service of the Backend Transaction Ecosystem.

## Project Overview

The Reconciliation Automation Engine compares sales and inventory records,
detects discrepancies, and produces reconciliation reports through a dedicated
service layer. Data retrieval is delegated to `SalesClient` and
`InventoryClient`, allowing the reconciliation logic to remain independent of
the underlying data source. The clients currently read CSV files and can later
be migrated to HTTP APIs without modifying the reconciliation workflow.

It is the final service in the current backend ecosystem.

The Reconciliation Automation Engine does not own transactional or inventory data.

Its responsibility is to analyze, compare and report on data produced by upstream services while preserving source-system ownership.

---

## Adapter Pattern

The application uses dedicated client adapters to isolate data access from the
reconciliation pipeline.

```text
Current

SalesClient
InventoryClient
        │
        ▼
   CSV Files

Future

SalesClient
InventoryClient
        │
        ▼
 REST APIs / HTTP Services
```

Because the application communicates only with `SalesClient` and
`InventoryClient`, replacing CSV files with upstream service APIs requires
changes only inside the client layer. The reconciliation service and business
logic remain unchanged.

---

## Ecosystem Position

Startup Dependency

```text
      Authentication Service
                ↓
    Inventory Dispatch System
                ↓
    Sales Transaction Service
                ↓
  Reconciliation Automation Engine
```

Responsibilities

- ETL
- Data normalization
- Record matching
- Discrepancy detection
- Report generation

Consumes

- Sales Transaction Service
- Inventory Dispatch System

Produces

- Matching reports
- Discrepancy reports
- Reconciliation summaries

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
Sales CSV              Inventory CSV
     │                      │
     ▼                      ▼
SalesClient        InventoryClient
      \                   /
       \                 /
        ▼               ▼
      ReconciliationService
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

## Architecture

The Reconciliation Automation Engine follows a layered architecture that separates
data access from reconciliation logic.

```text
                  Reconciliation Automation Engine

                +------------------------------+
                |            main.py           |
                +--------------+---------------+
                               |
                               v
                +------------------------------+
                |    ReconciliationService     |
                +--------------+---------------+
                               |
               +---------------+---------------+
               |                               |
               v                               v
      +-------------------+          +----------------------+
      |    SalesClient    |          |   InventoryClient    |
      +---------+---------+          +----------+-----------+
                |                               |
                v                               v
        sales records                   inventory records
                \                               /
                 \                             /
                  +---------------------------+
                  | Normalization Services    |
                  +---------------------------+
                              |
                              v
                  +---------------------------+
                  |   Compare Records         |
                  +---------------------------+
                              |
                              v
                  +---------------------------+
                  | Detect Mismatches         |
                  +---------------------------+
                              |
                              v
                  +---------------------------+
                  | Report Generator          |
                  +---------------------------+
                              |
                              v
                  +---------------------------+
                  | Analytics & Charts        |
                  +---------------------------+
```

### Architectural Layers

- **Application Layer**
  - `main.py`

- **Service Layer**
  - `ReconciliationService`

- **Client Layer**
  - `SalesClient`
  - `InventoryClient`

- **Business Logic**
  - Normalization
  - Record Comparison
  - Mismatch Detection

- **Reporting**
  - CSV Reports
  - Summary Analytics
  - Charts

---

## Service Ownership

The Reconciliation Automation Engine is the authoritative owner of:

- Reconciliation Reports
- Matching Results
- Summary Reports
- Analytics Output
- Visualization Charts

This service consumes data from upstream services but never modifies their source data or databases.

Source systems remain the owners of their respective business entities.

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

### Outputs

- CSV reconciliation reports
- Summary reports
- Analytics charts

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
git clone https://github.com/Abhiram-TK/reconciliation_engine.git
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

### Execution Flow

Running the application performs the following sequence automatically:

```text
       Load Source Dataset
                ↓
       Load Target Dataset
                ↓
          Normalize Data
                ↓
         Compare Records
                ↓
        Detect Mismatches
                ↓
         Generate Reports
                ↓
        Generate Summary
                ↓
         Generate Charts
```

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

## Related Projects

| Service                   | Relationship                                          |
| ------------------------- | ----------------------------------------------------- |
| Authentication Service    | Upstream authentication provider within the ecosystem |
| Inventory Dispatch System | Inventory data source                                 |
| Sales Transaction Service | Transaction data source                               |

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
- Modular ETL Pipeline
- Configuration-driven Processing

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
