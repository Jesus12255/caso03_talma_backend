from datetime import datetime
import time

now_utc = datetime.utcnow()
now_ts = now_utc.timestamp()
exp_from_log = 1773283325

print(f"Now UTC: {now_utc}")
print(f"Now TS: {now_ts}")
print(f"Exp TS: {exp_from_log}")
print(f"Diff: {exp_from_log - now_ts}")
