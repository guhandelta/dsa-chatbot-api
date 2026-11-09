"""Offline authoring checks for language-specific pathway evidence drafts.

This module never grades students or changes progress. A valid draft establishes
referential consistency; only independently validated assessments can later
support a stronger learning claim.
"""
import json
from pathlib import Path

from app.services import explain_pathway, learning_path, quiz

PILOT = Path(__file__).resolve().parents[2] / "data/curriculum/pathway-evidence-pilot.json"
EVIDENCE_ROLES = ("trace", "use", "choose", "transfer")


def load_pilot() -> dict:
    return json.loads(PILOT.read_text())


def audit(spec: dict) -> dict:
    """Check links and list missing assessment coverage without promoting it."""
    language = spec.get("language", "")
    errors: list[str] = []
    gaps: list[str] = []
    if language not in learning_path.LANGUAGE_LABELS:
        return {"errors": ["Unknown language"], "gaps": [], "evidence_links_complete": False}
    path_nodes = learning_path.nodes(language)
    nodes = {n["id"]: n for n in path_nodes}
    quiz_items = quiz.items(language)
    explain = {}
    if language == "javascript":
        explain = {u["id"]: u for u in explain_pathway.authored()["units"]}
    seen: set[str] = set()
    available_capabilities: set[str] = set()
    for unit in spec.get("units", []):
        unit_id = unit.get("id", "")
        if unit_id in seen or not unit_id.startswith(f"explain:{language}:"):
            errors.append(f"Invalid or duplicate unit: {unit_id}")
        if unit_id not in explain:
            errors.append(f"Missing language-owned Explain unit: {unit_id}")
        if not set(unit.get("prerequisite_ids", [])) <= seen:
            errors.append(f"Out-of-order prerequisite: {unit_id}")
        if not set(unit.get("external_prerequisite_nodes", [])) <= nodes.keys():
            errors.append(f"Missing path prerequisite: {unit_id}")
        assessment_node = explain.get(unit_id, {}).get("assessment_node_id")
        if assessment_node in nodes:
            for prerequisite in unit.get("external_prerequisite_nodes", []):
                if prerequisite in nodes and nodes[prerequisite]["order"] >= nodes[assessment_node]["order"]:
                    errors.append(f"Path prerequisite is not earlier: {unit_id}/{prerequisite}")
        capabilities = set(unit.get("capabilities", []))
        if not capabilities or not all(isinstance(c, str) and c.strip() for c in capabilities):
            errors.append(f"Missing capability: {unit_id}")
        if len(capabilities) != len(unit.get("capabilities", [])):
            errors.append(f"Duplicate capability: {unit_id}")
        if unit_id in explain and set(unit.get("prerequisite_ids", [])) != set(explain[unit_id]["prerequisite_ids"]):
            errors.append(f"Prerequisites disagree with Explain: {unit_id}")
        activities = {a["id"]: a for a in explain.get(unit_id, {}).get("activities", [])}
        families: set[str] = set()
        assessment_ids: set[str] = set()

        def check_ref(ref: dict, label: str) -> bool:
            source, item_id = ref.get("source"), ref.get("id")
            if source == "explain":
                if item_id not in activities:
                    errors.append(f"Missing Explain activity: {unit_id}/{label}/{item_id}")
                    return False
                return False  # Explain activities are currently ungraded.
            if source == "quiz":
                item = quiz_items.get(item_id)
                if item is None or item.get("node_id") not in nodes:
                    errors.append(f"Missing language quiz item: {unit_id}/{label}/{item_id}")
                    return False
                if assessment_node and item["node_id"] != assessment_node:
                    errors.append(f"Quiz item belongs to another node: {unit_id}/{label}/{item_id}")
                expected_roles = {"trace": {"trace"}, "use": {"implement", "debug"},
                                  "choose": {"explain"}, "transfer": {"implement", "explain"}}
                if label in expected_roles and item.get("role") not in expected_roles[label]:
                    errors.append(f"Quiz role does not match evidence: {unit_id}/{label}/{item_id}")
                return bool(ref.get("independent"))
            errors.append(f"Unknown evidence source: {unit_id}/{label}")
            return False

        for role in EVIDENCE_ROLES:
            ref = unit.get("evidence", {}).get(role)
            if not isinstance(ref, dict):
                gaps.append(f"{unit_id}: missing {role} evidence")
                continue
            independent = check_ref(ref, role)
            family = ref.get("family")
            if not isinstance(family, str) or not family.strip() or family in families:
                errors.append(f"Missing or reused evidence family: {unit_id}/{role}")
            families.add(family)
            if ref.get("source") == "explain" and ref.get("independent"):
                errors.append(f"Ungraded activity claims independence: {unit_id}/{role}")
            if ref.get("source") == "quiz":
                if ref.get("id") in assessment_ids:
                    errors.append(f"Reused assessment item: {unit_id}/{role}")
                assessment_ids.add(ref.get("id"))
            if not independent:
                gaps.append(f"{unit_id}: {role} needs an independent assessment")
        application = unit.get("application")
        if not isinstance(application, dict):
            gaps.append(f"{unit_id}: missing application")
        else:
            check_ref(application, "application")
            if not application.get("requires_capabilities"):
                errors.append(f"Application lacks capability requirements: {unit_id}")
            if not set(application.get("requires_capabilities", [])) <= available_capabilities | capabilities:
                errors.append(f"Application uses untaught capability: {unit_id}")
        recovery = unit.get("recovery", [])
        if not recovery:
            gaps.append(f"{unit_id}: missing recovery activities")
        for index, ref in enumerate(recovery):
            if not ref.get("when"):
                errors.append(f"Recovery lacks trigger: {unit_id}/{index}")
            check_ref(ref, f"recovery-{index}")
        seen.add(unit_id)
        available_capabilities.update(capabilities)
    if not seen:
        errors.append("No units")
    return {"errors": errors, "gaps": gaps, "evidence_links_complete": not errors and not gaps}
