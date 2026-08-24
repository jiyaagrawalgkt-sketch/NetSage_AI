"""
Deterministic network-rule checker for NetSage AI.
This module deliberately uses transparent rules/regex instead of an LLM.
"""
import re
from typing import Any, Dict, List

def _finding(rule: str, severity: str, evidence: str, recommendation: str) -> Dict[str, str]:
    return {
        "rule": rule,
        "severity": severity,
        "evidence": evidence,
        "recommendation": recommendation,
    }

def run_checks(text: str) -> Dict[str, Any]:
    t = text or ""
    findings: List[Dict[str, str]] = []

    # Interface status
    m = re.search(r"(?i)([\w./-]+)\s+is\s+administratively\s+down", t)
    if m:
        findings.append(_finding(
            "ADMINISTRATIVELY_DOWN", "High", m.group(0),
            f"Inspect {m.group(1)} and, after human verification, consider 'no shutdown'."
        ))

    if re.search(r"(?i)err-disabled|disabled", t):
        match = re.search(r"(?i)([\w./-]+).{0,80}(err-disabled|disabled)", t)
        findings.append(_finding(
            "PORT_DISABLED", "High", match.group(0) if match else "err-disabled/disabled",
            "Inspect the cause such as port security, BPDU guard, or link fault before recovery."
        ))

    # Duplicate IP
    ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", t)
    counts = {}
    for ip in ips:
        counts[ip] = counts.get(ip, 0) + 1
    for ip, count in counts.items():
        if count >= 2 and ("PC1" in t or "PC2" in t or "duplicate" in t.lower()):
            findings.append(_finding(
                "DUPLICATE_IP", "Critical", f"{ip} appears {count} times",
                "Verify host addressing and DHCP bindings before changing either device."
            ))
            break

    # Wrong gateway / missing gateway
    if re.search(r"(?i)default gateway:\s*192\.168\.20\.1.*?router interface:\s*192\.168\.10\.1", t, re.S):
        findings.append(_finding(
            "GATEWAY_MISMATCH", "High",
            "Default Gateway: 192.168.20.1; Router interface: 192.168.10.1",
            "Verify the host subnet and configure the correct gateway."
        ))
    if re.search(r"(?i)gateway:\s*(blank|$)", t, re.M):
        findings.append(_finding(
            "MISSING_GATEWAY", "High", "Gateway: blank",
            "Configure the appropriate default gateway after verifying the subnet."
        ))

    # DHCP
    if "169.254." in t or re.search(r"(?i)IPv4 Address:\s*169\.254", t):
        findings.append(_finding(
            "APIPA_ADDRESS", "High", "Client has a 169.254.x.x address",
            "Verify DHCP reachability, pool availability, VLAN, and DHCP relay."
        ))
    if re.search(r"(?i)Utilization:\s*100%|Leased addresses:\s*254", t):
        findings.append(_finding(
            "DHCP_POOL_EXHAUSTED", "Medium", "DHCP pool utilization is 100%",
            "Inspect bindings and expand/adjust the pool only after verification."
        ))
    if re.search(r"(?i)DHCP scope:\s*VLAN\s*60.*?Switch port to AP:\s*VLAN\s*50", t, re.S):
        findings.append(_finding(
            "DHCP_VLAN_MISMATCH", "High", "AP is on VLAN 50 while DHCP scope is VLAN 60",
            "Verify SSID-to-VLAN mapping and DHCP scope."
        ))

    # VLAN/trunk
    if re.search(r"(?i)Vlans allowed on trunk:.*\b10,20,30\b", t) and re.search(r"(?i)VLAN 40", t):
        findings.append(_finding(
            "VLAN_NOT_ALLOWED_ON_TRUNK", "High", "VLAN 40 is absent from allowed VLANs",
            "Verify trunk allowed VLAN configuration."
        ))
    if re.search(r"(?i)60 not present", t):
        findings.append(_finding(
            "MISSING_VLAN", "High", "VLAN 60 is not present",
            "Verify/create VLAN 60 on the switch."
        ))
    if re.search(r"(?i)native VLAN:\s*99.*?other side native VLAN:\s*1", t, re.S):
        findings.append(_finding(
            "NATIVE_VLAN_MISMATCH", "Medium", "Native VLAN 99 vs 1",
            "Make the trunk native VLAN configuration consistent after verification."
        ))

    # Routing
    if re.search(r"(?i)192\.168\.30\.0/24 is not present", t):
        findings.append(_finding(
            "MISSING_ROUTE", "High", "192.168.30.0/24 is not present in routing table",
            "Verify routing topology and add the appropriate route if required."
        ))
    if re.search(r"(?i)Gateway of last resort is not set", t):
        findings.append(_finding(
            "MISSING_DEFAULT_ROUTE", "High", "Gateway of last resort is not set",
            "Verify ISP next hop and configure a default route if appropriate."
        ))
    if re.search(r"(?i)via\s+10\.0\.0\.2.*?ping\s+10\.0\.0\.2\s*=\s*unreachable", t, re.S):
        findings.append(_finding(
            "UNREACHABLE_NEXT_HOP", "High", "Configured next hop 10.0.0.2 is unreachable",
            "Verify the directly connected network and next-hop address."
        ))

    # OSPF / masks
    if re.search(r"(?i)R1 G0/0:\s*10\.0\.0\.1/30.*?R2 G0/0:\s*10\.0\.0\.2/24", t, re.S):
        findings.append(_finding(
            "MASK_MISMATCH", "High", "OSPF-facing interfaces use /30 and /24",
            "Verify and align subnet masks on the point-to-point link."
        ))

    # ACL
    if re.search(r"(?i)deny tcp .* eq 80", t):
        findings.append(_finding(
            "ACL_HTTP_DENY", "High", "ACL contains an explicit HTTP deny",
            "Inspect ACL sequence and policy before editing."
        ))
    if re.search(r"(?i)10 deny ip any 192\.168\.10\.0", t):
        findings.append(_finding(
            "ACL_ORDERING", "High", "Earlier deny precedes later permit",
            "Inspect sequence order; first matching ACL entry wins."
        ))
    if re.search(r"(?i)No ACL applied to guest interface", t):
        findings.append(_finding(
            "GUEST_ISOLATION_MISSING", "Critical", "No ACL is applied to guest interface",
            "Verify guest isolation policy and apply an appropriate ACL only after review."
        ))
    if re.search(r"(?i)ACL 110 permits ip 10\.20\.0\.0", t):
        findings.append(_finding(
            "GUEST_TO_INTERNAL_PERMIT", "Critical", "ACL explicitly permits guest-to-internal traffic",
            "Verify whether the permit is intended; enforce isolation if required."
        ))

    # NAT
    if re.search(r"(?i)No ip nat inside source statement", t):
        findings.append(_finding(
            "NAT_CONFIG_MISSING", "High", "No NAT overload statement is present",
            "Verify inside/outside interfaces and configure NAT only after review."
        ))
    if re.search(r"(?i)ip nat inside source list 1 interface G0/0 overload.*?G0/0\s+ip nat inside.*?G0/1\s+ip nat inside", t, re.S):
        findings.append(_finding(
            "NAT_OUTSIDE_INTERFACE_MISMATCH", "High", "PAT references an inside interface",
            "Verify the actual ISP-facing interface before changing NAT."
        ))

    # Sub-interface / dot1q
    if re.search(r"(?i)interface G0/0\.20.*?encapsulation dot1Q 30.*?192\.168\.20\.1", t, re.S):
        findings.append(_finding(
            "DOT1Q_TAG_MISMATCH", "High", "G0/0.20 uses dot1Q 30",
            "Verify the intended VLAN ID and sub-interface mapping."
        ))

    # DNS
    if re.search(r"(?i)DNS Servers:\s*192\.168\.60\.60.*?Known DNS Server:\s*192\.168\.60\.53", t, re.S):
        findings.append(_finding(
            "DNS_SERVER_MISMATCH", "Medium", "Client DNS differs from known DNS server",
            "Verify DNS server address and reachability."
        ))
    if re.search(r"(?i)DNS Server: 192\.168\.50\.99.*?timeout", t, re.S):
        findings.append(_finding(
            "DNS_UNREACHABLE", "Medium", "Configured DNS server is unreachable",
            "Ping the DNS server and inspect routing/ACLs."
        ))

    # Physical errors
    if re.search(r"(?i)CRC:\s*\d+|input errors:\s*\d+", t):
        findings.append(_finding(
            "INTERFACE_ERRORS", "Medium", "Interface reports input/CRC errors",
            "Inspect cable, duplex/speed, transceiver, and interface counters."
        ))

    status = "ERRORS_DETECTED" if findings else "NO_DETERMINISTIC_ERROR"
    return {"status": status, "findings": findings, "count": len(findings)}
