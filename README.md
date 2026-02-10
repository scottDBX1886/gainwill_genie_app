# Gainwell Genie Data App

Data app built with **Databricks APX** (FastAPI + React + shadcn/ui) and **Genie** for natural language over plan data. Ask questions in the chat, view results as a table, download CSV, or generate a chart. Deployable via **Asset Bundles**; SQL uses warehouse **dbdemos-shared-endpoint**.

## Features

- **Chat interface**: Natural language questions over `dc_dev_replication.plandata_parallel_replica` tables (member, carrier, benefitplan, enrollkeys, provider, claim, referral).
- **Data view**: Table of query results with SQL shown.
- **Download**: Export current result as CSV.
- **Visualize**: Bar chart from the result set.
- **Parameterized**: Catalog, schema, warehouse ID, and Genie space ID are bundle variables.

## Repo layout

```
gainwell_genie_app/
├── databricks.yml              # Bundle config + variables
├── resources/
│   └── gainwell_genie_app.app.yml   # App resource (source_code_path: ../src/app)
├── src/
│   └── app/                    # APX app root (Databricks App)
│       ├── app.yml             # App command + env (uvicorn ...)
│       ├── pyproject.toml      # APX + Python deps
│       ├── package.json       # Frontend deps (Bun/npm)
│       └── gainwell_genie_app/
│           ├── backend/       # FastAPI, router, Genie client
│           ├── ui/            # React + TanStack Router + shadcn
│           └── __dist__/      # Built UI (after apx build)
└── scripts/
    └── generate_synthetic_plandata.py
```

## Prerequisites

- **Warehouse**: **dbdemos-shared-endpoint** (ID `a94a22f8652d85c1`).
- **Genie Space**: **Gainwell Plan Data**; ID in `databricks.yml` and `src/app/app.yml` (`GENIE_SPACE_ID`).
- **Data**: Tables in `dc_dev_replication.plandata_parallel_replica` (or run synthetic script).

## 1. Synthetic data (optional)

- Set `CATALOG` / `SCHEMA` if needed.
- On Databricks, run: `scripts/generate_synthetic_plandata.py` (e.g. via Run Python file MCP or a job).

## 2. Deploy with Asset Bundles

1. **Build the app** (from repo root):  
   `cd src/app && uv run apx build`  
   (Builds frontend and populates `gainwell_genie_app/__dist__` and metadata.)
2. **Validate**:  
   `databricks bundle validate -t dev`
3. **Deploy**:  
   `databricks bundle deploy -t dev`
4. **Run app**:  
   `databricks bundle run gainwell_genie_app -t dev`
5. **Logs**:  
   `databricks apps logs gainwell-genie-app-dev --profile <profile>`

## 3. Local development (APX)

From `src/app`:

- **Start dev servers** (backend + frontend + OpenAPI watcher):  
  `uv run apx dev start`
- **Status**:  
  `uv run apx dev status`
- **Type check**:  
  `uv run apx dev check`
- **Build for production**:  
  `uv run apx build`

Requires `uv` and (for full APX) `bun` or Node; first run will install deps.

## 4. App configuration

Env vars in `src/app/app.yml` (overridable via bundle):

| Variable | Purpose |
|----------|--------|
| `DATABRICKS_CATALOG` | Catalog. |
| `DATABRICKS_SCHEMA` | Schema. |
| `DATABRICKS_WAREHOUSE_ID` | SQL warehouse. |
| `GENIE_SPACE_ID` | Genie space for chat. |
| `PORT` | 8080. |

Authentication is handled by the Databricks Apps runtime.

## Summary

- **Stack**: Databricks APX (FastAPI + React + shadcn/ui), Genie (NL → SQL).
- **Warehouse**: dbdemos-shared-endpoint.
- **Deploy**: Build with `apx build` in `src/app`, then `bundle deploy` from repo root.
