
from utl.date_util import DateUtil
from datetime import datetime

print("--- VERIFICATION: NAIVE IMPLEMENTATION ---")

# 1. Check DateUtil output
local_dt = DateUtil.get_current_local_datetime()
print(f"1. DateUtil.get_current_local_datetime returns: {local_dt}")
print(f"   Type: {type(local_dt)}")
print(f"   Has Timezone (tzinfo)? {local_dt.tzinfo}")

if local_dt.tzinfo is None:
    print("   [SUCCESS] Date is Naive (No Timezone Info)")
else:
    print("   [FAIL] Date still has Timezone Info")

# 2. visual check
print(f"   Visual Time: {local_dt.strftime('%H:%M:%S')}")
print("   Please verify this matches your current wall clock.")
