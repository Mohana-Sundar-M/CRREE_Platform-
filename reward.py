from crree_env.models import Reward, CrreeAction as Action, Task
from crree_env.graders import evaluate_action
from crree_env.utils import monitor

def compute_reward(action: Action, task: Task) -> Reward:
    perf = monitor.stop()
    eval_results = evaluate_action(action, task)
    
    return Reward(
        score=eval_results["final_score"],
        breakdown={
            "bug_detection": eval_results["bug_score"],
            "severity_accuracy": eval_results["severity_score"],
            "suggestion_quality": eval_results["suggestion_score"],
            "security_score": eval_results.get("security_score", 0.0)
        },
        performance_metrics=perf
    )
