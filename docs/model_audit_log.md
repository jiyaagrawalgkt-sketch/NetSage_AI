# NetSage AI Model Audit Log

The Streamlit application appends decisions to this file.

Required human-review outcomes:
- ACCEPTED
- EDITED
- REJECTED

The project demonstration should intentionally include at least 5 cases where a human
corrects or rejects the AI recommendation.
| 2026-08-24 17:39:58 | NET-003 | ACCEPTED | Default gateway is in the wrong subnet | 0.82 | Review the evidence and verify the diagnosis.<br>Recommended action: ipconfig / show ip interface brief.<br>Apply the change only after human approval in the lab. |  |
| 2026-08-24 18:22:50 | NET-002 | ACCEPTED | Access port is assigned to VLAN 30 instead of VLAN 20 | 0.62 | Review the evidence and verify the diagnosis.<br>Recommended action: switchport access vlan 20.<br>Apply the change only after human approval in the lab. |  |
| 2026-08-24 18:23:05 | NET-005 | EDITED | Configured DNS server is unreachable | 0.82 | Review the evidence and verify the diagnosis.<br>Recommended action: ping 192.168.50.99; show ip route.<br>Apply the change only after human approval in the lab. | Human modified the AI recommendation before acceptance. |
| 2026-08-24 18:23:21 | NET-003 | REJECTED | Default gateway is in the wrong subnet | 0.82 | Review the evidence and verify the diagnosis.<br>Recommended action: ipconfig / show ip interface brief.<br>Apply the change only after human approval in the lab. | Human reviewer rejected the AI diagnosis/fix. |
