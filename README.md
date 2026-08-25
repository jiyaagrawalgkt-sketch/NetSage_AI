# NetSage AI

## AI-Assisted Network Troubleshooting & Diagnosis Platform

NetSage AI is an AI-assisted network troubleshooting platform designed to help users diagnose common networking problems using structured case data, deterministic rule-based checks, network evidence, and optional Generative AI analysis.

The system combines traditional troubleshooting logic with AI-assisted reasoning while keeping a **Human-in-the-Loop (HITL)** approval process before any remediation is considered deployable.

The application provides an interactive Streamlit dashboard for:

- Network case selection
- Evidence inspection
- Deterministic diagnosis
- AI-assisted diagnosis
- Root-cause identification
- OSI-layer mapping
- Confidence estimation
- Recommended verification commands
- Proposed remediation
- Human approval, editing, or rejection
- Audit logging
- Analytics and visualization

> **Important:** NetSage AI operates in simulation mode. It does not directly connect to or modify physical network devices.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [How NetSage AI Works](#how-netsage-ai-works)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Application Sections](#application-sections)
- [Deterministic Diagnosis](#deterministic-diagnosis)
- [Gemini AI Integration](#gemini-ai-integration)
- [Human-in-the-Loop Review](#human-in-the-loop-review)
- [Auditability and Safety](#auditability-and-safety)
- [Analytics](#analytics)
- [Sample Network Case](#sample-network-case)
- [Network Concepts Covered](#network-concepts-covered)
- [Testing](#testing)
- [Security](#security)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Learning Outcomes](#learning-outcomes)
- [Conclusion](#conclusion)
- [Author](#author)
- [Repository](#repository)
- [License](#license)

---

## Overview

Network troubleshooting often requires examining symptoms, topology information, device outputs, configuration evidence, and protocol behavior before identifying the root cause.

NetSage AI provides a structured environment where these troubleshooting steps can be represented as a repeatable workflow.

The platform follows a hybrid approach:

```text
Network Case
     |
     v
Evidence Collection
     |
     v
Deterministic Rule Checks
     |
     +----------------------+
     |                      |
     v                      v
Rule-Based Findings     Optional Gemini AI
     |                      |
     +----------+-----------+
                |
                v
         Diagnosis Result
                |
                v
        Human Review Gate
                |
       +--------+--------+
       |        |        |
       v        v        v
    Approve    Edit    Reject
       |
       v
     Audit
```

---

## Problem Statement

Network issues can have similar symptoms while having completely different root causes.

For example, a connectivity problem may be caused by:

- Incorrect VLAN configuration
- Interface failure
- Routing problems
- ACL restrictions
- DHCP failure
- NAT configuration
- Incorrect default gateway
- DNS issues
- Trunk configuration
- Inter-VLAN routing problems

Traditional troubleshooting usually requires a network engineer to manually inspect evidence and determine the most likely cause.

NetSage AI aims to assist this process by providing:

- Structured case analysis
- Evidence-based diagnosis
- Deterministic troubleshooting checks
- Optional AI-assisted reasoning
- OSI-layer identification
- Verification commands
- Suggested remediation
- Human review
- Auditability
- Analytics

---

## Objectives

The main objectives of NetSage AI are:

- Build an interactive network troubleshooting dashboard.
- Provide structured network troubleshooting cases.
- Analyze CLI and network evidence.
- Perform deterministic troubleshooting checks.
- Integrate Generative AI for optional diagnosis assistance.
- Identify probable root causes.
- Map network issues to OSI layers.
- Recommend verification commands.
- Suggest possible remediation steps.
- Provide a Human-in-the-Loop review process.
- Maintain audit information for reviewed decisions.
- Provide analytics and visualizations.
- Keep remediation in simulation mode for safety.

---

## Key Features

### 1. Interactive Dashboard

NetSage AI provides a modern Streamlit dashboard for exploring network troubleshooting cases, including:

- Case selection
- Network evidence
- Severity information
- OSI-layer information
- Issue classification
- Diagnostic results
- AI-assisted analysis
- Verification commands
- Proposed remediation
- Review actions
- Analytics
- Audit information

### 2. Network Case Management

The application uses structured troubleshooting cases. Each case can contain:

- Case ID
- Network symptom
- Issue type
- Severity
- OSI layer
- Concept tag
- Topology information
- CLI evidence
- Expected troubleshooting direction

**Example:**

```
Case ID: NET-001
Issue: Inter-VLAN Routing Failure
Severity: High
OSI Layer: Layer 3
Evidence: Router sub-interface is administratively down.
```

### 3. Deterministic Diagnosis Engine

NetSage AI includes a rule-based diagnostic layer that checks network evidence for known troubleshooting patterns, including:

- Interface status problems
- VLAN configuration issues
- DHCP failures
- Routing problems
- ACL restrictions
- NAT issues
- DNS problems
- Default gateway problems
- Trunk configuration problems

The deterministic engine provides a predictable fallback diagnosis even when an external AI service is unavailable.

### 4. Gemini AI Integration

NetSage AI can optionally use Google Gemini to enhance troubleshooting analysis. Gemini can analyze:

- Network symptoms
- Network topology
- CLI evidence
- Deterministic findings
- Troubleshooting context

The AI-assisted diagnosis can provide:

- Probable root cause
- Supporting evidence
- OSI layer
- Confidence
- Verification commands
- Proposed remediation

Gemini is optional. If the Gemini API is unavailable, the application uses the deterministic fallback diagnosis.

---

## How NetSage AI Works

The application follows a structured troubleshooting workflow.

**Step 1 — Select a Case**

The user selects a troubleshooting case from the dashboard (e.g. `NET-001 • Inter-VLAN Routing`).

**Step 2 — Review Network Information**

The application displays relevant information such as Case ID, Severity, Issue Type, OSI Layer, Concept, Symptom, Topology, and CLI Evidence.

**Step 3 — Run Deterministic Diagnosis**

The deterministic engine examines the available evidence.

```
Evidence: GigabitEthernet0/0.30 administratively down

Potential Issue: Interface is administratively disabled.
OSI Layer: Layer 3
Verification: show ip interface brief
```

**Step 4 — Optional Gemini Analysis**

When Gemini is configured, the case information and deterministic findings can be analyzed by the AI model, producing a structured diagnosis with Root Cause, Evidence, Verification, and Proposed Remediation.

**Step 5 — Human Review**

The reviewer evaluates the recommendation: Approve, Edit & Accept, or Reject.

**Step 6 — Audit**

The final review decision is recorded for traceability.

---

## System Architecture

```
+------------------------------------------------------+
|                  STREAMLIT UI                        |
|                                                        |
| Dashboard | Diagnosis | Analytics | Audit & Safety    |
+--------------------------+-----------------------------+
                           |
                           v
+------------------------------------------------------+
|                CASE MANAGEMENT                        |
|                                                        |
| Case | Symptom | Severity | Topology | Evidence       |
+--------------------------+-----------------------------+
                           |
                           v
+------------------------------------------------------+
|             DETERMINISTIC CHECKER                     |
|                                                        |
| VLAN | DHCP | ACL | Routing | NAT | DNS | Interface   |
+--------------------------+-----------------------------+
                           |
                           v
+------------------------------------------------------+
|                 DIAGNOSIS ENGINE                       |
|                                                        |
| Deterministic Fallback + Optional Gemini AI           |
+--------------------------+-----------------------------+
                           |
                           v
+------------------------------------------------------+
|                HUMAN REVIEW GATE                       |
|                                                        |
| Approve | Edit & Accept | Reject                      |
+--------------------------+-----------------------------+
                           |
                           v
+------------------------------------------------------+
|                    AUDIT LOG                           |
+------------------------------------------------------+
```

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python 3.x |
| Frontend | Streamlit, HTML, CSS, Streamlit components, Data visualization |
| AI | Google Gemini API |
| Data Processing | Pandas, CSV-based troubleshooting dataset |
| Backend Logic | Python, Deterministic rule-based diagnosis, Diagnosis engine |
| Version Control | Git, GitHub |

---

## Project Structure

```
NetSage_AI/
│
├── data/
│   └── cases.csv
│
├── docs/
│   └── model_audit_log.md
│
├── prompts/
│   └── diagnose_prompt.md
│
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── checker.py
│   └── engine.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Installation

### Prerequisites

Make sure the following are installed:

- Python 3.10 or higher
- Git
- Internet connection
- Google Gemini API key for AI-assisted diagnosis

### Clone the Repository

```bash
git clone https://github.com/shiwanijha48-bot/NetStage_AI.git
cd NetStage_AI
```

### Create Virtual Environment

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a file named `.env` in the root directory and add:

```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.7-flash
```

Replace `your_gemini_api_key_here` with your actual Gemini API key.

### Important Security Note

Never commit your real API key to GitHub. The `.env` file should remain local. The repository should only contain `.env.example`.

**Example `.env.example`:**

```
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.7-flash
```

The real API key must never be placed in:

- README.md
- .env.example
- Python source files
- CSV files
- Git commits
- GitHub repository files

### .gitignore

The project should ignore local secrets and generated Python files:

```
.env
.venv/
__pycache__/
*.pyc
```

---

## Running the Application

From the project root directory, run:

```bash
streamlit run src/app.py
```

After Streamlit starts, open:

```
http://localhost:8501
```

The application should display the NetSage AI dashboard.

---

## Application Sections

### Overview

The Overview section provides a high-level summary of the troubleshooting dataset, including:

- Total cases
- Number of issue categories
- Severity distribution
- Review statistics
- AI-related metrics
- Network troubleshooting charts

### Diagnosis

The Diagnosis section is the main troubleshooting workspace. The user can:

- Select a network case.
- Inspect its information.
- Review network evidence.
- Run deterministic analysis.
- Request optional AI analysis.
- Review the root cause.
- Inspect verification commands.
- Review proposed remediation.
- Approve, edit, or reject the recommendation.

### Analytics

The Analytics section provides visual representations of the dataset:

- **Issue Type Distribution** — Displays how many cases belong to each network issue category.
- **Severity Distribution** — Displays the number of cases categorized by severity.
- **OSI Layer Distribution** — Shows which OSI layers are represented in the troubleshooting cases.
- **Issue Type vs Severity** — Provides a comparison between issue categories and their severity.
- **Review Outcomes** — Shows human review decisions such as Approved, Edited, Rejected.

### Audit & Safety

The Audit & Safety section focuses on:

- Human review
- Decision tracking
- AI limitations
- Simulation mode
- Audit information
- Responsible AI usage

---

## Deterministic Diagnosis

The deterministic diagnosis engine is designed to provide predictable results based on network evidence.

**Example:**

```
Input:
Interface GigabitEthernet0/0.30
administratively down

Possible diagnostic result:
Issue: Interface is disabled.
Likely Cause: The required interface or sub-interface is administratively disabled.
OSI Layer: Layer 3
Verification: show ip interface brief
```

This layer is important because it provides a baseline diagnosis independent of the AI service.

---

## Gemini AI Integration

When Gemini is enabled, the system can use the AI model to provide additional reasoning.

**Workflow:**

```
Case Data
    |
    v
Network Evidence
    |
    v
Deterministic Findings
    |
    v
Gemini AI
    |
    v
Structured Diagnosis
```

The AI-assisted diagnosis focuses on:

- Root Cause
- Evidence
- OSI Layer
- Confidence
- Verification
- Proposed Remediation

The AI output should be treated as an assistance mechanism rather than an unquestionable source of truth.

### AI Fallback

Gemini is optional. If:

- The API key is missing
- The API request fails
- The model is unavailable
- The network connection fails

the application can fall back to deterministic diagnosis. This makes the application more resilient and allows the core troubleshooting workflow to continue without requiring an external AI service.

---

## Human-in-the-Loop Review

A key feature of NetSage AI is Human-in-the-Loop review. The AI does not automatically execute network remediation. Instead, the system presents its diagnosis and recommendation to a human reviewer.

The reviewer can choose:

- **Approve** — The reviewer accepts the recommendation.
- **Edit & Accept** — The reviewer modifies the recommendation and accepts the revised version.
- **Reject** — The reviewer rejects the recommendation.

This approach ensures that AI recommendations remain under human control.

---

## Auditability and Safety

NetSage AI maintains an audit-oriented workflow so that troubleshooting decisions can be reviewed later. Audit information can include:

- Case ID
- Diagnosis
- Recommended action
- Reviewer decision
- Review status
- Timestamp
- Remediation status

This improves transparency and accountability.

### Safety Model

NetSage AI follows a controlled troubleshooting model. The system does not automatically apply changes to real network devices.

```
Evidence
   |
   v
Diagnosis
   |
   v
Recommendation
   |
   v
Human Review
   |
   +---- Approve
   |
   +---- Edit
   |
   +---- Reject
```

This reduces the risk of blindly applying AI-generated network configuration changes.

### Responsible AI

NetSage AI is designed around several responsible AI principles:

- **Human Oversight** — AI recommendations require human review.
- **Explainability** — The system attempts to provide evidence supporting a diagnosis.
- **Safety** — The project operates in a simulated environment.
- **Fallback** — Deterministic diagnosis remains available when AI is unavailable.
- **Auditability** — Review decisions can be tracked.

---

## Analytics

NetSage AI includes visual analytics for the troubleshooting dataset, representing:

- Cases by issue type
- Severity distribution
- Issue type vs severity
- OSI-layer distribution
- Review outcomes
- AI confidence
- Diagnostic trends

These visualizations make it easier to understand the characteristics of the network troubleshooting dataset.

---

## Sample Network Case

**Case ID:** NET-001

**Issue:** Inter-VLAN Routing

**Severity:** High

**OSI Layer:** Layer 3

**Symptom:** Hosts in different VLANs cannot communicate.

**Evidence:** Router sub-interface is administratively down.

**Diagnostic workflow output:**

```
Root Cause: The required router sub-interface is disabled.
Evidence: The interface status indicates administrative shutdown.
Verification: show ip interface brief
Proposed Remediation: Enable the affected interface after validating its configuration.
```

The final recommendation is then reviewed by a human.

---

## Network Concepts Covered

The project is designed around common networking troubleshooting concepts:

- Inter-VLAN Routing
- VLAN
- DHCP
- Routing
- ACL
- NAT
- DNS
- Interface Status
- Default Gateway
- Trunk Configuration

The dataset can be expanded with additional networking scenarios.

---

## Testing

After installation, verify the following.

**Application Startup**

```bash
streamlit run src/app.py
```

The Streamlit dashboard should load successfully.

**Case Selection**

- Cases are displayed.
- Case IDs are visible.
- Case details load correctly.
- Network evidence is displayed.

**Diagnosis**

- Deterministic diagnosis runs.
- Root cause information is displayed.
- Verification commands are shown.
- Proposed remediation is shown.

**Gemini** (when configured)

- Gemini requests are processed.
- AI diagnosis is displayed.
- The application does not crash if the API fails.

**Human Review**

- Approve works.
- Edit & Accept works.
- Reject works.
- Review information is recorded.

**Analytics**

- Charts load correctly.
- Dataset statistics are displayed.
- Issue categories are represented.
- Severity information is displayed.

---

## Security

- Never commit real API keys to the repository.
- Keep secrets only in the local `.env` file.
- Only `.env.example` (with placeholder values) should be tracked in Git.
- Generated files (`.venv/`, `__pycache__/`, `*.pyc`) should be excluded via `.gitignore`.

---

## Limitations

NetSage AI is currently a troubleshooting assistance and simulation platform. It does not currently:

- Connect directly to physical routers.
- Connect directly to physical switches.
- Automatically modify network configurations.
- Automatically deploy remediation.
- Guarantee that an AI diagnosis is correct.
- Replace an experienced network engineer.
- Provide production-grade network automation.

AI recommendations should always be reviewed before implementation.

---

## Future Enhancements

### Real Network Device Integration

Future versions could integrate with network devices using:

- SSH
- NETCONF
- RESTCONF
- Vendor APIs

### Advanced Network Topology

An interactive network topology could be added, for example:

```
Client
  |
  v
Switch
  |
  v
Router
  |
  v
Firewall
  |
  v
Server
```

### More Networking Protocols

Future diagnostic rules could cover:

- STP
- OSPF
- BGP
- IPv6
- EtherChannel
- Port Security
- Wireless Networking
- Firewall Policies

### Database Integration

The current dataset can be extended from CSV storage to a database such as:

- SQLite
- PostgreSQL

This would improve scalability and persistent audit storage.

### Authentication and Authorization

Future versions could support role-based access control with roles such as:

- Administrator
- Network Engineer
- Reviewer
- Viewer

### Advanced AI Evaluation

Future versions could compare Deterministic Diagnosis + Gemini Diagnosis + Human Diagnosis, and calculate:

- Agreement rate
- Confidence
- Correction rate
- Acceptance rate
- Rejection rate

### Production Deployment

Possible deployment options include:

- Docker
- Streamlit Community Cloud
- Cloud VM
- Kubernetes
- Internal enterprise infrastructure

---

## Example End-to-End Workflow

```
1. Open NetSage AI
          |
          v
2. Select network troubleshooting case
          |
          v
3. Inspect symptom and evidence
          |
          v
4. Run deterministic diagnosis
          |
          v
5. Optional Gemini analysis
          |
          v
6. Review root cause and evidence
          |
          v
7. Review verification command
          |
          v
8. Review proposed remediation
          |
          v
9. Human decision
          |
     +----+----+
     |    |    |
     v    v    v
  Approve Edit Reject
     |
     v
10. Audit decision
```

---

## Project Highlights

NetSage AI demonstrates the combination of:

Networking + Python + Streamlit + Deterministic Rules + Generative AI + Data Visualization + Human-in-the-Loop + Auditability

Key project capabilities include:

- Interactive troubleshooting dashboard
- Structured network cases
- CLI evidence analysis
- Deterministic diagnostic engine
- Google Gemini integration
- Root-cause analysis
- OSI-layer mapping
- Verification commands
- Proposed remediation
- Human approval workflow
- Audit-oriented design
- Analytics dashboard
- Simulation-only remediation
- AI fallback mechanism
- Environment-based API configuration

---

## Learning Outcomes

This project demonstrates practical understanding of:

- Python application development
- Streamlit application development
- Network troubleshooting
- OSI model concepts
- Network configuration analysis
- Rule-based systems
- Generative AI integration
- Prompt-based AI reasoning
- Data processing
- Data visualization
- Human-in-the-Loop AI
- Responsible AI design
- Git and GitHub
- Environment variable management

---

## Conclusion

NetSage AI demonstrates how Generative AI can be combined with traditional networking knowledge and deterministic troubleshooting rules to create an explainable network troubleshooting assistant.

Instead of allowing AI to independently modify network infrastructure, the system follows a controlled workflow:

```
Network Evidence
       |
       v
Deterministic Analysis
       |
       v
AI Assistance
       |
       v
Human Review
       |
       v
Audit
```

This architecture provides a safer and more transparent approach to AI-assisted network troubleshooting.

NetSage AI can serve as a foundation for future development of intelligent Network Operations Center (NOC) assistance, automated troubleshooting, network observability, and human-supervised network automation.

---

## Author

**NetSage AI**
AI-Assisted Network Troubleshooting & Diagnosis Platform

Built with:

- Python
- Streamlit
- Google Gemini
- Pandas
- Networking Concepts
- Deterministic Diagnostic Rules



---

## License

This project is intended for educational, demonstration, and research purposes.

A formal open-source license can be added to the repository if required.
