# PostgreSQL OLAP Optimization Lab

A Python-based performance lab for **analytical PostgreSQL workloads** on a large synthetic banking dataset.

The project generates millions of records, runs expensive aggregation queries, applies several PostgreSQL optimization techniques and compares the execution time of the original and optimized query paths.

> Focus: **Python backend engineering, PostgreSQL performance, OLAP, indexing and materialized views.**

---

## Why this project exists

Analytical SQL can become expensive very quickly when queries combine:

- large transaction tables;
- multiple `JOIN`s;
- `GROUP BY` aggregations;
- time-series filtering;
- customer segmentation;
- repeated business analytics over the same source data.

This project models that situation and demonstrates how the query path can be redesigned instead of only trying to micro-optimize Python code around it.

---

## Test dataset

The script can generate a synthetic banking workload with:

| Entity | Generated rows |
|---|---:|
| Clients | 50,000 |
| Accounts | 150,000 |
| Transactions | 5,000,000 |
| **Total** | **5,200,000** |

The data covers clients, account balances, transaction categories, transaction types and timestamps spread across several years.

---

## Optimization techniques

### 1. Purpose-built indexes

The optimizer creates several types of indexes for different access patterns:

- **BRIN index** for transaction timestamps;
- composite indexes for common multi-column filters;
- partial indexes for high-value amounts and balances;
- indexes for account relations, transaction categories and client dimensions.

Examples include:

```sql
CREATE INDEX idx_transactions_created_at_brin
ON transactions USING BRIN(created_at);

CREATE INDEX idx_transactions_type_date
ON transactions(transaction_type, created_at);

CREATE INDEX idx_transactions_amount_partial
ON transactions(amount)
WHERE amount > 1000;
```

### 2. Materialized views

Heavy aggregations are precomputed into materialized views for frequently requested analytical slices:

```text
raw tables
   │
   ├── clients
   ├── accounts
   └── transactions
          │
          ▼
   expensive joins + aggregation
          │
          ▼
   materialized views
   ├── mv_client_stats
   ├── mv_daily_transactions
   ├── mv_city_stats
   └── mv_monthly_analytics
          │
          ▼
   faster analytical reads
```

Separate indexes are also created on those materialized views.

### 3. Benchmarking original vs optimized queries

The script measures both versions of the same analytical workload and calculates the resulting speedup:

```text
Original SQL ───────► execute ──► execution time
                                      │
Optimized SQL ──────► execute ──► execution time
                                      │
                                      ▼
                             speedup = original / optimized
```

Each query is warmed up and then executed repeatedly before the average execution time is reported.

---

## Analytical workloads

The benchmark currently covers several realistic OLAP-style scenarios:

1. client statistics with multi-table joins;
2. monthly transaction analytics;
3. geographic analytics by city;
4. daily time-series activity;
5. customer segmentation by transaction activity.

The optimized versions read from precomputed analytical structures where appropriate.

---

## Architecture

```text
┌─────────────────────┐
│   Python benchmark  │
│     psycopg2        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│     PostgreSQL      │
├─────────────────────┤
│ clients             │
│ accounts            │
│ transactions        │
├─────────────────────┤
│ BRIN / B-tree       │
│ partial indexes     │
│ composite indexes   │
├─────────────────────┤
│ materialized views  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ benchmark results   │
│ time / speedup      │
└─────────────────────┘
```

---

## Tech stack

- **Python**
- **PostgreSQL**
- **psycopg2**
- SQL / OLAP
- BRIN and B-tree indexes
- partial and composite indexes
- materialized views
- synthetic data generation
- execution-time benchmarking

---

## Running locally

### Requirements

- Python 3.9+
- PostgreSQL
- a PostgreSQL database available locally
- `psycopg2`

Install the dependency:

```bash
pip install psycopg2-binary
```

Create a PostgreSQL database, then update the connection configuration in `main.py` for your local environment.

Run:

```bash
python main.py
```

The script will:

```text
01  recreate the test schema
02  generate synthetic banking data
03  create optimized indexes
04  create materialized views
05  execute original analytical queries
06  execute optimized analytical queries
07  print timings and calculated speedups
```

> Generating 5 million transactions is intentionally resource-intensive. Reduce the dataset sizes in `create_massive_test_data()` if you only want to inspect the workflow locally.

---

## Benchmark output

The project intentionally does **not** hard-code a claimed performance improvement in this README. Actual timings depend on PostgreSQL configuration, hardware, cache state and dataset size.

When the benchmark runs, it prints results in this form:

```text
Original:      ... s
Optimized:     ... s
Speedup:       ... x
Improvement:   ... %
```

This makes the result reproducible on the machine where the experiment is executed instead of presenting an arbitrary performance number.

---

## What this demonstrates

This project is mainly an exercise in moving performance work to the correct layer:

- understanding database access patterns;
- choosing indexes according to the workload;
- trading write/storage cost for faster analytical reads;
- precomputing expensive aggregation paths;
- measuring results instead of assuming an optimization worked.

It is closer to a **database performance engineering experiment** than to a traditional CRUD application.

---

## Possible next steps

- move database credentials to environment variables;
- add Docker Compose for reproducible PostgreSQL setup;
- capture `EXPLAIN (ANALYZE, BUFFERS)` plans;
- export benchmark results to CSV/JSON;
- add charts comparing query latency before and after optimization;
- split data generation, schema setup and benchmarking into separate modules;
- add automated tests for schema and query correctness.

---

### Author

**Furlos** — Python / Backend / PostgreSQL
