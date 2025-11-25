import os.path
import requests
import re
from datetime import datetime, timezone
import json
from dotenv import load_dotenv

load_dotenv()
TRACKING_FILE = 'posted_jobs_internships.json'


def fetch_parse_jobs():
    REPO_URL = 'https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md'

    response = requests.get(REPO_URL)
    content = response.text

    jobs = {}

    # Split content by ## headers to get sections
    sections = re.split(r'(## .*?)\n', content)

    target_content = ""
    capture = False

    for i, section in enumerate(sections):
        if '💻' in section or '📱' in section or '🤖' in section:
            if 'Software Engineering' in section or 'Product Management' in section or 'Data Science' in section:
                capture = True
                continue
        # Check if we hit a different section
        elif section.startswith('## ') and capture:
            capture = False

        # Capture the content if we're in a target section
        if capture and i < len(sections):
            target_content += section

    print(f"Extracted target sections, length: {len(target_content)}")

    # Use regex to find all table rows in target sections only
    tr_pattern = r'<tr>(.*?)</tr>'
    td_pattern = r'<td[^>]*>(.*?)</td>'

    # Find all table rows
    rows = re.findall(tr_pattern, target_content, re.DOTALL)

    print(f"Found {len(rows)} total rows in target sections")

    for row in rows:
        # Extract all td elements from this row
        cells = re.findall(td_pattern, row, re.DOTALL)

        # We need at least 5 cells: Company, Role, Location, Application, DayOld
        if len(cells) < 5:
            continue

        company_html = cells[0]
        role_html = cells[1]
        location_html = cells[2]
        application_html = cells[3]
        age_html = cells[4]

        # Extract company name (remove HTML tags and emojis)
        company = re.sub(r'<[^>]+>', '', company_html)
        company = re.sub(r'[🔥🛂🇺🇸🔒🎓↳]', '', company).strip()

        # Skip if company is empty or just an arrow
        if not company or company == '↳':
            continue

        # Extract role name (remove HTML tags)
        role = re.sub(r'<[^>]+>', '', role_html).strip()

        # Extract location (handle <details> tags and <br> tags)
        location = re.sub(r'<details>.*?</details>', '', location_html, flags=re.DOTALL)
        location = re.sub(r'<br\s*/?>', ', ', location)
        location = re.sub(r'<[^>]+>', '', location).strip()

        # Extract application link from the application column
        link_match = re.search(r'href=["\']([^"\']+)["\']', application_html)
        link = link_match.group(1) if link_match else None

        # Extract days old
        age_text = re.sub(r'<[^>]+>', '', age_html).strip()
        age_match = re.search(r'(\d+)d', age_text)
        days_old = int(age_match.group(1)) if age_match else 999

        # Only process jobs that are 0-3 days old (fresh postings)
        if days_old > 3:
            continue

        # Skip if no link
        if not link:
            continue

        print(f"Found fresh job: {company} - {role} ({days_old}d old)")

        # Clean up role and company names
        clean_role = re.sub(r'\s+', ' ', role).strip()
        clean_company = re.sub(r'\s+', ' ', company).strip()

        # Create unique job ID
        raw_id = f"{clean_company}_{clean_role}_{location}"
        raw_id = re.sub(r'[^\w\s-]', '', raw_id)
        raw_id = raw_id.replace(' ', '_').replace(',', '')
        job_id = raw_id[:100].lower()

        jobs[job_id] = {
            'company': clean_company,
            'role': clean_role,
            'location': location,
            'link': link,
            'DaysOld': days_old
        }

    return jobs


def load_posted_job():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get('posted_ids', []))
    return set()


def saved_posted_job(posted_id):
    data = {
        'posted_ids': list(posted_id),
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'total_posted': len(posted_id)
    }
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def send_discord_webhook(job, webhook_url):
    if not job['link']:
        print(f" Skipped {job['company']} - {job['role']} (no application link)")
        return False

    embed = {
        "title": f"🎯 {job['company']} - {job['role']}",
        "url": job['link'],
        "color": 3447003,
        "fields": [
            {
                "name": "📍 Location",
                "value": job['location'],
                "inline": True
            },
            {
                "name": "🔗 Application",
                "value": f"[Click here to apply]({job['link']})",
                "inline": False
            }
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {
            "text": "Panthers to FAANG | Summer 2026 Internships"
        }
    }

    payload = {"embeds": [embed]}

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"✅ Posted: {job['company']} - {job['role']}")
        return True
    except Exception as e:
        print(f"Error Posting Job: {e}")
        return False


def main():
    WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

    if not WEBHOOK_URL:
        print("This is not the correct webhook url/ not being uploaded correctly")

    # Load the posted jobs
    posted_jobs = load_posted_job()
    print(f"📋 Already posted: {len(posted_jobs)} jobs")

    all_jobs = fetch_parse_jobs()
    print(f"📊 Found {len(all_jobs)} total jobs in repo")

    # Filter to only new jobs
    new_jobs = {job_id: job_data for job_id, job_data in all_jobs.items()
                if job_id not in posted_jobs}
    print(f"🆕 New jobs to post: {len(new_jobs)}")

    # to avoid constant redeploying if there is no new jobs then we will exit waiting for the next run
    if not new_jobs:
        print("No new jobs were found")
        return

    MAX_POST = 10
    posted_count = 0

    for job_id, job_data in list(new_jobs.items())[:MAX_POST]:
        if send_discord_webhook(job_data, WEBHOOK_URL):
            posted_jobs.add(job_id)
            posted_count += 1

    saved_posted_job(posted_jobs)
    print(f"✅ Done! Posted {posted_count} new jobs. Total tracked: {len(posted_jobs)}")

    if len(new_jobs) > MAX_POST:
        print(f"⏳ {len(new_jobs) - MAX_POST} jobs remaining for next run")


if __name__ == '__main__':
    main()
