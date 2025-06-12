#!/usr/bin/env python3
"""
Fetch every “place” matching a free-form query via Google Places API,
then dump the full details into a brand-new Google Sheet titled as that query,
and optionally share that sheet with specified Google accounts.

Now reads `GOOGLE_API_KEY` and `GOOGLE_APPLICATION_CREDENTIALS` from a `.env` file,
and uses Drive API to grant view/edit permissions.

Prereqs:
  pip install requests google-api-python-client google-auth python-dotenv

.env example:
  GOOGLE_API_KEY=AIzaSy...
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
"""

import os
import time
import requests
import argparse
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ------------------------------------------------------------
# LOAD .env
# ------------------------------------------------------------
load_dotenv()  # reads .env in cwd

# ------------------------------------------------------------
# CONFIG & AUTH
# ------------------------------------------------------------
API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
if not API_KEY:
    raise RuntimeError("Please set GOOGLE_API_KEY in your .env file.")

SERVICE_ACC_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
if not SERVICE_ACC_FILE or not os.path.exists(SERVICE_ACC_FILE):
    raise RuntimeError(
        "Please set GOOGLE_APPLICATION_CREDENTIALS in your .env to your service-account JSON."
    )

# We need both Sheets and Drive scopes to create and share spreadsheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACC_FILE, scopes=SCOPES
)

# Build service clients
sheets_svc = build("sheets", "v4", credentials=creds)
drive_svc  = build("drive",  "v3", credentials=creds)

# Places endpoints
TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL     = "https://maps.googleapis.com/maps/api/place/details/json"

# ------------------------------------------------------------
# 1) Grab all places via Text Search (handles pagination)
# ------------------------------------------------------------
def fetch_all_places(query):
    params = {"query": query, "key": API_KEY}
    places = []

    while True:
        resp = requests.get(TEXT_SEARCH_URL, params=params).json()
        if resp.get("status") not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Places TextSearch error: {resp}")
        places.extend(resp.get("results", []))
        token = resp.get("next_page_token")
        if not token:
            break
        # next_page_token needs a short pause
        time.sleep(2)
        params = {"pagetoken": token, "key": API_KEY}

    return places

# ------------------------------------------------------------
# 2) Drill into each place for full details
# ------------------------------------------------------------
def fetch_place_details(place_id):
    params = {
        "place_id": place_id,
        "fields": ",".join([
            "name",
            "formatted_address",
            "international_phone_number",
            "website",
            "place_id",
            "types",
            "rating",
            "user_ratings_total",
            "geometry",
        ]),
        "key": API_KEY,
    }
    resp = requests.get(DETAILS_URL, params=params).json()
    if resp.get("status") != "OK":
        return {}
    return resp.get("result", {})

# ------------------------------------------------------------
# 3) Create a new Google Sheet named as the query
# ------------------------------------------------------------
def create_spreadsheet(title):
    body = {"properties": {"title": title}}
    sheet = sheets_svc.spreadsheets().create(
        body=body, fields="spreadsheetId"
    ).execute()
    return sheet["spreadsheetId"]

# ------------------------------------------------------------
# 4) Share spreadsheet via Drive API
# ------------------------------------------------------------
def share_spreadsheet(spreadsheet_id, share_list, notify=False):
    for email, role in share_list:
        permission = {
            "type": "user",
            "role": role,            # "writer" or "reader"
            "emailAddress": email
        }
        drive_svc.permissions().create(
            fileId=spreadsheet_id,
            body=permission,
            sendNotificationEmail=notify
        ).execute()

# ------------------------------------------------------------
# 5) Write rows into Sheet
# ------------------------------------------------------------
def write_rows(spreadsheet_id, rows):
    body = {"values": rows}
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="A1",
        valueInputOption="RAW",
        body=body
    ).execute()

# ------------------------------------------------------------
# 6) Main flow
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Export Google Places results into a new Google Sheet and optionally share it."
    )
    parser.add_argument(
        "query",
        help="Free-form search string, e.g. 'commercial real estate agency in Roseville CA'"
    )
    parser.add_argument(
        "--share",
        action="append",
        metavar="EMAIL:ROLE",
        help="Grant permission to EMAIL with ROLE (writer or reader)."
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Send notification email when sharing."        
    )
    args = parser.parse_args()
    query = args.query

    print(f"🔍 Searching Places for: {query}")
    basic_places = fetch_all_places(query)

    print(f"ℹ️  Found {len(basic_places)} results, fetching details...")
    detailed = []
    for idx, pinfo in enumerate(basic_places, 1):
        pid = pinfo.get("place_id")
        if not pid:
            continue
        detail = fetch_place_details(pid)
        if not detail:
            continue
        detailed.append({
            "name": detail.get("name", ""),
            "formatted_address": detail.get("formatted_address", ""),
            "international_phone_number": detail.get("international_phone_number", ""),
            "website": detail.get("website", ""),
            "place_id": detail.get("place_id", ""),
            "types": ",".join(detail.get("types", [])),
            "rating": detail.get("rating", ""),
            "user_ratings_total": detail.get("user_ratings_total", ""),
            "lat": detail.get("geometry", {}).get("location", {}).get("lat", ""),
            "lng": detail.get("geometry", {}).get("location", {}).get("lng", ""),
        })
        print(f"  • ({idx}/{len(basic_places)}) {detail.get('name')}")

    # Build rows
    header = [
        "name", "formatted_address", "international_phone_number",
        "website", "place_id", "types", "rating",
        "user_ratings_total", "lat", "lng"
    ]
    rows = [header] + [[d[h] for h in header] for d in detailed]

    print("📄 Creating new Google Sheet...")
    sid = create_spreadsheet(query)

    # Share if requested
    if args.share:
        share_list = [tuple(s.split(':', 1)) for s in args.share]
        print(f"🚀 Sharing spreadsheet with: {share_list}")
        share_spreadsheet(sid, share_list, notify=args.notify)

    print(f"✏️  Writing {len(detailed)} rows to sheet ID={sid} …")
    write_rows(sid, rows)

    print(f"✅ Done! Sheet URL: https://docs.google.com/spreadsheets/d/{sid}")

if __name__ == "__main__":
    main()
