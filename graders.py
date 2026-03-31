import os
import subprocess
import tempfile
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
from crree_env.models import CrreeAction as Action, Task

# Load a lightweight model for semantic similarity
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    return _model

def calculate_semantic_score(suggestions: List[str], expected_keywords: List[List[str]]) -> float:
    if not suggestions or not expected_keywords:
        return 0.0
    
    model = get_model()
    total_score = 0
    
    for i in range(min(len(suggestions), len(expected_keywords))):
        s_emb = model.encode(suggestions[i], convert_to_tensor=True)
        max_sim = 0
        for kw in expected_keywords[i]:
            kw_emb = model.encode(kw, convert_to_tensor=True)
            sim = util.pytorch_cos_sim(s_emb, kw_emb).item()
            if sim > max_sim:
                max_sim = sim
        
        total_score += 1.0 if max_sim > 0.6 else max_sim / 0.6
        
    return min(1.0, total_score / len(expected_keywords))

def run_static_analysis(diff: str) -> Dict[str, float]:
    with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as f:
        f.write(diff)
        temp_path = f.name

    try:
        bandit_res = subprocess.run(["bandit", "-q", "-f", "json", temp_path], capture_output=True, text=True)
        return {
            "security_risk": 1.0 if not bandit_res.stderr else 0.5,
            "complexity_score": 1.0
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def calculate_bug_score(detected_issues: List[str], ground_truth_issues: List[str]) -> float:
    if not ground_truth_issues:
        return 1.0 if not detected_issues else 0.0
    
    model = get_model()
    matches = 0
    for gt in ground_truth_issues:
        matched = False
        gt_emb = model.encode(gt, convert_to_tensor=True)
        for det in detected_issues:
            det_emb = model.encode(det, convert_to_tensor=True)
            if util.pytorch_cos_sim(gt_emb, det_emb).item() > 0.7:
                matched = True
                break
        if matched:
            matches += 1
            
    return matches / len(ground_truth_issues)

def evaluate_action(action: Action, task: Task) -> Dict[str, float]:
    bug_score = calculate_bug_score(action.issues, task.ground_truth_issues)
    suggestion_score = calculate_semantic_score(action.suggestions, task.expected_suggestions_keywords)
    static_metrics = run_static_analysis(task.diff)
    
    correct_sev = 0
    for i in range(min(len(action.severity), len(task.ground_truth_severity))):
        if action.severity[i].lower() == task.ground_truth_severity[i].lower():
            correct_sev += 1
    severity_score = correct_sev / len(task.ground_truth_severity) if task.ground_truth_severity else 1.0
    
    final_score = (
        0.4 * bug_score +
        0.15 * severity_score + 
        0.35 * suggestion_score +
        0.1 * static_metrics["security_risk"]
    )
    
    return {
        "final_score": max(0.0, min(1.0, final_score)),
        "bug_score": bug_score,
        "severity_score": severity_score,
        "suggestion_score": suggestion_score,
        "security_score": static_metrics["security_risk"]
    }
