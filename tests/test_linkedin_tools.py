import os
import pytest
import responses
from get_job_listing import get_job_listing
from get_linkedin_profile import get_linkedin_profile

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("BRIGHTDATA_API_TOKEN", "fake_token")
    monkeypatch.setenv("BRIGHTDATA_JOB_DATASET_ID", "fake_job_id")
    monkeypatch.setenv("BRIGHTDATA_PROFILE_DATASET_ID", "fake_profile_id")

@responses.activate
def test_get_job_listing_success():
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger?dataset_id=fake_job_id"
    status_url = "https://api.brightdata.com/datasets/v3/snapshot/snap_123"
    download_url = f"{status_url}?format=json"

    # Mock trigger
    responses.add(
        responses.POST,
        trigger_url,
        json={"snapshot_id": "snap_123"},
        status=200
    )

    # Mock status check
    responses.add(
        responses.GET,
        status_url,
        json={"status": "ready"},
        status=200
    )

    # Mock download
    responses.add(
        responses.GET,
        download_url,
        json=[{"job_title": "Software Engineer"}],
        status=200
    )

    result = get_job_listing("https://www.linkedin.com/jobs/view/123")
    assert result == {"job_title": "Software Engineer"}

@responses.activate
def test_get_linkedin_profile_success():
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger?dataset_id=fake_profile_id"
    status_url = "https://api.brightdata.com/datasets/v3/snapshot/snap_456"
    download_url = f"{status_url}?format=json"

    # Mock trigger
    responses.add(
        responses.POST,
        trigger_url,
        json={"snapshot_id": "snap_456"},
        status=200
    )

    # Mock status check
    responses.add(
        responses.GET,
        status_url,
        json={"status": "ready"},
        status=200
    )

    # Mock download
    responses.add(
        responses.GET,
        download_url,
        json=[{"name": "John Doe"}],
        status=200
    )

    result = get_linkedin_profile("https://www.linkedin.com/in/johndoe")
    assert result == {"name": "John Doe"}
