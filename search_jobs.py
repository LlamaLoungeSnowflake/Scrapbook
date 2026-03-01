import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


def search_jobs(keyword: str) -> list[dict]:
    """
    Searches for LinkedIn job listings matching a keyword using Bright Data API.

    Args:
        keyword (str): The search query (e.g. "python developer").

    Returns:
        list[dict]: A list of matching job listing dicts.
    """
    api_token = os.environ.get("BRIGHTDATA_API_TOKEN")
    dataset_id = os.environ.get("BRIGHTDATA_JOB_DATASET_ID")

    if not api_token or not dataset_id:
        raise ValueError("Missing Bright Data API credentials in environment variables.")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    # 1) Trigger keyword discovery
    # BrightData's job dataset expects a URL, so we construct a LinkedIn search URL
    from urllib.parse import quote_plus
    encoded_keyword = quote_plus(keyword)
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_keyword}"
    
    trigger_url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={dataset_id}"
    payload = [{"url": search_url}]

    print(f"Triggering job search with payload {payload}")
    resp = requests.post(trigger_url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    snapshot_id = resp.json().get("snapshot_id")

    if not snapshot_id:
        raise RuntimeError(f"Failed to get snapshot_id from response: {resp.json()}")

    # 2) Poll until ready
    status_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    poll_interval = int(os.environ.get("BRIGHTDATA_POLL_INTERVAL", 5))

    print(f"Snapshot ID: {snapshot_id}. Polling status every {poll_interval}s...")

    while True:
        status_resp = requests.get(status_url, headers=headers, timeout=30)
        status_resp.raise_for_status()
        info = status_resp.json()
        status = info.get("status")

        print(f"Polling status: {status}")

        if status == "ready":
            break
        if status == "failed":
            raise RuntimeError(f"Snapshot failed: {info}")

        time.sleep(poll_interval)

    # 3) Download results as JSON
    print("Downloading results...")
    download_url = f"{status_url}?format=json"
    data_resp = requests.get(download_url, headers=headers, timeout=60)
    try:
        data_resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error downloading data: {e}")
        print(f"Response body: {data_resp.text}")
        raise
    data = data_resp.json()

    if not isinstance(data, list):
        data = [data] if data else []

    # 4) Filter each job to keep only useful fields
    keep_fields = {
        "job_title", "company_name", "job_location", "job_url",
        "job_summary", "job_seniority_level", "job_employment_type",
        "job_industries", "job_base_pay_range", "base_salary",
    }

    results = []
    for raw_job in data:
        filtered = {k: v for k, v in raw_job.items() if k in keep_fields}
        if filtered:
            results.append(filtered)

    return results


if __name__ == "__main__":
    import json

    sample_keyword = "python developer"
    try:
        jobs = search_jobs(sample_keyword)
        print(f"Found {len(jobs)} job(s) for '{sample_keyword}':\n")
        print(json.dumps(jobs, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
