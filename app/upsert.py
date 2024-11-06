import pandas as pd
import psycopg2
from config.settings import get_settings
from datasets import load_dataset
from services.summarize import generate_summary

settings = get_settings()

# Load the dataset
dataset = load_dataset("cnn_dailymail", "3.0.0")
subset = dataset["train"].shuffle(seed=42).select(range(10))

# Select only required columns
df = pd.DataFrame(subset)[["article", "highlights"]]


# Add the summary to the dataframe for context
df["summary"] = df["article"].apply(generate_summary)


with psycopg2.connect(settings.database.service_url) as conn:
    with conn.cursor() as cursor:
        # Prepare the SQL statement for bulk insertion
        insert_query = """
            INSERT INTO news (article, highlights, summary) 
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
        """
        # Convert DataFrame to list of tuples for efficient bulk insertion
        records = list(df.itertuples(index=False, name=None))

        try:
            cursor.executemany(insert_query, records)
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to insert records: {str(e)}") from e
