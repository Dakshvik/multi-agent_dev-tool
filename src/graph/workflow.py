from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from src.graph.routes import route_after_hitl, route_after_validator, route_from_orchestrator
from src.nodes.code_fixer import run_code_fixer
from src.nodes.orchestrator import run_orchestrator
from src.nodes.performance_optimizer import run_performance_optimizer
from src.nodes.security_auditor import run_security_auditor
from src.nodes.synthesizer import run_failed, run_synthesizer
from src.nodes.technical_writer import run_technical_writer
from src.nodes.test_engineer import run_test_engineer
from src.nodes.validator import run_validator
from src.policies.hitl_gate import run_hitl_gate


def build_graph():
    graph = StateGraph(dict)

    graph.add_node("orchestrator", run_orchestrator)
    graph.add_node("security", run_security_auditor)
    graph.add_node("performance", run_performance_optimizer)
    graph.add_node("fixer", run_code_fixer)
    graph.add_node("test", run_test_engineer)
    graph.add_node("docs", run_technical_writer)
    graph.add_node("validator", run_validator)
    graph.add_node("hitl", run_hitl_gate)
    graph.add_node("synthesizer", run_synthesizer)
    graph.add_node("failed", run_failed)

    graph.add_edge(START, "orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        route_from_orchestrator,
        {
            "security": "security",
            "performance": "performance",
            "fixer": "fixer",
            "test": "test",
            "docs": "docs",
            "hitl": "hitl",
            "synthesizer": "synthesizer",
        },
    )

    graph.add_edge("security", "validator")
    graph.add_edge("performance", "validator")
    graph.add_edge("fixer", "validator")
    graph.add_edge("test", "validator")
    graph.add_edge("docs", "validator")

    graph.add_conditional_edges(
        "validator",
        route_after_validator,
        {
            "security": "security",
            "performance": "performance",
            "fixer": "fixer",
            "test": "test",
            "docs": "docs",
            "hitl": "hitl",
            "synthesizer": "synthesizer",
            "failed": "failed",
        },
    )

    graph.add_conditional_edges(
        "hitl",
        route_after_hitl,
        {
            "synthesizer": "synthesizer",
            "failed": "failed",
        },
    )

    graph.add_edge("synthesizer", END)
    graph.add_edge("failed", END)

    return graph.compile()


def run_pipeline(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    app = build_graph()
    return app.invoke(initial_state)