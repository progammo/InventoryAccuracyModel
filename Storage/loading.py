import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from ingestion import ingest_daily

# Load variables from .env file
load_dotenv()

# Read the URL securely
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

df = pd.read_csv("Data\\sales_inventory_cleaned.csv")
ingest_daily(df, engine)