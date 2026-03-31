import requests
import json
import sys

# Production URL
BASE_URL = "https://mohana17-crree-env.hf.space"

TASKS = {
    "1": ("task_1_easy", "Missing Null Check", {
        "issues": ["Potential NullPointerException when user is not found."],
        "severity": ["high"],
        "suggestions": ["Add a null check: return user.email if user else None"],
        "decision": "request_changes"
    }),
    "2": ("task_2_medium", "Logic Flaw & Edge Case", {
        "issues": ["Missing validation for negative price.", "Discount rate could be negative."],
        "severity": ["medium", "medium"],
        "suggestions": ["Add price validation.", "Clamp discount rate using max(0, rate)."],
        "decision": "request_changes"
    }),
    "3": ("task_3_hard", "SQL Injection & Performance", {
        "issues": ["SQL Injection vulnerability.", "Inefficient list extension loop."],
        "severity": ["critical", "medium"],
        "suggestions": ["Use parameterized queries (e.g., using ?).", "Use list comprehension for efficiency."],
        "decision": "request_changes"
    }),
    "4": ("task_4_security", "Weak Crypto & Hardcoded Creds", {
        "issues": ["Hardcoded API key.", "Insecure MD5 hashing."],
        "severity": ["critical", "critical"],
        "suggestions": ["Use environment variables for secrets.", "Use bcrypt or Argon2 for hashing."],
        "decision": "request_changes"
    }),
    "5": ("task_5_performance", "N+1 Query Problem", {
        "issues": ["N+1 query problem in loop.", "Potential SQL injection."],
        "severity": ["high", "medium"],
        "suggestions": ["Use SQL IN clause for bulk fetch.", "Use parameterized queries."],
        "decision": "request_changes"
    }),
    "6": ("task_6_architecture", "Tight Coupling", {
        "issues": ["Tight coupling to StripeGateway.", "Missing dependency injection."],
        "severity": ["medium", "medium"],
        "suggestions": ["Inject gateway dependency in constructor.", "Enable mocking for tests."],
        "decision": "request_changes"
    })
}

def test_production():
    print("====================================================")
    print("   CRREE Production Benchmark Tester")
    print("====================================================")
    print("Select a task to test (1-6):")
    for k, v in TASKS.items():
        print(f" {k}. {v[1]} ({v[0]})")
    
    choice = input("\nEnter choice (default is 3): ") or "3"
    if choice not in TASKS:
        print("Invalid choice.")
        return

    task_id, task_name, perfect_action = TASKS[choice]
    
    print(f"\n--- Testing Task: {task_name} ---")
    
    try:
        # 1. Reset with specific task
        print(f"\n[1/2] Initializing {task_id}...")
        resp = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id})
        if resp.status_code == 200:
            result = resp.json()
            obs = result.get("observation", result)
            print("✓ Environment Ready")
            print(f"DIFF TO REVIEW:\n{obs.get('diff')}")
        else:
            print(f"✗ Reset failed: {resp.status_code}")
            return

        # 2. Perform Perfect Review
        print(f"\n[2/2] Submitting Senior AI Review...")
        payload = {"action": perfect_action}
        resp = requests.post(f"{BASE_URL}/step", json=payload)
        
        if resp.status_code == 200:
            result = resp.json()
            obs = result.get("observation", {})
            print(f"\nBREAKDOWN:")
            print(f"- Bug Detection:      {obs.get('bug_detection', 0):.2f}")
            print(f"- Severity Accuracy:  {obs.get('severity_accuracy', 0):.2f}")
            print(f"- Suggestion Quality: {obs.get('suggestion_quality', 0):.2f}")
            print(f"- Security Hygiene:   {obs.get('security_score', 0):.2f}")
            
            print(f"\nRESOURCE PERFORMANCE:")
            print(f"- Latency: {obs.get('latency_ms', 0):.1f} ms")
            print(f"- Memory:  {obs.get('memory_mb', 0):.2f} MB")
            print("====================================================")
        else:
            print(f"✗ Evaluation failed: {resp.status_code}")
            print(resp.text)

    except Exception as e:
        print(f"\nError connecting to Space: {e}")

if __name__ == "__main__":
    test_production()
