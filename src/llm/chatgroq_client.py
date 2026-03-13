from __future__ import annotations

import json
from typing import List, Tuple

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from src.config import settings


class SecurityAuditResponse(BaseModel):
    security_notes: str = Field(
        description="Short security review summary with concrete risks and fixes, no markdown fences"
    )


class OrchestratorPlanResponse(BaseModel):
    routing_plan: List[str] = Field(
        description="Ordered list of agents from: security, performance, fixer, test, docs"
    )
    risk_score: float = Field(description="Risk score between 0.0 and 1.0")
    reasoning: str = Field(description="Short explanation for the plan")


class PerformanceAuditResponse(BaseModel):
    performance_notes: str = Field(
        description="Concise performance analysis and practical optimization suggestions"
    )


class DocsSummaryResponse(BaseModel):
    docs: str = Field(
        description="Concise PR documentation summary with changes, risks, and tests"
    )


def _err_tag(exc: Exception) -> str:
    return f"fallback_error:{type(exc).__name__}:{str(exc)[:120]}"


def _fallback_test_suite(language: str) -> str:
    if language.lower() == "python":
        return "def test_smoke():\n    assert True\n"
    return "def test_smoke():\n    assert True\n"


def _fallback_security_notes() -> str:
    return (
        "No LLM security review available. Manual review recommended for auth, "
        "database, and secret handling."
    )


def _fallback_performance_notes() -> str:
    return (
        "No LLM performance review available. Manual review recommended for complexity "
        "and data-structure efficiency."
    )


def _fallback_docs() -> str:
    return (
        "Generated docs fallback.\n\n"
        "Summary:\n"
        "- Pipeline executed.\n"
        "- Manual review still recommended.\n"
    )


def _fallback_fixed_code(code: str) -> str:
    return f"# Auto-fix unavailable. Manual review required.\n\n{code}"


def _build_model() -> ChatGroq:
    api_key = settings.groq_api_key.strip().strip('"').strip("'")
    return ChatGroq(
        api_key=api_key,
        model=settings.groq_model,
        temperature=settings.groq_temperature,
    )


def _normalize_plan(plan: List[str]) -> List[str]:
    allowed = {"security", "performance", "fixer", "test", "docs"}
    deduped: List[str] = []
    seen = set()

    for item in plan:
        value = str(item).strip().lower()
        if value in allowed and value not in seen:
            deduped.append(value)
            seen.add(value)

    has_issue_agents = ("security" in seen) or ("performance" in seen)
    if has_issue_agents and "fixer" not in seen:
        insert_idx = 0
        if "performance" in deduped:
            insert_idx = max(insert_idx, deduped.index("performance") + 1)
        if "security" in deduped:
            insert_idx = max(insert_idx, deduped.index("security") + 1)
        deduped.insert(insert_idx, "fixer")
        seen.add("fixer")

    if "test" not in seen:
        deduped.append("test")
        seen.add("test")
    if "docs" not in seen:
        deduped.append("docs")

    return deduped


def generate_test_suite(code: str, language: str) -> Tuple[str, str]:
    if not settings.llm_enabled:
        return _fallback_test_suite(language), "fallback_disabled"
    if not settings.groq_api_key:
        return _fallback_test_suite(language), "fallback_no_key"

    try:
        model = _build_model()
        prompt = (
            "Return ONLY valid JSON with exactly one key: test_suite.\n"
            "No markdown fences. No prose.\n"
            "test_suite can be:\n"
            "- a single executable code string, or\n"
            "- an object whose values are executable test-code strings.\n"
            "Prefer pytest style when language is python.\n\n"
            f"Language: {language}\n\n"
            f"Code:\n{code}\n"
        )

        response = model.invoke(prompt)
        content = (response.content or "").strip()
        if not content:
            raise ValueError("Empty model response.")

        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:].strip()

        payload = json.loads(content)
        raw = payload.get("test_suite", "")

        if isinstance(raw, str):
            test_suite = raw.strip()
        elif isinstance(raw, dict):
            parts = []
            for key in sorted(raw.keys()):
                value = raw.get(key)
                if isinstance(value, str) and value.strip():
                    parts.append(value.strip())
            test_suite = "\n\n".join(parts).strip()
        else:
            raise ValueError("test_suite must be a string or dict of strings.")

        if not test_suite:
            raise ValueError("Missing or empty test_suite in JSON response.")
        if "```" in test_suite:
            raise ValueError("Model returned fenced output inside test_suite.")

        return test_suite, "chatgroq"
    except Exception as exc:
        return _fallback_test_suite(language), _err_tag(exc)


def generate_security_review(code: str, language: str) -> Tuple[str, str]:
    if not settings.llm_enabled:
        return _fallback_security_notes(), "fallback_disabled"
    if not settings.groq_api_key:
        return _fallback_security_notes(), "fallback_no_key"

    try:
        model = _build_model()
        structured_model = model.with_structured_output(SecurityAuditResponse)
        prompt = (
            "Review the code for security concerns.\n"
            "Rules:\n"
            "1) Return only structured output.\n"
            "2) No markdown fences.\n"
            "3) Mention concrete risks if present.\n"
            "4) Mention practical fixes briefly.\n"
            "5) Keep it concise and technical.\n\n"
            f"Language: {language}\n\n"
            f"Code:\n{code}\n"
        )
        result = structured_model.invoke(prompt)
        security_notes = result.security_notes.strip()

        if not security_notes:
            raise ValueError("Empty security review from model.")
        if "```" in security_notes:
            raise ValueError("Model returned fenced output.")

        return security_notes, "chatgroq"
    except Exception as exc:
        return _fallback_security_notes(), _err_tag(exc)


def generate_orchestrator_plan(code: str, language: str) -> Tuple[List[str], float, str, str]:
    if not settings.llm_enabled:
        return [], 0.0, "", "fallback_disabled"
    if not settings.groq_api_key:
        return [], 0.0, "", "fallback_no_key"

    try:
        model = _build_model()
        structured_model = model.with_structured_output(OrchestratorPlanResponse)
        prompt = (
            "You are a strict routing planner for a CI PR hardening pipeline.\n"
            "Return routing_plan, risk_score, and reasoning.\n"
            "routing_plan agents must be from: security, performance, fixer, test, docs.\n"
            "Always include test and docs.\n"
            "Use security when auth/db/secrets/security risks exist.\n"
            "Use performance for clear complexity/bottleneck issues.\n"
            "If security or performance is selected, include fixer before test/docs.\n"
            "risk_score must be between 0.0 and 1.0.\n\n"
            f"Language: {language}\n\n"
            f"Code:\n{code}\n"
        )
        result = structured_model.invoke(prompt)
        plan = _normalize_plan(result.routing_plan)
        risk_score = max(0.0, min(1.0, float(result.risk_score)))
        reasoning = (result.reasoning or "").strip()

        return plan, risk_score, reasoning, "chatgroq"
    except Exception as exc:
        return [], 0.0, "", _err_tag(exc)


def generate_performance_review(code: str, language: str) -> Tuple[str, str]:
    if not settings.llm_enabled:
        return _fallback_performance_notes(), "fallback_disabled"
    if not settings.groq_api_key:
        return _fallback_performance_notes(), "fallback_no_key"

    try:
        model = _build_model()
        structured_model = model.with_structured_output(PerformanceAuditResponse)
        prompt = (
            "Review code for performance and complexity.\n"
            "Return concise, practical notes.\n"
            "Mention bottlenecks and suggested optimization tactics.\n"
            "No markdown fences.\n\n"
            f"Language: {language}\n\n"
            f"Code:\n{code}\n"
        )
        result = structured_model.invoke(prompt)
        notes = result.performance_notes.strip()

        if not notes:
            raise ValueError("Empty performance review from model.")
        if "```" in notes:
            raise ValueError("Model returned fenced output.")

        return notes, "chatgroq"
    except Exception as exc:
        return _fallback_performance_notes(), _err_tag(exc)


def generate_docs_summary(
    code: str,
    language: str,
    security_notes: str,
    performance_notes: str,
    test_suite: str,
    validation_status: str,
) -> Tuple[str, str]:
    if not settings.llm_enabled:
        return _fallback_docs(), "fallback_disabled"
    if not settings.groq_api_key:
        return _fallback_docs(), "fallback_no_key"

    try:
        model = _build_model()
        structured_model = model.with_structured_output(DocsSummaryResponse)
        prompt = (
            "Create concise PR documentation.\n"
            "Include:\n"
            "- what changed\n"
            "- key security/performance observations\n"
            "- testing summary\n"
            "- deployment confidence note\n"
            "No markdown fences.\n\n"
            f"Language: {language}\n"
            f"Validation: {validation_status}\n\n"
            f"Code:\n{code}\n\n"
            f"Security notes:\n{security_notes}\n\n"
            f"Performance notes:\n{performance_notes}\n\n"
            f"Test suite:\n{test_suite}\n"
        )
        result = structured_model.invoke(prompt)
        docs = result.docs.strip()

        if not docs:
            raise ValueError("Empty docs summary from model.")
        if "```" in docs:
            raise ValueError("Model returned fenced output.")

        return docs, "chatgroq"
    except Exception as exc:
        return _fallback_docs(), _err_tag(exc)


def generate_fixed_code(
    code: str,
    language: str,
    security_notes: str,
    performance_notes: str,
) -> Tuple[str, str]:
    if not settings.llm_enabled:
        return _fallback_fixed_code(code), "fallback_disabled"
    if not settings.groq_api_key:
        return _fallback_fixed_code(code), "fallback_no_key"

    try:
        model = _build_model()

        issues = []
        if security_notes.strip():
            issues.append(f"Security issues:\n{security_notes}")
        if performance_notes.strip():
            issues.append(f"Performance issues:\n{performance_notes}")
        issues_text = "\n\n".join(issues) or "No specific issues found."

        prompt = (
            f"You are an expert {language} developer.\n"
            "Rewrite the code to fix all listed issues.\n"
            "Return only corrected code. No markdown fences. No explanation.\n\n"
            f"Original code:\n{code}\n\n"
            f"Issues to fix:\n{issues_text}\n\n"
            "Fixed code:"
        )

        result = model.invoke(prompt)
        fixed = (result.content or "").strip()

        if fixed.startswith("```"):
            lines = fixed.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            fixed = "\n".join(lines).strip()

        if not fixed:
            raise ValueError("Empty fixed code from model.")
        if "```" in fixed:
            raise ValueError("Model returned fenced output inside fixed code.")

        return fixed, "chatgroq"
    except Exception as exc:
        return _fallback_fixed_code(code), _err_tag(exc)