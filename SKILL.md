---
name: littlebeaver-cfo
description: Read and analyze locally mirrored data in Little Beaver CFO, including company overview, financial statements, invoice and tax filing summaries, fund trends, and anomaly findings. Use when the user asks for a cross-assistant finance view or CFO analysis.
license: See LICENSE
---

# Little Beaver CFO

Query the local read-only API exposed by the running 首席财务官 application. Use the bundled `scripts/cfo_client.py` rather than reading the mirror database directly.

## Requirements

- 首席财务官 v1.0.6 or later is installed and running on the same computer.
- Python 3.10 or later is available to run the client.
- The client only connects to `127.0.0.1` or `localhost`; default discovery scans ports 8860 through 8879. Use `--base-url` when automatic discovery cannot find the service.

## Workflow

1. Run `health` and confirm the service is `littlebeaver-cfo`.
2. Run `companies` to identify the company. If the user did not identify a company and several are returned, ask which one to use.
3. Use the matching read command: `overview`, `findings`, `fin-index`, `fin-statement`, `fin-analysis`, `fin-trend`, `invoice-insights`, `fund-insights`, `filings`, `filing-detail`, or `report-preview`.
4. When the user specifies a period, preserve it exactly. Do not silently replace a missing period with the latest period. For `fin-statement` and `fin-analysis`, use a company tax number and period returned by `fin-index`.
5. State the company and data-as-of date when available. Distinguish source facts from analysis, and do not infer missing values.

## Commands

```bash
python scripts/cfo_client.py health
python scripts/cfo_client.py companies
python scripts/cfo_client.py overview
python scripts/cfo_client.py findings --tax-no 91310000XXXXXXXXXX --status open
python scripts/cfo_client.py fin-index
python scripts/cfo_client.py fin-statement --tax-no 91310000XXXXXXXXXX --period 2025 --statement income
python scripts/cfo_client.py fin-analysis --tax-no 91310000XXXXXXXXXX --period 2025
python scripts/cfo_client.py fin-trend --tax-no 91310000XXXXXXXXXX --metric revenue
python scripts/cfo_client.py invoice-insights --tax-no 91310000XXXXXXXXXX --months 12
python scripts/cfo_client.py fund-insights --tax-no 91310000XXXXXXXXXX --months 12
python scripts/cfo_client.py filings --tax-no 91310000XXXXXXXXXX
python scripts/cfo_client.py filing-detail --tax-no 91310000XXXXXXXXXX --form-code VAT --period-key 2025-12
python scripts/cfo_client.py report-preview --tax-no 91310000XXXXXXXXXX --months 12
```

`fin-statement --statement` accepts `balance`, `income`, or `cash`. `fin-trend` accepts `--metric` or a `--statement` plus `--item-name`. `filings` accepts `--view overview` to return the filing overview instead of the period catalog.

## Data and safety

- CFO reads from its local mirror of the three assistants. It does not expose every source detail: invoice records and bank transaction records are not mirrored.
- The client sends only GET requests to the local CFO service. It never triggers synchronization, changes findings, edits source configuration, or writes to assistant databases.
- Treat returned financial data as private. Do not send it to external services unless the user explicitly asks.
- If the service is unavailable, ask the user to start 首席财务官 and retry. A missing company, period, or filing means the corresponding source data may not have been synced.
