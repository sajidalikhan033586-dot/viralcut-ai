import sqlite3
from pathlib import Path

db_path = Path("data/viralcut.db")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
cursor.execute("UPDATE jobs SET status = 'completed', progress = 100.0, current_stage = 'Processing complete' WHERE id = 'job_c521131dd0'")
conn.commit()
print("Updated job_c521131dd0 status to completed. Rows affected:", cursor.rowcount)
conn.close()
