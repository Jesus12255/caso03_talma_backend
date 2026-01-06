
from datetime import datetime
from zoneinfo import ZoneInfo
import json

# Setup
TIME_ZONE = ZoneInfo("America/Bogota")
print("--- TEST: NAIVE LOCAL STORAGE ---")

# 1. Proposal: Get Naive Local Date (Strip TZ)
def get_naive_local_datetime():
    # Get current time in Bogota
    now_aware = datetime.now(TIME_ZONE)
    # Strip timezone info effectively saying "It is 15:30" (abstract)
    return now_aware.replace(tzinfo=None)

naive_local = get_naive_local_datetime()
print(f"1. Naive Local Generated: {naive_local} (Computed from Bogota time)")
print(f"   Has tzinfo? {naive_local.tzinfo}")

# 2. Simulate User View (Reading it back from DB)
# If stored as Naive in TIMESTAMP (no TZ): 
print(f"2. Value in DB (Naive): {naive_local}")
print(f"   User sees: {naive_local}")

# 3. Validation
# The user wants "15:xx" to happen.
print(f"3. Does this match user wall clock? YES (assuming user is in Bogota)")

# 4. JSON Serialization check
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type not serializable")

json_out = json.dumps({"creado": naive_local}, default=json_serial)
print(f"4. JSON API Output: {json_out}")
print("   Note: No 'Z' or offset. Frontend treats as local time usually.")
