---
title: Crree-env
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# 🛡️ CRREE Platform v2.0: AI Code Review Benchmark

**CRREE (Code Review & Risk Evaluation Environment)** is a production-grade OpenEnv benchmark designed to evaluate Large Language Models (LLMs) on their ability to perform senior-level software engineering code reviews.

## 🏗️ Technical Architecture

### 1. Unified Project Structure
The project follows the official **OpenEnv CLI Standard**, ensuring total compatibility with the evaluation framework.
- **`server/app.py`**: FastAPI entrypoint hosting the benchmark API.
- **`server/crree_env_environment.py`**: Core logic implementing the OpenEnv `Environment` interface.
- **`models.py`**: Data schemas for Actions, Observations, and Rewards.
- **`graders.py`**: The "Brain" - implements AI semantic similarity and static analysis.
- **`tasks.py`**: The "Challenge Suite" - 6 curated tasks with known vulnerabilities.

### 🧠 2. AI-Powered Grading Engine
Our grading engine moves beyond simple string matching:
- **Semantic Similarity**: Uses `sentence-transformers` (`paraphrase-MiniLM-L3-v2`) to compare AI suggestions with expert benchmarks using cosine similarity.
- **Static Analysis**: Integrated **Bandit** (Security) and **Radon** (Complexity) to verify that the AI is actually identifying real-world risks.
- **Resource Monitoring**: Tracks **Latency (ms)** and **Memory (MB)** for every single review step.

## 📊 Scoring Formula (FCS)
Every review is graded on a scale of **0.00 to 1.00**:
`Score = 0.4*BugDetection + 0.15*SeverityAccuracy + 0.35*SuggestionQuality + 0.1*SecurityHygiene`

## 🚀 How to Call the Benchmark API (Hugging Face)

### 1. Reset Environment (Start a Task)
Initialize the environment. You can optionally specify a `task_id`.
```bash
curl -X POST "https://mohana17-crree-env.hf.space/reset" \
     -H "Content-Type: application/json" \
     -d '{"task_id": "task_3_hard"}'
```

### 2. Execute a Step (Perform Review)
Submit the AI's review for evaluation.
```bash
curl -X POST "https://mohana17-crree-env.hf.space/step" \
     -H "Content-Type: application/json" \
     -d '{
       "action": {
         "issues": ["SQL Injection in get_user_data"],
         "severity": ["critical"],
         "suggestions": ["Use parameterized queries"],
         "decision": "request_changes"
       }
     }'
```

### 3. Retrieve Metrics
Get global performance averages.
```bash
curl -G "https://mohana17-crree-env.hf.space/metrics"
```

## 🧩 Task Difficulty Levels
- **Task 1 (Easy)**: Missing Null Checks.
- **Task 2 (Medium)**: Logic Flaws & Negative Value handling.
- **Task 3 (Hard)**: SQL Injection & Loop Optimizations.
- **Task 4 (Hard)**: Insecure Cryptography (MD5) & Secrets Management.
- **Task 5 (Hard)**: N+1 Query Performance bottleneck.
- **Task 6 (Medium)**: Architectural Coupling & Dependency Injection.

---
© 2026 CRREE Platform | Optimized for Senior AI Benchmarking.
