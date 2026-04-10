# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the Crree Env Environment.

This module creates an HTTP server that exposes the CrreeEnvironment
over HTTP and WebSocket endpoints, compatible with EnvClient.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - WS /ws: WebSocket endpoint for persistent sessions

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

    # Or run directly:
    python -m server.app
"""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

from models import CrreeAction, CrreeObservation
from server.crree_env_environment import CrreeEnvironment


# Create the app with web interface and README integration
app = create_app(
    CrreeEnvironment,
    CrreeAction,
    CrreeObservation,
    env_name="crree_env",
    max_concurrent_envs=1,  # increase this number to allow more concurrent WebSocket sessions
)

@app.get("/metrics")
async def get_metrics_endpoint():
    from db import get_metrics
    return get_metrics()

@app.get("/history")
async def get_history_endpoint(limit: int = 10):
    from db import get_history
    return get_history(limit)


def main(host: str = "0.0.0.0", port: int = 7860):
    """
    Entry point for direct execution.
    """
    import uvicorn
    # Use string reference to avoid issues with global imports during multi-mode loading
    uvicorn.run("server.app:app", host=host, port=port, reload=False)


if __name__ == '__main__':
    main()
