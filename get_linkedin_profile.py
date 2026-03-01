import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def filter_profile_data(data: dict) -> dict:
    """Filters profile data returning only the specifically requested fields."""
    if not data:
        return {}

    direct_fields = {
        "name", "city", "country_code", "about", 
        "educations_details", "languages", "recommendations", 
        "current_company_name", "publications", "organizations", 
        "honors_and_awards", "bio_links", "first_name", "last_name",
        "education", "certifications", "projects", "experience"
    }

    # 1. Remove top-level keys not in our allowed list
    keys_to_remove = [k for k in data.keys() if k not in direct_fields]
    for k in keys_to_remove:
        data.pop(k, None)
            
    # 2. Process education array (keep only first item, remove specific keys)
    education = data.get("education", [])
    if isinstance(education, list):
        if len(education) > 0:
            edu_first = education[0]
            if isinstance(edu_first, dict):
                for key in ["description", "description_html", "institute_logo_url"]:
                    edu_first.pop(key, None)
            data["education"] = [edu_first]
        else:
            data.pop("education", None)

    # 3. Process certifications array
    certifications = data.get("certifications", [])
    if isinstance(certifications, list):
        new_certs = []
        for cert in certifications:
            if isinstance(cert, dict):
                for key in ["credential_url", "credential_id"]:
                    cert.pop(key, None)
                if "subtitle" in cert:
                    cert["issuer"] = cert.pop("subtitle")
                if "meta" in cert:
                    cert["notes"] = cert.pop("meta")
                new_certs.append(cert)
        if new_certs:
            data["certifications"] = new_certs
        else:
            data.pop("certifications", None)

    # 4. Remove nulls ONLY from projects array
    projects = data.get("projects", [])
    if isinstance(projects, list):
        new_projects = [p for p in projects if p is not None]
        if new_projects:
            data["projects"] = new_projects
        else:
            data.pop("projects", None)

    # 5. Remove membership_number from organizations
    orgs = data.get("organizations", [])
    if isinstance(orgs, list):
        for org in orgs:
            if isinstance(org, dict):
                org.pop("membership_number", None)
    

    return data

def get_linkedin_profile(profile_url: str) -> dict:
    """
    Fetches a LinkedIn profile using Bright Data API.
    
    Args:
        profile_url (str): The LinkedIn profile URL.
        
    Returns:
        dict: The profile data.
    """
    api_token = os.environ.get("BRIGHTDATA_API_TOKEN")
    dataset_id = os.environ.get("BRIGHTDATA_PROFILE_DATASET_ID")
    
    if not api_token or not dataset_id:
        raise ValueError("Missing Bright Data API credentials in environment variables.")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    # 1) Trigger collection
    trigger_url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={dataset_id}"
    payload = [{"url": profile_url}]
    
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

        if status == "ready" or status is None and info.get("name"):
            break
        if status == "failed":
            raise RuntimeError(f"Snapshot failed: {info}")

        time.sleep(poll_interval)

    # 3) Download result as JSON
    download_url = f"{status_url}?format=json"
    data_resp = requests.get(download_url, headers=headers)
    data_resp.raise_for_status()
    data = data_resp.json()
    
    raw_profile = data[0] if data else {}
    return filter_profile_data(raw_profile)

if __name__ == "__main__":
    import json
    # Example usage
    user_slug = "ankita-sethi21"  # csabatothdev
    sample_url = f"https://www.linkedin.com/in/{user_slug}/"
    try:
        profile = get_linkedin_profile(sample_url)
        print("\nFull profile JSON:")
        print(json.dumps(profile, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
