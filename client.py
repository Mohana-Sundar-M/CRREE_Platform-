from typing import Dict, Any
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State
from .models import CrreeAction, CrreeObservation

class CrreeEnv(EnvClient[CrreeAction, CrreeObservation, State]):
    """Client for the CRREE AI Code Review Environment."""

    def _step_payload(self, action: CrreeAction) -> Dict[str, Any]:
        return action.model_dump()

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[CrreeObservation]:
        obs_data = payload.get("observation", payload) # Support both wrapped and direct
        observation = CrreeObservation(**obs_data)
        
        return StepResult(
            observation=observation,
            reward=payload.get("reward", observation.reward),
            done=payload.get("done", observation.done),
        )

    def _parse_state(self, payload: Dict[str, Any]) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
