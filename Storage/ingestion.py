from sqlalchemy import Table, MetaData
from sqlalchemy.dialects.postgresql import insert

def ingest_daily(new_df, engine):
    metadata = MetaData()
    sales_table = Table("sales_data", metadata, autoload_with=engine)

    with engine.begin() as conn:
        for _, row in new_df.iterrows():
            stmt = insert(sales_table).values(**row.to_dict())
            stmt = stmt.on_conflict_do_update(
                index_elements=["sku_id", "date"],
                set_=row.to_dict()
            )
            conn.execute(stmt)
