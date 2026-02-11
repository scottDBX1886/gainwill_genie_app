# Gainwell Genie Data App

Data app built with **Databricks APX** (FastAPI + React + shadcn/ui) and **Genie** for natural language over plan data. Ask questions in the chat, view results as a table, download CSV, or generate a chart. **Parameterized** so anyone can clone the repo and deploy with their own catalog, schema, warehouse, and Genie space.

## Features

- **Chat interface**: Natural language questions over your Unity Catalog tables (member, carrier, benefitplan, enrollkeys, provider, claim, referral).
- **Data view**: Table of query results with SQL shown.
- **Download**: Export current result as CSV.
- **Visualize**: Bar chart from the result set.
- **Parameterized**: Set `catalog`, `schema`, `warehouse_id`, and `genie_space_id` in `databricks.yml` (or via `-v`) and deploy; no hardcoded workspace values in app code.

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

## Clone and deploy (anyone can run this)

1. **Clone the repo** and `cd` into it.
2. **Configure your workspace and variables** (pick one):
   - **Option A**: Edit `databricks.yml` → under `targets.dev.variables` (or `prod`) set `catalog`, `schema`, `warehouse_id`, and `genie_space_id`. Set `workspace.profile` to your Databricks CLI profile (e.g. create with `databricks configure --token`).
   - **Option B**: Keep the file and override at deploy time:  
     `databricks bundle deploy -t dev -v catalog=my_catalog -v schema=my_schema -v warehouse_id=MY_WAREHOUSE_ID -v genie_space_id=MY_GENIE_SPACE_ID --profile MY_PROFILE`
3. **Create a Genie space** (if you don’t have one): In Databricks, create a Genie space over the same catalog/schema (and warehouse) you use for the app; copy the space ID into `genie_space_id`.
4. **Build, deploy, and run** (from repo root):  
   `./build-deploy-run.sh`  
   Or with a different target/profile:  
   `./build-deploy-run.sh dev my_profile`
5. **Set app env** so the app can talk to Genie and your warehouse: in `src/app/app.yml`, set `DATABRICKS_CATALOG`, `DATABRICKS_SCHEMA`, `DATABRICKS_WAREHOUSE_ID`, and `GENIE_SPACE_ID` to the same values as in your `databricks.yml` target (or your `-v` overrides). If you use the bundled `dev`/`prod` targets as-is, `app.yml` is already set to match.
6. Open the app URL printed at the end.

## Prerequisites

- **Warehouse**: A SQL warehouse in your workspace (used for Genie and the app).
- **Genie Space**: A Genie space over your catalog/schema; put its ID in `genie_space_id`.
- **Data**: Tables in your catalog/schema (or run the synthetic data job to create them).

## 1. Synthetic data (optional)

- Set `CATALOG` / `SCHEMA` if needed.
- On Databricks, run: `scripts/generate_synthetic_plandata.py` (e.g. via Run Python file MCP or a job).

## 2. Deploy with Asset Bundles

After configuring variables (see **Clone and deploy** above):

1. **Build the app** (from repo root):  
   `cd src/app && uv run apx build`  
   (Builds frontend and populates `gainwell_genie_app/__dist__` and metadata.)
2. **Validate**:  
   `databricks bundle validate -t dev`
3. **Deploy**:  
   `databricks bundle deploy -t dev --profile <your-profile>`
4. **Run app**:  
   `databricks bundle run gainwell_genie_app -t dev --profile <your-profile>`

Or use the one-liner: **`./build-deploy-run.sh [target] [profile]`**

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

Set these in **`src/app/app.yml`** so they match your bundle variables (same catalog, schema, warehouse, Genie space):

| Variable | Purpose | Match in databricks.yml |
|----------|---------|-------------------------|
| `DATABRICKS_CATALOG` | Catalog for data | `variables.catalog` |
| `DATABRICKS_SCHEMA` | Schema for data | `variables.schema` |
| `DATABRICKS_WAREHOUSE_ID` | SQL warehouse for Genie | `variables.warehouse_id` |
| `GENIE_SPACE_ID` | Genie space for chat | `variables.genie_space_id` |
| `PORT` | Set by platform (do not override) | — |

Keep `app.yml` in sync with `databricks.yml` (or your `-v` overrides) so the app and job use the same catalog/schema. Authentication is handled by the Databricks Apps runtime.

## Summary

- **Stack**: Databricks APX (FastAPI + React + shadcn/ui), Genie (NL → SQL).
- **Parameterized**: Set catalog, schema, warehouse ID, and Genie space ID in `databricks.yml` or via `-v`; app and job use bundle variables.
- **Deploy**: `./build-deploy-run.sh` or build in `src/app` then `bundle deploy` from repo root.
