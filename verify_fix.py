import data_manager
import time
import pandas as pd

print("--- Starting Verification ---")

start_time = time.time()
success, msg = data_manager.load_data()
end_time = time.time()

print(f"Load Data Result: {success}, Message: {msg}")
print(f"Time taken: {end_time - start_time:.4f} seconds")

if success:
    df = data_manager.get_candidates()
    prefs = data_manager.get_preferences()
    
    print(f"\nCandidates Loaded: {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")
    
    print("\nPreferences Loaded:")
    for key, val in prefs.items():
        print(f"  - {key}: {len(val)} items")
        if len(val) > 0:
            print(f"    Sample: {val[:3]}")
else:
    print("Failed to load data.")
