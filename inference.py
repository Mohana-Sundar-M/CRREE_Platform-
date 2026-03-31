import os
import json
import httpx
from openai import OpenAI
from typing import Dict

# Configuration from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN", "")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "dummy-key"),
    base_url=os.getenv("OPENAI_BASE_URL") # For local or custom endpoints
)

async def run_evaluation():
    tasks = ["task_1_easy", "task_2_medium", "task_3_hard", "task_4_security", "task_5_performance", "task_6_architecture"]
    scores = {}

    async with httpx.AsyncClient(base_url=API_BASE_URL) as env_client:
        for task_id in tasks:
            print(f"Evaluating {task_id}...")
            
            # 1. Reset environment
            response = await env_client.post("/reset", params={"task_id": task_id})
            if response.status_code != 200:
                print(f"Failed to reset: {response.text}")
                continue
            
            obs = response.json()
            
            # 2. Build Prompt
            prompt = f"""
You are a senior software reviewer. Review the following code diff:

Repo: {obs['repo_name']}
Context: {obs['context']}
Diff:
{obs['diff']}

Identify bugs, assess severity (low, medium, high, critical), and provide suggestions.
Respond ONLY in JSON format:
{{
    "issues": ["bug 1 description", ...],
    "severity": ["high", ...],
    "suggestions": ["fix suggestion 1", ...],
    "decision": "request_changes"
}}
"""

            # 3. Call Model
            try:
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                action_data = json.loads(completion.choices[0].message.content)
            except Exception as e:
                print(f"Model call failed: {e}")
                continue

            # 4. Step environment
            step_response = await env_client.post("/step", json=action_data)
            if step_response.status_code != 200:
                print(f"Step failed: {step_response.text}")
                continue
            
            result = step_response.json()
            scores[task_id] = result["reward"]["score"]
            print(f"Score for {task_id}: {result['reward']['score']}")

    # Output Results
    print("\nTask Scores:")
    for task, score in scores.items():
        print(f"{task.replace('task_', '').capitalize()}: {score}")
    
    if scores:
        avg = sum(scores.values()) / len(scores)
        print(f"\nAverage: {avg:.2f}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_evaluation())
