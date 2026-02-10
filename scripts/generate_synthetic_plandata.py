"""
Generate synthetic data for plandata_parallel_replica tables.
Parameterized via env: CATALOG, SCHEMA (defaults: dc_dev_replication, plandata_parallel_replica).
Run on Databricks (Spark + pandas). Uses dbdemos-shared-endpoint for any SQL if needed.
"""
import os
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

# -----------------------------------------------------------------------------
# CONFIG (parameterized for Asset Bundle / repo sharing)
# -----------------------------------------------------------------------------
CATALOG = os.environ.get("CATALOG", "dc_dev_replication")
SCHEMA = os.environ.get("SCHEMA", "plandata_parallel_replica")
N_MEMBERS = 800
N_CARRIERS = 12
N_PLANS = 50
N_PROVIDERS = 120
N_ENROLLMENTS = 2000
N_CLAIMS = 3500
N_REFERRALS = 400
SEED = 42

np.random.seed(SEED)
Faker.seed(SEED)
fake = Faker()

# Spark session (available on Databricks)
spark = None
try:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
except Exception:
    pass

if spark is None:
    raise RuntimeError("Spark is required. Run this script on Databricks or a Spark environment.")


def full_name(table: str) -> str:
    return f"{CATALOG}.{SCHEMA}.{table}"


def write_table(df: pd.DataFrame, table: str, mode: str = "overwrite") -> None:
    spark_df = spark.createDataFrame(df)
    # Overwrite schema so our generated columns replace any existing table schema (e.g. NOT NULL cosgroupid)
    # Retry on concurrent update (e.g. another run or retry writing to same table)
    last_err = None
    for attempt in range(4):
        try:
            spark_df.write.mode(mode).option("overwriteSchema", "true").saveAsTable(full_name(table))
            return
        except Exception as e:
            last_err = e
            if "ConcurrentAppendException" in type(e).__name__ or "DELTA_CONCURRENT" in str(e):
                if attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
            raise last_err
    raise last_err


def run_sql(sql: str) -> None:
    spark.sql(sql)


def main() -> None:
    print(f"Using catalog.schema: {CATALOG}.{SCHEMA}")
    print("Creating schema if not exists...")
    run_sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

    # ----- Carriers -----
    print("Generating carriers...")
    carriers = pd.DataFrame({
        "carrierid": [f"C{i:04d}" for i in range(N_CARRIERS)],
        "description": [fake.company() for _ in range(N_CARRIERS)],
        "carriertype": np.random.choice(["PPO", "HMO", "EPO"], N_CARRIERS, p=[0.5, 0.35, 0.15]),
        "fullname": [fake.company() for _ in range(N_CARRIERS)],
        "createdate": [fake.date_time_between(start_date="-2y", end_date="-1y") for _ in range(N_CARRIERS)],
        "lastupdate": datetime.now(),
    })
    write_table(carriers, "carrier")

    # ----- Benefit plans -----
    print("Generating benefit plans...")
    plans = pd.DataFrame({
        "planid": [f"PLAN{i:05d}" for i in range(N_PLANS)],
        "programid": np.random.choice(["MED", "DENT", "VISION"], N_PLANS, p=[0.7, 0.2, 0.1]),
        "description": [f"Plan {i} - {fake.catch_phrase()}" for i in range(N_PLANS)],
        "plantype": np.random.choice(["Standard", "Premium", "Basic"], N_PLANS, p=[0.5, 0.3, 0.2]),
        "status": np.random.choice(["active", "inactive"], N_PLANS, p=[0.9, 0.1]),
        "lifetimemax": np.round(np.random.lognormal(12, 0.5, N_PLANS), 2),
        "familydeductible": np.round(np.random.lognormal(8, 0.6, N_PLANS), 2),
        "maxoutofpocket": np.round(np.random.lognormal(9, 0.5, N_PLANS), 2),
        "createdate": [fake.date_time_between(start_date="-2y", end_date="-6m") for _ in range(N_PLANS)],
        "lastupdate": datetime.now(),
    })
    write_table(plans, "benefitplan")

    # ----- Members -----
    print("Generating members...")
    members = pd.DataFrame({
        "memid": [f"M{i:06d}" for i in range(N_MEMBERS)],
        "entityid": [f"ENT{i:06d}" for i in range(N_MEMBERS)],
        "status": np.random.choice(["active", "inactive", "terminated"], N_MEMBERS, p=[0.85, 0.05, 0.1]),
        "sex": np.random.choice(["M", "F"], N_MEMBERS, p=[0.48, 0.52]),
        "fullname": [fake.name() for _ in range(N_MEMBERS)],
        "dob": [fake.date_of_birth(minimum_age=18, maximum_age=85) for _ in range(N_MEMBERS)],
        "createdate": [fake.date_time_between(start_date="-3y", end_date="-1y") for _ in range(N_MEMBERS)],
        "lastupdate": datetime.now(),
    })
    write_table(members, "member")

    # ----- Providers -----
    print("Generating providers...")
    providers = pd.DataFrame({
        "provid": [f"P{i:05d}" for i in range(N_PROVIDERS)],
        "entityid": [f"PE{i:05d}" for i in range(N_PROVIDERS)],
        "fullname": [fake.name() for _ in range(N_PROVIDERS)],
        "specialtycode": np.random.choice(["IM", "PED", "CAR", "ORTH", "PSY"], N_PROVIDERS, p=[0.25, 0.2, 0.2, 0.2, 0.15]),
        "provtype": np.random.choice(["MD", "DO", "NP", "PA"], N_PROVIDERS, p=[0.5, 0.2, 0.2, 0.1]),
        "status": np.random.choice(["active", "inactive"], N_PROVIDERS, p=[0.92, 0.08]),
        "createdate": [fake.date_time_between(start_date="-3y", end_date="-6m") for _ in range(N_PROVIDERS)],
        "lastupdate": datetime.now(),
    })
    write_table(providers, "provider")

    # ----- Enrollments (enrollkeys) -----
    print("Generating enrollments...")
    mem_ids = members["memid"].tolist()
    plan_ids = plans["planid"].tolist()
    eff_end = datetime.now()
    eff_start = eff_end - timedelta(days=365 * 2)
    enrolls = []
    for i in range(N_ENROLLMENTS):
        enrolls.append({
            "enrollid": f"E{i:08d}",
            "planid": np.random.choice(plan_ids),
            "memid": np.random.choice(mem_ids),
            "effdate": fake.date_time_between(start_date=eff_start, end_date=eff_end),
            "termdate": np.random.choice([None, fake.date_time_between(start_date=eff_start, end_date=eff_end)], p=[0.85, 0.15]),
            "enrollmenttype": np.random.choice(["New", "Renewal", "Transfer"], p=[0.3, 0.5, 0.2]),
            "createdate": fake.date_time_between(start_date=eff_start, end_date=eff_end),
            "lastupdate": datetime.now(),
        })
    enroll_df = pd.DataFrame(enrolls)
    write_table(enroll_df, "enrollkeys")

    # ----- Claims (subset of columns) -----
    print("Generating claims...")
    enroll_ids = enroll_df["enrollid"].tolist()
    prov_ids = providers["provid"].tolist()
    claim_dates = pd.date_range(end=datetime.now(), periods=400, freq="D")
    claims = []
    for i in range(N_CLAIMS):
        dt = pd.Timestamp(np.random.choice(claim_dates))
        amt = float(np.random.lognormal(6, 1.2))
        claims.append({
            "claimid": f"CLM{i:08d}",
            "enrollid": np.random.choice(enroll_ids),
            "memid": np.random.choice(mem_ids),
            "provid": np.random.choice(prov_ids),
            "planid": np.random.choice(plan_ids),
            "startdate": dt,
            "enddate": dt + timedelta(days=int(np.random.randint(0, 5))),
            "totalamt": round(amt, 2),
            "eligibleamt": round(amt * np.random.uniform(0.7, 1.0), 2),
            "totalpaid": round(amt * np.random.uniform(0.5, 0.95), 2),
            "status": np.random.choice(["paid", "pending", "denied"], p=[0.75, 0.2, 0.05]),
            "createdate": dt,
            "lastupdate": datetime.now(),
        })
    write_table(pd.DataFrame(claims), "claim")

    # ----- Referrals (subset) -----
    print("Generating referrals...")
    refs = []
    for i in range(N_REFERRALS):
        refs.append({
            "referralid": f"REF{i:07d}",
            "enrollid": np.random.choice(enroll_ids),
            "memid": np.random.choice(mem_ids),
            "referto": np.random.choice(prov_ids),
            "referfrom": np.random.choice(prov_ids),
            "effdate": fake.date_time_between(start_date=eff_start, end_date=eff_end),
            "termdate": np.random.choice([None, fake.date_time_between(start_date=eff_start, end_date=eff_end)], p=[0.8, 0.2]),
            "status": np.random.choice(["approved", "pending", "completed"], p=[0.5, 0.2, 0.3]),
            "createdate": fake.date_time_between(start_date=eff_start, end_date=eff_end),
            "lastupdate": datetime.now(),
        })
    write_table(pd.DataFrame(refs), "referral")

    print("Done. Tables written to " + full_name("") + "*")


if __name__ == "__main__":
    main()
