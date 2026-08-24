# NetSage AI

NetSage AI is an AI-assisted Cisco/Packet Tracer troubleshooting helper with:
- 30 structured troubleshooting cases
- deterministic rule checker
- structured LLM diagnosis
- human-in-the-loop Accept / Edit / Reject workflow
- audit logging
- dashboard metrics and charts
- simulated lab deployment (no real network device is modified)

## Project structure

```text
NetSage_AI/
├── data/
│   └── cases.csv
├── prompts/
│   └── diagnose_prompt.md
├── src/
│   ├── __init__.py
│   ├── checker.py
│   ├── engine.py
│   └── app.py
├── docs/
│   └── model_audit_log.md
├── .env.example
├── requirements.txt
└── README.md
```

## Run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run src/app.py
```

The application works without an API key using the built-in deterministic fallback.
For real LLM diagnosis, copy `.env.example` to `.env`, set `OPENAI_API_KEY`, and restart Streamlit.

## Safety

The "Approve & Deploy" action is intentionally a simulated lab deployment. It records the approval in the audit log but does not connect to or change a Cisco device. This preserves the project's mandatory human-review gate.

## Required workflow

1. Select a case.
2. Review symptom, topology and show output.
3. Run deterministic checks.
4. Run AI diagnosis.
5. Review evidence and proposed commands.
6. Accept, edit, or reject.
7. Record the decision.
8. Verify the case and inspect dashboard/audit metrics.
