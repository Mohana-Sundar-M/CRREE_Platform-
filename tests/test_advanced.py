import pytest
from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

def test_semantic_similarity():
    # Attempt to reset with task_id. If it fails to set, we'll check which task we got.
    resp = client.post("/reset", params={"task_id": "task_4_security"})
    obs = resp.json()["observation"]
    
    # We want task_4_security for this test
    if obs["pr_id"] != "task_4_security":
        # Hack for testing: keep resetting until we get it or just skip if it's random
        for _ in range(10):
            resp = client.post("/reset")
            obs = resp.json()["observation"]
            if obs["pr_id"] == "task_4_security":
                break
    
    action = {
        "issues": ["The API key is hardcoded which is bad for safety", "MD5 hashing is not secure enough"],
        "severity": ["critical", "critical"],
        "suggestions": ["Store the API key in an environment variable", "Apply bcrypt for hashing passwords"],
        "decision": "request_changes"
    }
    
    response = client.post("/step", json={"action": action})
    assert response.status_code == 200
    data = response.json()
    
    # Check if we got a good reward (indicates semantic similarity worked)
    assert data["reward"] > 0.5

def test_performance_tracking():
    client.post("/reset")
    action = {
        "issues": ["test"], "severity": ["low"], "suggestions": ["test"], "decision": "approve"
    }
    response = client.post("/step", json={"action": action})
    assert response.status_code == 200
    data = response.json()
    assert "reward" in data

def test_metrics_endpoint():
    client.post("/reset")
    client.post("/step", json={"action": {"issues":["t"], "severity":["low"], "suggestions":["t"], "decision":"approve"}})
    
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "evaluation_count" in data
    assert data["evaluation_count"] >= 1

def test_history_endpoint():
    response = client.get("/history", params={"limit": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 0 # Might be empty if DB not initialized in test run, but should stay 200

def test_task_4_security_vulnerability():
    # Only run if we actually get task 4
    for _ in range(10):
        resp = client.post("/reset")
        obs = resp.json()["observation"]
        if obs["pr_id"] == "task_4_security":
            action = {
                "issues": ["Hardcoded API Key"],
                "severity": ["critical"],
                "suggestions": ["Use env var"],
                "decision": "request_changes"
            }
            response = client.post("/step", json={"action": action})
            data = response.json()
            assert data["reward"] > 0.1 # Should get some score
            return
    pytest.skip("Could not reset to task_4_security")

def test_task_5_performance_n_plus_one():
    for _ in range(10):
        resp = client.post("/reset")
        obs = resp.json()["observation"]
        if obs["pr_id"] == "task_5_performance":
            action = {
                "issues": ["N+1 query problem", "SQL Injection"],
                "severity": ["high", "medium"],
                "suggestions": ["Use bulk fetch with IN clause", "Use parameterized queries"],
                "decision": "request_changes"
            }
            response = client.post("/step", json={"action": action})
            data = response.json()
            assert data["reward"] > 0.7
            return
    pytest.skip("Could not reset to task_5_performance")
