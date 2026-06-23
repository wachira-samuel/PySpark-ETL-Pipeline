# PySpark E-Commerce ETL Pipeline

A simple PySpark ETL project for generating synthetic e-commerce data, ingesting CSV files with schema enforcement, and performing basic data cleaning.

```
Raw CSVs → Ingestion → Cleaning → Enrichment → Aggregation → Analysis → Partitioned Parquet Output
```

---

<div align="center">

![PySpark](https://img.shields.io/badge/Apache_Spark-3.4.0-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Parquet](https://img.shields.io/badge/Parquet-Format-6B3BA4?style=for-the-badge&logo=apacheparquet&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-FFD700?style=for-the-badge&logo=opensourceinitiative&logoColor=white)

</div>

## Tech Stack

* Python 3.10+
* PySpark 3.4+
* Faker

---

## Project Structure

```text
PySpark-ETL-Pipeline/
│
├── README.md
├── Requirements.txt
├── Generate_data.py
├── Ingestion.py
├── cleaning.py
├── config.py
└── LICENSE
```

## Installation

### Prerequisites

* Python 3.10+
* Java 11 or 17
* PySpark 3.4+

### Clone the Repository

```
git clone https://github.com/wachira-samuel/PySpark-ETL-Pipeline.git
cd PySpark-ETL-Pipeline
```

### Create a Virtual Environment

```
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Install Dependencies

```
pip install -r Requirements.txt
```

## Generate Sample Data

Run:

```
python Generate_data.py
```

This creates synthetic e-commerce datasets including:

* Orders
* Order Items
* Customers
* Returns

## Pipeline Components

### 1. Data Generation (`Generate_data.py`)

Generates synthetic e-commerce data using Faker and writes it to CSV files.

### 2. Data Ingestion (`Ingestion.py`)

* Loads CSV files into Spark DataFrames.
* Uses predefined schemas from `config.py`.
* Enforces data types during ingestion.
* Captures invalid records for review.

### 3. Data Cleaning (`cleaning.py`)

Performs common data quality checks such as:

* Removing duplicate records
* Standardizing values
* Handling missing data
* Validating key fields
* Flagging suspicious values

### 4. Configuration (`config.py`)

Stores:

* File paths
* Spark schemas
* Shared configuration values used across the project

## Dependencies

Key packages:

```
pyspark==3.4.3
faker==24.2.0
pandas==2.2.1
numpy==1.26.4
pytest==8.1.1
pytest-mock==3.14.0
```

Install all dependencies with:

```
pip install -r Requirements.txt
```

---

## License

This project is licensed under the MIT License.
