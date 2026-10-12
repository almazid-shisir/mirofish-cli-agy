"""
MiroFish MCP Server — Model Context Protocol interface for MiroFish Swarm Simulation Engine.
Enables Antigravity CLI (agy) and other MCP clients to control, monitor, and query simulations.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .cli import _default_project_name, _require_existing_files, _run_pipeline, cmd_doctor
from .config import Config
from .run_artifacts import RunStore
from .utils.logger import get_logger, set_console_level

# Direct all service logging to stderr so stdout is purely for MCP JSON-RPC
logger = get_logger("mirofish.mcp")
set_console_level(logging.WARNING)

mcp = FastMCP(
    "mirofish",
    instructions="MiroFish Swarm Intelligence & Social Simulation Prediction Engine for Antigravity CLI",
)

_store = RunStore()
_background_threads: Dict[str, threading.Thread] = {}
_thread_lock = threading.Lock()


def _background_worker(args: argparse.Namespace) -> None:
    """Worker function for running simulations asynchronously."""
    try:
        _run_pipeline(args)
    except Exception as exc:
        logger.error(f"Background simulation failed: {exc}", exc_info=True)


@mcp.tool()
def mirofish_start_simulation(
    files: List[str],
    requirement: str,
    max_rounds: int = 5,
    platform: str = "parallel",
    run_in_background: bool = True,
) -> Dict[str, Any]:
    """Start a MiroFish multi-agent predictive simulation on input documents.

    Args:
        files: List of file paths to ingest (.pdf, .md, .txt).
        requirement: Prediction prompt or requirement description (plain English).
        max_rounds: Number of simulation debate rounds (default: 5).
        platform: Social arena platform ('parallel', 'twitter', or 'reddit').
        run_in_background: If True, returns immediately with run_id while running in background.
                           If False, waits until completion and returns the final verdict.
    """
    for file_path in files:
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "error": f"File not found: {file_path}",
            }

    validated_files = [os.path.abspath(f) for f in files]
    output_dir = os.path.abspath(os.path.join(Config.UPLOAD_FOLDER, "runs"))

    args = SimpleNamespace(
        files=validated_files,
        requirement=requirement,
        platform=platform,
        max_rounds=max(1, min(max_rounds, 50)),
        output_dir=output_dir,
        json=True,
    )

    if run_in_background:
        # Pre-create run manifest so run_id is immediately available to caller
        project_name = _default_project_name(validated_files)
        manifest = _store.create(requirement, validated_files, project_name=project_name)
        run_id = manifest["run_id"]
        _store.update(run_id, status="running", task_message="Simulation started in background")

        # Launch thread
        worker_thread = threading.Thread(
            target=_background_worker,
            args=(args,),
            daemon=True,
            name=f"mirofish-{run_id}",
        )
        with _thread_lock:
            _background_threads[run_id] = worker_thread
        worker_thread.start()

        return {
            "status": "running",
            "run_id": run_id,
            "project_name": project_name,
            "requirement": requirement,
            "message": "Simulation started in background. Use mirofish_get_status to track progress.",
            "output_directory": _store.run_dir(run_id),
        }
    else:
        try:
            final_manifest = _run_pipeline(args)
            run_id = final_manifest["run_id"]
            verdict = _store.read_json(run_id, "report/verdict.json")
            return {
                "status": "completed",
                "run_id": run_id,
                "project_name": final_manifest.get("project_name"),
                "verdict": verdict,
                "artifacts": list(final_manifest.get("artifacts", {}).keys()),
            }
        except Exception as exc:
            return {
                "status": "failed",
                "error": str(exc),
            }


@mcp.tool()
def mirofish_get_status(run_id: str) -> Dict[str, Any]:
    """Get the current progress, status, and artifact overview of a simulation run.

    Args:
        run_id: Unique simulation run identifier (e.g. 'run_abc123').
    """
    try:
        manifest = _store.load(run_id)
    except FileNotFoundError:
        return {"status": "not_found", "run_id": run_id, "error": f"Run '{run_id}' not found."}

    artifacts = manifest.get("artifacts", {})
    return {
        "run_id": manifest.get("run_id"),
        "status": manifest.get("status"),
        "project_name": manifest.get("project_name"),
        "requirement": manifest.get("requirement"),
        "task_progress": manifest.get("task_progress", 0),
        "task_message": manifest.get("task_message", ""),
        "created_at": manifest.get("created_at"),
        "updated_at": manifest.get("updated_at"),
        "artifact_count": len(artifacts),
        "available_artifacts": list(artifacts.keys()),
        "error": manifest.get("error"),
    }


@mcp.tool()
def mirofish_list_runs(limit: int = 15) -> List[Dict[str, Any]]:
    """List recent MiroFish simulation runs with their status and metadata.

    Args:
        limit: Maximum number of recent runs to return (default: 15).
    """
    runs = _store.list(limit=limit)
    return [
        {
            "run_id": r.get("run_id"),
            "status": r.get("status"),
            "created_at": r.get("created_at"),
            "artifact_count": r.get("artifact_count", 0),
        }
        for r in runs
    ]


@mcp.tool()
def mirofish_get_verdict(run_id: str) -> Dict[str, Any]:
    """Retrieve the quantitative prediction verdict for a completed simulation run.

    Args:
        run_id: Unique simulation run identifier.
    """
    try:
        verdict = _store.read_json(run_id, "report/verdict.json")
    except FileNotFoundError:
        return {"error": f"Run '{run_id}' not found."}

    if not verdict:
        try:
            manifest = _store.load(run_id)
            status = manifest.get("status", "unknown")
        except FileNotFoundError:
            status = "not_found"
        return {
            "error": f"Verdict not available for run '{run_id}'. Current run status is '{status}'.",
        }
    return verdict


@mcp.tool()
def mirofish_get_report(run_id: str) -> Dict[str, Any]:
    """Retrieve the comprehensive markdown analysis report for a simulation run.

    Args:
        run_id: Unique simulation run identifier.
    """
    try:
        content = _store.read_text(run_id, "report/report.md")
    except FileNotFoundError:
        return {"error": f"Report not found for run '{run_id}'."}

    if not content:
        return {"error": f"Report not found for run '{run_id}'."}
    return {
        "run_id": run_id,
        "report_markdown": content,
    }


@mcp.tool()
def mirofish_get_knowledge_graph(run_id: str) -> Dict[str, Any]:
    """Retrieve the knowledge graph structure (nodes, edges, ontology) extracted from documents.

    Args:
        run_id: Unique simulation run identifier.
    """
    try:
        graph_data = _store.read_json(run_id, "graph/graph.json")
        graph_summary = _store.read_json(run_id, "graph/graph_summary.json")
        ontology = _store.read_json(run_id, "input/ontology.json")
    except FileNotFoundError:
        return {"error": f"Run '{run_id}' not found."}

    if not graph_data and not graph_summary:
        return {"error": f"Graph data not found for run '{run_id}'."}

    return {
        "run_id": run_id,
        "summary": graph_summary,
        "ontology": ontology,
        "node_count": len((graph_data or {}).get("nodes", [])),
        "edge_count": len((graph_data or {}).get("edges", [])),
        "sample_nodes": (graph_data or {}).get("nodes", [])[:10],
    }


@mcp.tool()
def mirofish_get_agents(run_id: str) -> Dict[str, Any]:
    """Retrieve the persona agents generated for the social simulation and their activity.

    Args:
        run_id: Unique simulation run identifier.
    """
    try:
        top_agents = _store.read_json(run_id, "simulation/top_agents.json")
        timeline = _store.read_json(run_id, "simulation/timeline.json")
    except FileNotFoundError:
        return {"error": f"Run '{run_id}' not found."}

    return {
        "run_id": run_id,
        "top_agents": top_agents or [],
        "rounds_recorded": len(timeline or []),
        "timeline_summary": timeline or [],
    }


@mcp.tool()
def mirofish_doctor() -> Dict[str, Any]:
    """Run MiroFish environment, CLI bridge, and configuration diagnostics."""
    valid_providers = ("claude-cli", "codex-cli", "agy-cli")
    provider = Config.LLM_PROVIDER
    provider_binaries = {
        "claude-cli": "claude",
        "codex-cli": "codex",
        "agy-cli": "agy",
    }
    binary_name = provider_binaries.get(provider, provider)

    import shutil

    binary_on_path = shutil.which(binary_name) is not None

    return {
        "engine": "MiroFish CLI AGY",
        "llm_provider": provider,
        "llm_provider_valid": provider in valid_providers,
        "provider_binary": binary_name,
        "binary_on_path": binary_on_path,
        "upload_folder": Config.UPLOAD_FOLDER,
        "data_dir": Config.DATA_DIR,
        "ready": provider in valid_providers and binary_on_path,
    }


def main() -> None:
    """Main entry point for running the MCP server."""
    # Run FastMCP via stdio
    mcp.run()


if __name__ == "__main__":
    main()
