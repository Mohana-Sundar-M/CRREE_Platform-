import pytest
from fastapi.testclient import TestClient
from crree_env.server.app import app
from crree_env.models import CrreeAction as Action

client = TestClient(app)

def test_reset():
    response = client.post("/reset")
    assert response.status_code == 200
    data = response.json()
    assert "pr_id" in data
    assert "diff" in data

def test_reset_specific_task():
    response = client.post("/reset", params={"task_id": "task_1_easy"})
    assert response.status_code == 200
    data = response.json()
    assert data["pr_id"] == "task_1_easy"

def test_step_without_reset():
    # Fresh server instance in tests might need careful handling, 
    # but normally env state persists in test session if app is imported.
    action = {
        "issues": ["test"],
        "severity": ["low"],
        "suggestions": ["test"],
        "decision": "approve"
    }
    response = client.post("/step", json=action)
    # If reset wasn't called, it should fail or use default.
    # In our implementation, reset is usually needed.
    pass

def test_full_cycle_easy_task():
    # 1. Reset
    client.post("/reset", params={"task_id": "task_1_easy"})
    
    # 2. Step with correct action
    action = {
        "issues": ["Null pointer check in return user.email"],
        "severity": ["high"],
        "suggestions": ["Add null check before accessing email field"],
        "decision": "request_changes"
    }
    response = client.post("/step", json=action)
    assert response.status_code == 200
    data = response.json()
    
    assert data["reward"]["score"] > 0.5
    assert data["reward"]["breakdown"]["bug_detection"] > 0.8

def test_state():
    client.post("/reset", params={"task_id": "task_1_easy"})
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "task_1_easy"
    assert data["step_count"] == 0
