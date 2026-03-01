import os
import pytest
import responses
from get_job_listing import get_job_listing
from get_linkedin_profile import get_linkedin_profile
from search_jobs import search_jobs

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

@responses.activate
def test_search_jobs_success():
    trigger_url = "https://api.brightdata.com/datasets/v3/trigger?dataset_id=fake_job_id"
    status_url = "https://api.brightdata.com/datasets/v3/snapshot/snap_789"
    download_url = f"{status_url}?format=json"

    # Mock trigger
    responses.add(
        responses.POST,
        trigger_url,
        json={"snapshot_id": "snap_789"},
        status=200,
    )

    # Mock status check
    responses.add(
        responses.GET,
        status_url,
        json={"status": "ready"},
        status=200,
    )

    # Mock download — multiple jobs with extra fields that should be filtered out
    responses.add(
        responses.GET,
        download_url,
        json=[
            {
                "job_title": "Python Developer",
                "company_name": "Acme Corp",
                "job_location": "Remote",
                "job_url": "https://linkedin.com/jobs/view/111",
                "extra_field": "should be removed",
            },
            {
                "job_title": "Senior Python Engineer",
                "company_name": "Beta Inc",
                "job_location": "New York, NY",
                "job_url": "https://linkedin.com/jobs/view/222",
                "internal_id": "xyz",
            },
        ],
        status=200,
    )

    result = search_jobs("python developer")
    assert len(result) == 2
    assert result[0] == {
        "job_title": "Python Developer",
        "company_name": "Acme Corp",
        "job_location": "Remote",
        "job_url": "https://linkedin.com/jobs/view/111",
    }
    assert result[1] == {
        "job_title": "Senior Python Engineer",
        "company_name": "Beta Inc",
        "job_location": "New York, NY",
        "job_url": "https://linkedin.com/jobs/view/222",
    }
    # Verify extra fields were filtered out
    assert "extra_field" not in result[0]
    assert "internal_id" not in result[1]

