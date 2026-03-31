from typing import List, Dict, Optional, Any
from openenv.core.env_server.types import Action, Observation
from pydantic import Field, BaseModel

class CrreeAction(Action):
    """Action for the AI Code Review environment."""
    issues: List[str] = Field(..., description="Detected bugs or issues")
    severity: List[str] = Field(..., description="Severity for each issue: low, medium, high, critical")
    suggestions: List[str] = Field(..., description="Fix suggestions for each issue")
    decision: str = Field(..., description="Decision: approve or request_changes")

class CrreeObservation(Observation):
    """Observation from the AI Code Review environment."""
    pr_id: str = Field(..., description="Unique ID of the PR")
    repo_name: str = Field(..., description="Repository name")
    diff: str = Field(..., description="Code diff to review")
    context: str = Field(..., description="PR description/context")
    step_count: int = Field(..., description="Current step in episode")
    max_steps: int = Field(..., description="Maximum steps allowed")
    goal: str = Field(..., description="Review goal")
    reward: float = Field(0.0, description="Reward from the step")
    done: bool = Field(False, description="Whether the episode is done")
    bug_detection: float = Field(0.0, description="Bug detection score [0-1]")
    severity_accuracy: float = Field(0.0, description="Severity accuracy score [0-1]")
    suggestion_quality: float = Field(0.0, description="Suggestion quality score [0-1]")
    security_score: float = Field(0.0, description="Security hygiene score [0-1]")
    latency_ms: float = Field(0.0, description="Step latency in milliseconds")
    memory_mb: float = Field(0.0, description="Memory usage in MB")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class Reward(BaseModel):
    score: float
    breakdown: Dict[str, float]
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Resource usage metrics: latency, memory, cpu")

class Task(BaseModel):
    id: str
    name: str
    description: str
    diff: str
    ground_truth_issues: List[str]
    ground_truth_severity: List[str]
    expected_suggestions_keywords: List[List[str]]
    difficulty: str
