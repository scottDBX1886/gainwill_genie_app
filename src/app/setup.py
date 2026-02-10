# Minimal setup for Databricks Apps install (pip install .).
# Local dev and apx build use pyproject.toml.
from setuptools import setup, find_packages

setup(
    name="gainwell-genie-app",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.119.0",
        "pydantic-settings>=2.11.0",
        "uvicorn>=0.37.0",
        "databricks-sdk>=0.74.0",
        "python-dotenv>=1.0.0",
    ],
)
