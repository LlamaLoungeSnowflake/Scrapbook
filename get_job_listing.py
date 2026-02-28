import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def get_job_listing(job_url: str) -> dict:
    """
    Fetches a LinkedIn job listing using Bright Data API.
    
    Args:
        job_url (str): The LinkedIn job posting URL.
        
    Returns:
        dict: The job listing data.
    """
    api_token = os.environ.get("BRIGHTDATA_API_TOKEN")
    dataset_id = os.environ.get("BRIGHTDATA_JOB_DATASET_ID")
    
    if not api_token or not dataset_id:
        raise ValueError("Missing Bright Data API credentials in environment variables.")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    # 1) Trigger collection
    trigger_url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={dataset_id}"
    payload = [{"url": job_url}]
    
    resp = requests.post(trigger_url, headers=headers, json=payload)
    resp.raise_for_status()
    snapshot_id = resp.json().get("snapshot_id")
    
    if not snapshot_id:
        raise RuntimeError(f"Failed to get snapshot_id from response: {resp.json()}")

    # 2) Poll until ready
    status_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    poll_interval = int(os.environ.get("BRIGHTDATA_POLL_INTERVAL", 5))
    
    while True:
        status_resp = requests.get(status_url, headers=headers)
        status_resp.raise_for_status()
        info = status_resp.json()
        status = info.get("status")

        if status == "ready":
            break
        if status == "failed":
            raise RuntimeError(f"Snapshot failed: {info}")

        time.sleep(poll_interval)

    # 3) Download result as JSON
    download_url = f"{status_url}?format=json"
    data_resp = requests.get(download_url, headers=headers)
    data_resp.raise_for_status()
    data = data_resp.json()
    
    return data[0] if data else {}

if __name__ == "__main__":
    import json
    # Example usage
    sample_url = "https://www.linkedin.com/jobs/view/1234567890/"
    try:
        job = get_job_listing(sample_url)
        print(json.dumps(job, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
