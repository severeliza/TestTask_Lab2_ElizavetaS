import requests
import json
import clickhouse_connect
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(5),                 # максимум 5 попыток
    wait=wait_exponential(multiplier=1, min=1), # задержка: 1, 2, 4, 8, 16...
    retry=retry_if_exception_type(requests.exceptions.RequestException)
)

def download_data(url):
    resp = requests.get(url)
    if resp.status_code == 429 or resp.status_code >= 500:
        raise requests.exceptions.RequestException(
            f"Retryable error {resp.status_code}"
        )
    resp.raise_for_status()
    return resp.json()


def download_data(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def upload_to_clickhouse(data, client, table: str):
    if not isinstance(data, list):
        data = [data]

    rows = [(json.dumps(row, ensure_ascii=False),) for row in data]

    client.insert(
        table=table,
        data=rows,
        column_names=['raw_json']
    )


# Connect to ClickHouse
if __name__ == "__main__":    
    client = clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="default",
        password=""
    )

    # Create RAW_TABLE
    client.command("""
    CREATE TABLE IF NOT EXISTS raw_table (
        _inserted_at DateTime DEFAULT now(),
        raw_json String
    ) ENGINE = MergeTree 
    ORDER BY _inserted_at
    """)

    #не ReplicatedMergeTree, т.к. нет ZooKeeper/ClickHouse Keeper
    
    # Download data
    url = "http://api.open-notify.org/astros.json"
    json_data = download_data(url)

    upload_to_clickhouse(json_data, client, "raw_table")

    print("✅ Данные успешно загружены в ClickHouse!")