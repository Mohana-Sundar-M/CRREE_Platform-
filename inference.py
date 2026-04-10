import os
import json
import httpx
from openai import OpenAI
from typing import Dict

# Configuration from environment variables
# STRICT REQUIREMENTS: Use os.environ to ensure platform-provided variables are used
API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)

def validate_llm_connection():
    """Forces an initial LLM call to ensure the LiteLLM proxy detects usage."""
    print("Verifying LLM Proxy connection...", flush=True)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Test connection. Respond with 'OK'."}],
            max_tokens=5
        )
        print(f"LLM Proxy Working [OK]: {response.choices[0].message.content.strip()}", flush=True)
    except Exception as e:
        print(f"LLM Proxy Failed [ERROR]: {e}", flush=True)

# Mandatory startup call to hit the proxy
validate_llm_connection()

async def run_evaluation():
    # Unified task list based on repo contents
    tasks = ["task_1_easy", "task_2_medium", "task_3_hard", "task_4_security", "task_5_performance", "task_6_architecture"]
    scores = {}

    async with httpx.AsyncClient(base_url=API_BASE_URL) as env_client:
        for task_id in tasks:
            print(f"[START] task={task_id}", flush=True)
            print(f"Evaluating {task_id}...", flush=True)
            
            try:
                # 1. Reset environment
                response = await env_client.post("/reset", params={"task_id": task_id})
                if response.status_code != 200:
                    print(f"Failed to reset: {response.text}", flush=True)
                    print(f"[END] task={task_id} score=0.01 steps=0", flush=True)
                    continue
                
                data = response.json()
                obs = data.get("observation", data)
                
                # 2. Build Prompt
                prompt = f"""
You are a senior software reviewer. Review the following code diff:

Repo: {obs.get('repo_name', 'Unknown')}
Context: {obs.get('context', 'No context available')}
Diff:
{obs.get('diff', 'No diff provided')}

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
                    print(f"Model call failed: {e}", flush=True)
                    print(f"[END] task={task_id} score=0.01 steps=0", flush=True)
                    continue

                # 4. Step environment
                step_response = await env_client.post("/step", json=action_data)
                if step_response.status_code != 200:
                    print(f"Step failed: {step_response.text}", flush=True)
                    print(f"[END] task={task_id} score=0.01 steps=0", flush=True)
                    continue
                
                result = step_response.json()
                # Handle nested reward if present
                reward_data = result.get("reward", result)
                # Robust score extraction with fallback to 0.01
                score = 0.01
                if isinstance(reward_data, dict):
                    score = reward_data.get("score", 0.01)
                elif isinstance(reward_data, (int, float)):
                    score = float(reward_data)
                
                # FINAL MANDATORY CLAMPING
                score = max(0.01, min(0.99, score))
                scores[task_id] = score
                
                print(f"[STEP] step=1 reward={score}", flush=True)
                print(f"Score for {task_id}: {score}", flush=True)
                print(f"[END] task={task_id} score={score} steps=1", flush=True)
            except Exception as e:
                print(f"Unexpected error evaluating {task_id}: {e}", flush=True)
                print(f"[END] task={task_id} score=0.01 steps=0", flush=True)

    # Output Results
    print("\nTask Scores:", flush=True)
    for task, score in scores.items():
        print(f"{task.replace('task_', '').capitalize()}: {score}", flush=True)
    
    if scores:
        avg = sum(scores.values()) / len(scores)
        print(f"\nAverage: {avg:.2f}", flush=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_evaluation())
