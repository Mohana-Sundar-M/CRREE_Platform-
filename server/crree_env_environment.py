import random
from typing import Optional, Dict, Any, List
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from models import CrreeAction, CrreeObservation
from tasks import TASKS
from reward import compute_reward
from utils import monitor
from db import save_evaluation

# Global state for the environment (single-agent benchmark)
_CURRENT_TASK = None
_MAX_STEPS = 1

class CrreeEnvironment(Environment):
    """AI Code Review Environment - OpenEnv v2.0."""
    
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)

    @property
    def state(self) -> State:
        return self._state

    def reset(self, **kwargs) -> CrreeObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        
        global _CURRENT_TASK
        task_id = kwargs.get("task_id")
        if task_id:
            _CURRENT_TASK = next((t for t in TASKS if t.id == task_id), None)
        else:
            _CURRENT_TASK = random.choice(TASKS)
            
        if not _CURRENT_TASK:
            _CURRENT_TASK = TASKS[0] 
            
        return CrreeObservation(
            pr_id=_CURRENT_TASK.id,
            repo_name="demo-repo",
            diff=_CURRENT_TASK.diff,
            context=_CURRENT_TASK.description,
            step_count=0,
            max_steps=_MAX_STEPS,
            goal="Identify all bugs, assess severity, and provide fix suggestions.",
            done=False,
            reward=0.01
        )

    def step(self, action: CrreeAction) -> CrreeObservation:
        global _CURRENT_TASK
        if not _CURRENT_TASK:
             _CURRENT_TASK = TASKS[0] 
            
        monitor.start()
        self._state.step_count += 1
        
        reward_obj = compute_reward(action, _CURRENT_TASK)
        done = self._state.step_count >= _MAX_STEPS
        
        # Save to database for metrics/history
        save_evaluation(_CURRENT_TASK.id, reward_obj.score, reward_obj.breakdown, reward_obj.performance_metrics)
        
        return CrreeObservation(
            pr_id=_CURRENT_TASK.id,
            repo_name="demo-repo",
            diff=_CURRENT_TASK.diff,
            context=_CURRENT_TASK.description,
            step_count=self._state.step_count,
            max_steps=_MAX_STEPS,
            goal="Review completed." if done else "Continue review.",
            done=done,
            reward=reward_obj.score,
            bug_detection=reward_obj.breakdown.get("bug_detection", 0.01),
            severity_accuracy=reward_obj.breakdown.get("severity_accuracy", 0.01),
            suggestion_quality=reward_obj.breakdown.get("suggestion_quality", 0.01),
            security_score=reward_obj.breakdown.get("security_score", 0.01),
            latency_ms=reward_obj.performance_metrics.get("latency_ms", 0.01),
            memory_mb=reward_obj.performance_metrics.get("memory_mb", 0.01),
            metadata=reward_obj.breakdown
        )
