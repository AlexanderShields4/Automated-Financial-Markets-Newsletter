#!/usr/bin/env python3
"""
Backfill missing newsletter entries in Supabase.

Queries the daily_briefs table for existing dates, then runs newsletter_collector
for each missing business day in the requested range.

Note: News API free tier only provides 1 month of history. Entries backfilled
beyond that will contain all market/FRED data but no news headlines.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
from supabase import create_client

from newsletter_collector import main as collect


def business_days(start: date, end: date) -> list[date]:
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:  # Mon–Fri
            days.append(current)
        current += timedelta(days=1)
    return days


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Backfill missing newsletter dates")
    parser.add_argument("--start-date", required=True,
                        type=lambda s: date.fromisoformat(s),
                        help="Start date YYYY-MM-DD (inclusive)")
    parser.add_argument("--end-date",
                        type=lambda s: date.fromisoformat(s),
                        default=date.today() - timedelta(days=1),
                        help="End date YYYY-MM-DD (inclusive, default: yesterday)")
    parser.add_argument("--force", action="store_true",
                        help="Re-run even for dates that already exist in the database")
    args = parser.parse_args()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)

    # Fetch all existing dates from the database
    result = supabase.table("daily_briefs").select("date").execute()
    existing_dates = {row["date"] for row in result.data}
    print(f"Found {len(existing_dates)} existing entries in database")

    # Determine which business days are missing
    all_days = business_days(args.start_date, args.end_date)
    missing = all_days if args.force else [d for d in all_days if str(d) not in existing_dates]

    if not missing:
        print("No missing dates found — database is up to date.")
        return

    print(f"\nDates to backfill ({len(missing)}):")
    for d in missing:
        print(f"  {d}")

    # Warn if any dates are older than 30 days (News API limitation)
    cutoff = date.today() - timedelta(days=30)
    old_dates = [d for d in missing if d < cutoff]
    if old_dates:
        print(f"\nWarning: {len(old_dates)} date(s) are older than 30 days.")
        print("News API free tier only provides 1 month of history.")
        print("Those entries will be generated without news headlines.\n")

    failed = []
    for i, d in enumerate(missing, 1):
        print(f"\n[{i}/{len(missing)}] Collecting data for {d}...")
        try:
            collect(target_date=d)
            print(f"  ✓ {d} saved successfully")
        except Exception as e:
            print(f"  ✗ {d} failed: {e}")
            failed.append(d)

    print(f"\n--- Backfill complete ---")
    print(f"  Succeeded: {len(missing) - len(failed)}")
    print(f"  Failed:    {len(failed)}")
    if failed:
        print(f"  Failed dates: {[str(d) for d in failed]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
