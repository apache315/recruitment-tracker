import pandas as pd
import data_manager

print("Loading candidates...")
df = data_manager.load_candidates()
print("Columns found:", df.columns.tolist())

# Check for any column that looks like Status
for col in df.columns:
    if "STATUS" in str(col).upper():
        print(f"Potential match: '{col}'")
