# Scripts

## generate_synthetic_plandata.py

Generates synthetic data for the plandata schema and writes to the parameterized catalog/schema.

**Usage (on Databricks):**

1. Set environment or Spark conf:
   - `CATALOG` (default: `dc_dev_replication`)
   - `SCHEMA` (default: `plandata_parallel_replica`)

2. Run via MCP: `run_python_file_on_databricks` with `file_path` pointing to this script.

3. Or run as a job: add a job that runs this script and pass `catalog`/`schema` as job parameters (set in script via `spark.conf.get("catalog")` or env).

**Tables populated (subset for demo):**

- `member` – members with key columns
- `carrier` – carriers
- `benefitplan` – benefit plans
- `enrollkeys` – enrollment keys (links member, plan)
- `provider` – providers
- `claim` – claims (key columns, FK to member/enroll/provider)
- `referral` – referrals (key columns)

After running, create or update the Genie Space to point at the same catalog/schema and use that space’s ID in the app (`GENIE_SPACE_ID`).
