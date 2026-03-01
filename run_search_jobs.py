from search_jobs import search_jobs
import json

def main():
    print("Testing LinkedIn Job Search using BrightData...")
    keyword = "python developer"
    print(f"Searching for keyword: '{keyword}'")
    
    try:
        jobs = search_jobs(keyword)
        print(f"\nFound {len(jobs)} job(s):\n")
        print(json.dumps(jobs, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\nError occurred: {e}")

if __name__ == "__main__":
    main()
