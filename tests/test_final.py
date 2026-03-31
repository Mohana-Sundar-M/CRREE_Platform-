import pytest
from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

def get_observation_and_reward(response):
    data = response.json()
    # Support both wrapped and flat response depending on OpenEnv version
    obs = data.get("observation", data)
    reward = data.get("reward", obs.get("reward", 0.0))
    return obs, reward

def test_environment_reset():
    response = client.post("/reset")
    assert response.status_code == 200
    obs, _ = get_observation_and_reward(response)
    assert "pr_id" in obs
    assert "diff" in obs

def test_semantic_grading_logic():
    # We'll just take whatever task we get from reset
    resp = client.post("/reset")
    obs, _ = get_observation_and_reward(resp)
    task_id = obs["pr_id"]
    
    # Simple action for testing (might not get high score for all tasks, but checking for no errors)
    action = {
        "issues": ["test issue"],
        "severity": ["medium"],
        "suggestions": ["use a fix"],
        "decision": "request_changes"
    }
    
    response = client.post("/step", json={"action": action})
    assert response.status_code == 200
    data = response.json()
    assert "reward" in data
    # At least we shouldn't get 0 if it's the right task and we guessed right, 
    # but here we just check it runs without error.

def test_metrics_persistence():
    # Run a full step to save to DB
    client.post("/reset")
    client.post("/step", json={"action": {
        "issues": ["t"], "severity": ["low"], "suggestions": ["t"], "decision": "approve"
    }})
    
    response = client.get("/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["evaluation_count"] >= 1

def test_all_tasks_loadable():
    from tasks import TASKS
    assert len(TASKS) == 6

def test_advanced_security_grading():
    # Hunt for task 4 specifically
    found = False
    for _ in range(20):
        resp = client.post("/reset")
        obs, _ = get_observation_and_reward(resp)
        if obs["pr_id"] == "task_4_security":
            found = True
            action = {
                "issues": ["Hardcoded API Key", "Weak MD5 Hashing"],
                "severity": ["critical", "critical"],
                "suggestions": ["Use OS environment variables", "Use bcrypt hashing library"],
                "decision": "request_changes"
            }
            response = client.post("/step", json={"action": action})
            _, reward = get_observation_and_reward(response)
            assert reward > 0.6
            break
    if not found:
        pytest.skip("Could not randomly hit task_4_security")
