from google_adk.tools import tool
from google.cloud import bigquery

from python_src.config.environment import config


@tool
def query_historical_storms(location: str, storm_type: str, years_back: int = 10) -> dict:
    """Queries historical storm data from NOAA datasets."""
    try:
        client = bigquery.Client(
            project=config.PROJECT_ID,
            location=config.BIGQUERY_LOCATION
        )
        query = f"""
            SELECT * FROM `bigquery-public-data.noaa_historic_severe_storms.storms_*`
            WHERE _TABLE_SUFFIX BETWEEN '{2023 - years_back}' AND '2023'
            AND event_type = '{storm_type}'
            AND state = '{location}'
            LIMIT 100
        """
        query_job = client.query(query)
        results = query_job.result()
        return {"results": [dict(row) for row in results]}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
