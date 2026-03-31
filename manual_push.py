from huggingface_hub import HfApi
import os

api = HfApi()
repo_id = "Mohana17/Crree-env"
folder_path = r"c:\Users\mohan\Documents\AntiGravity\crree_env"

ignore_patterns = [".venv*", ".pytest_cache*", "__pycache__", ".git", "eval_history.db"]

try:
    api.upload_folder(
        folder_path=folder_path,
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=ignore_patterns
    )
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
