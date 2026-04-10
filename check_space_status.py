from huggingface_hub import HfApi
import os

api = HfApi()
repo_id = "Mohana17/Crree-env"

try:
    # Check space status
    space_runtime = api.get_space_runtime(repo_id)
    print(f"Space Status: {space_runtime.stage}")
    
    # Try to check if build is successful
    # Note: logs are more tricky to get via API without proper permissions/token
    # But we can at least see if it's running.
except Exception as e:
    print(f"Error checking space: {e}")
