
import json
from get_linkedin_profile import get_linkedin_profile

# Fetch basic LinkedIn profile data from BrightData
profile = get_linkedin_profile("https://www.linkedin.com/in/ankita-sethi21/")
# Load staged experience data (dataset does not include work history)
with open("experience_override.json") as f:
    override = json.load(f)
# Merge experience into the main profile
profile["experience"] = override.get("experience")

print(json.dumps(profile, indent=2))
