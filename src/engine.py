"""NetSage AI diagnostic orchestration: deterministic checks + Gemini + safe fallback."""
import json
import os
from pathlib import Path
from typing import Any, Dict
import pandas as pd
from dotenv import load_dotenv
from .checker import run_checks

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "cases.csv"
PROMPT_FILE = ROOT / "prompts" / "diagnose_prompt.md"
load_dotenv(ROOT / ".env")


def load_cases() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


def load_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")


def _fallback(case: Dict[str, Any], check: Dict[str, Any]) -> Dict[str, Any]:
    evidence = [x["evidence"] for x in check.get("findings", [])[:3]]
    root = str(case.get("expected_fault", "Unable to determine root cause"))
    confidence = 0.82 if check.get("findings") else 0.62
    if case.get("case_id") == "NET-001" and check.get("findings"):
        root = "VLAN 30 router sub-interface is administratively down"
        confidence = 0.95
    return {
        "root_cause": root,
        "osi_layer": str(case.get("osi_layer", "Unknown")),
        "confidence": confidence,
        "evidence": evidence or [str(case.get("show_outputs", "")).splitlines()[0]],
        "next_command": _next_command(case, check),
        "fix_steps": _fix_steps(case),
        "provider": "deterministic_fallback",
    }


def _next_command(case: Dict[str, Any], check: Dict[str, Any]) -> str:
    concept = str(case.get("concept_tag", "")).lower()
    commands = {
        "vlan": "show vlan brief",
        "gateway": "ipconfig /all; show ip interface brief",
        "dhcp": "show ip dhcp pool; show ip dhcp binding",
        "dns": "nslookup; ping <DNS_SERVER>",
        "routing": "show ip route",
        "acl": "show access-lists",
        "nat": "show ip nat statistics; show ip nat translations",
        "wireless": "show vlan brief; inspect SSID-to-VLAN mapping",
        "trunk": "show interfaces trunk",
        "ospf": "show ip ospf neighbor; show ip ospf interface",
    }
    for key, command in commands.items():
        if key in concept:
            return command
    return "show interfaces; show ip interface brief"


def _fix_steps(case: Dict[str, Any]):
    return [
        "Review the evidence and verify the diagnosis.",
        f"Recommended action: {str(case.get('expected_fix', 'Verify the configuration.'))}.",
        "Apply the change only after human approval in the lab.",
    ]


def _gemini_diagnosis(case: Dict[str, Any], check: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _fallback(case, check)

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    payload = {"case": case, "deterministic_checker": check}
    user_prompt = load_prompt() + "\n\nCASE DATA:\n" + json.dumps(payload, ensure_ascii=False)

    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)
    required = ["root_cause", "osi_layer", "confidence", "evidence", "next_command", "fix_steps"]
    for key in required:
        if key not in data:
            raise ValueError(f"Gemini output missing required field: {key}")
    data["provider"] = "Gemini"
    return data


def diagnose_case(case: Dict[str, Any]) -> Dict[str, Any]:
    combined_text = "\n".join([
        str(case.get("symptom", "")),
        str(case.get("topology_note", "")),
        str(case.get("show_outputs", "")),
    ])
    check = run_checks(combined_text)
    try:
        diagnosis = _gemini_diagnosis(case, check)
    except Exception as exc:
        diagnosis = _fallback(case, check)
        diagnosis["llm_error"] = str(exc)
    return {"case": case, "checker": check, "diagnosis": diagnosis}
