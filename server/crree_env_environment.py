import random
from uuid import uuid4
from typing import Optional

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from crree_env.models import CrreeAction, CrreeObservation
from crree_env.tasks import TASKS
from crree_env.reward import compute_reward
from crree_env.utils import monitor

class CrreeEnvironment(Environment):
    """AI Code Review Environment - OpenEnv v2.0."""
    
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_task = None
        self.max_steps = 1

    def reset(self, **kwargs) -> CrreeObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        
        task_id = kwargs.get("task_id")
        if task_id:
            self.current_task = next((t for t in TASKS if t.id == task_id), None)
        else:
            self.current_task = random.choice(TASKS)
            
        if not self.current_task:
            self.current_task = TASKS[0] 
            
        return CrreeObservation(
            pr_id=self.current_task.id,
            repo_name="demo-repo",
            diff=self.current_task.diff,
            context=self.current_task.description,
            step_count=0,
            max_steps=self.max_steps,
            goal="Identify all bugs, assess severity, and provide fix suggestions.",
            done=False,
            reward=0.0
        )

    def step(self, action: CrreeAction) -> CrreeObservation:
        if not self.current_task:
             self.current_task = TASKS[0] # Auto-reset to first task if missing
            
        monitor.start()
        self._state.step_count += 1
        
        reward_obj = compute_reward(action, self.current_task)
        done = self._state.step_count >= self.max_steps
        
        return CrreeObservation(
            pr_id=self.current_task.id,
            repo_name="demo-repo",
            diff=self.current_task.diff,
            context=self.current_task.description,
            step_count=self._state.step_count,
            max_steps=self.max_steps,
            goal="Review completed." if done else "Continue review.",
            done=done,
            reward=reward_obj.score,
            metadata={
                "breakdown": reward_obj.breakdown,
                "performance": reward_obj.performance_metrics
            }
        )

    @property
    def state(self) -> State:
        return self._state
