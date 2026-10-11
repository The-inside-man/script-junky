"""Curated, evidence-led investigation guidance. This module does not scan hosts."""

REVIEWED_AT = "2026-10-09"
REFERENCES = [
    {"id": "attack", "title": "MITRE ATT&CK: adversary behaviors", "url": "https://attack.mitre.org/", "purpose": "Name possible attacker behaviors and find detection ideas; a technique match is not attribution."},
    {"id": "csf", "title": "NIST Cybersecurity Framework 2.0", "url": "https://www.nist.gov/cyberframework", "purpose": "Connect assets, protection, detection, response, and recovery to business risk."},
    {"id": "risk", "title": "NIST SP 800-30 Rev. 1: risk assessment", "url": "https://csrc.nist.gov/pubs/sp/800/30/r1/final", "purpose": "Assess threat events, conditions, likelihood, and impact; document uncertainty."},
    {"id": "response", "title": "NIST SP 800-61 Rev. 3: incident response", "url": "https://csrc.nist.gov/pubs/sp/800/61/r3/final", "purpose": "Prepare, investigate, communicate, respond, and recover within an organization's process."},
    {"id": "cis", "title": "CIS Controls v8.1", "url": "https://www.cisecurity.org/controls/cis-controls-list", "purpose": "Review practical defenses such as configuration, account management, logging, and incident response."},
    {"id": "stride", "title": "Microsoft STRIDE threat categories", "url": "https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats", "purpose": "Ask how identities, integrity, accountability, confidentiality, availability, or privileges might be abused."},
]

METHOD = [
    {"title": "Name what matters", "question": "What business function and asset are you protecting? Who authorized this investigation?", "action": "Record the host, time window, permitted evidence, owner, and stop conditions. Identify data, service availability, and privileged identities."},
    {"title": "Think in attacker goals", "question": "What would an adversary gain: access, persistence, privilege, data, or disruption?", "action": "Describe the actor's starting access and a plausible objective. Follow the cheapest feasible path through the system, not just the most dramatic exploit."},
    {"title": "Map the boundary", "question": "Which low-trust input reaches a higher-trust component?", "action": "Connect entry points, services, identities, writable configuration, startup mechanisms, and dependencies. Separate actual reachability from a listening address."},
    {"title": "Predict the evidence", "question": "If your hypothesis were true, what else should exist? What would contradict it?", "action": "Write a testable prediction. Correlate identity, time, process ancestry, file change, and network context. An ATT&CK mapping describes a possible behavior, not a confirmed attack."},
    {"title": "Try to disprove yourself", "question": "Could maintenance, a deployment, a user mistake, or missing telemetry explain this?", "action": "Check the baseline, change record, owner, and independent sources. Absence of an event only helps when the source should reliably have recorded it."},
    {"title": "Evaluate the threat", "question": "How damaging is the outcome, how plausible is the path, and how strongly is the finding supported?", "action": "Rate impact, likelihood, and evidence confidence separately with reasons. Unknown likelihood stays unknown. High potential impact can justify prompt escalation even when confidence is low."},
    {"title": "Choose the next test", "question": "Which permitted observation would reduce uncertainty most?", "action": "Preserve useful evidence and timestamps, record gaps, name the next collection, and identify the decision owner. Recommend a control and a way to verify it; use the incident-response process before making live changes."},
]

PROFILES = [
    {"id": "general", "name": "General Unix host", "assets": "User data, service integrity, credentials, and availability.", "focus": "Establish the machine's role and baseline before interpreting anomalies.", "questions": ["Who owns this host and which services should run?", "What changed during the approved time window?"], "priority": ["authentication", "persistence", "permission-risk"]},
    {"id": "healthcare", "name": "Healthcare", "assets": "Care delivery, sensitive records, scheduling, and recovery capability.", "focus": "Evaluate service disruption and sensitive-data access together. Coordinate collection on clinical systems with their operators.", "questions": ["Could collection interfere with a care-critical service?", "Which account can read sensitive records, and is that access recorded?"], "priority": ["ransomware", "identity", "data-egress"]},
    {"id": "finance", "name": "Financial services", "assets": "Transaction integrity, privileged identities, customer data, and audit records.", "focus": "Trace the authority to change transactions or records and preserve independently recorded evidence.", "questions": ["Which identity can alter business records?", "Can an independent log corroborate the action and its approval?"], "priority": ["authentication", "identity", "permission-risk"]},
    {"id": "saas", "name": "SaaS / cloud services", "assets": "Tenant data, service identities, application integrity, and deployment dependencies.", "focus": "Follow tenant and service-identity boundaries. A host snapshot must be supplemented by relevant cloud control-plane evidence.", "questions": ["Can this service identity reach another tenant or environment?", "Which deploy or package change explains the new executable?"], "priority": ["web-shell", "supply-chain", "identity"]},
    {"id": "critical", "name": "Critical infrastructure", "assets": "Operational availability, safe physical processes, remote access, and recovery.", "focus": "Separate IT evidence from operational-system access. Review remote administration with operators before planning any collection on operational equipment.", "questions": ["Which remote-access path crosses from IT toward operations?", "Could a collection step affect availability or safety?"], "priority": ["authentication", "living-off-land", "ransomware"]},
]
PROFILE_MAP = {profile["id"]: profile for profile in PROFILES}
PLATFORMS = [{"id": "captured", "name": "Captured lab evidence"}, {"id": "linux", "name": "Linux host context"}, {"id": "macos", "name": "macOS host context"}]
SIGNALS = [
    {"id": "login-spike", "label": "Unusual logins or repeated failures"},
    {"id": "startup-change", "label": "Unfamiliar startup job or service"},
    {"id": "unexpected-shell", "label": "Unexpected shell or process ancestry"},
    {"id": "writable-config", "label": "Writable privileged configuration"},
    {"id": "account-change", "label": "New account, key, or privilege"},
    {"id": "egress-change", "label": "Unexpected transfer or network activity"},
    {"id": "file-disruption", "label": "Rapid file changes or service disruption"},
    {"id": "package-drift", "label": "Package or executable baseline changed"},
]
SIGNAL_MAP = {signal["id"]: signal for signal in SIGNALS}

CASES = [
    {"id": "volt", "title": "Volt Typhoon: trusted tools and persistent access", "period": "2023–2024 reporting", "published": "2024-02-07", "publisher": "CISA and partner agencies", "url": "https://www.cyber.gov.au/sites/default/files/2024-02/aa24-038a-jcsa-prc-state-sponsored-actors-compromise-us-critical-infrastructure.pdf",
     "observed": "The joint advisory documented access to critical-infrastructure environments and use of existing administration tools to blend with normal activity.",
     "lesson": "Examine identity, timing, ancestry, and purpose even when a binary is legitimate. A familiar tool name is weak evidence of benign intent.",
     "limit": "Much of the published telemetry is Windows or network-device specific. The coach transfers the reasoning method to Unix; its lab is not a reproduction of this campaign."},
    {"id": "ivanti", "title": "Ivanti gateway exploitation: distrust one evidence source", "period": "December 2023–January 2024", "published": "2024-01-18", "publisher": "Volexity incident research", "url": "https://www.volexity.com/blog/2024/01/18/ivanti-connect-secure-vpn-exploitation-new-observations/",
     "observed": "Volexity reported compromised VPN appliances, web-shell findings, and modifications that caused an internal integrity checker to report no mismatches.",
     "lesson": "Corroborate appliance findings with independent artifacts. A clean result from a tool inside the suspected system is not sufficient clearance.",
     "limit": "These are historical observations about particular products. Do not apply old patch instructions to a current system or infer a compromise from a version string alone."},
    {"id": "lockbit", "title": "LockBit: availability and recovery are assets", "period": "2020–2023 activity summarized", "published": "2023-06-14", "publisher": "CISA and partner agencies, AA23-165A", "url": "https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-165a",
     "observed": "The advisory described varied affiliate intrusions and the development of ransomware targeting Linux and VMware ESXi.",
     "lesson": "Correlate widespread file changes with process activity and protect recovery evidence. Escalate potential service disruption promptly through the response process.",
     "limit": "File extensions and a ransom note are leads, not actor attribution. The synthetic exercises contain no encryptor and do not reproduce an intrusion."},
    {"id": "xz", "title": "xz backdoor: inspect the dependency chain", "period": "March 2024 discovery", "published": "2024-03-29", "publisher": "Red Hat Product Security", "url": "https://www.redhat.com/en/blog/urgent-security-alert-fedora-40-and-rawhide-users",
     "observed": "Red Hat reported malicious code in xz 5.6.0 and 5.6.1 and explained that affected builds and exploitability depended on distribution and build circumstances.",
     "lesson": "Check package origin, build details, trusted advisories, and known-good artifacts. A trusted project name or a matching version is insufficient by itself.",
     "limit": "This is a historical supply-chain compromise, not evidence that a current host is affected. Use current vendor guidance for a real exposure assessment."},
]
CASE_MAP = {case["id"]: case for case in CASES}


def technique(id, name):
    return {"id": id, "name": name, "url": "https://attack.mitre.org/techniques/" + id.replace(".", "/") + "/"}


def playbook(id, title, signals, goal, look_for, corroborate, alternatives, next_test,
             controls, techniques, lessons, cases, command, paths):
    return dict(id=id, title=title, signals=signals, attacker_goal=goal, look_for=look_for,
                corroborate=corroborate, alternatives=alternatives, next_test=next_test,
                controls=controls, techniques=techniques, lessons=lessons, cases=cases,
                lab_command=command, paths=paths)


PLAYBOOKS = [
    playbook("authentication", "Account abuse and login anomalies", ["login-spike", "account-change"],
             "Use guessed or stolen credentials to act as a legitimate identity.",
             ["Failures grouped by account, source, and time window; unexpected successful logins.", "A service identity used interactively or from a new source."],
             ["Link a successful login to the same identity, host, and time window; check owner approval.", "Seek session or process evidence and independent identity-provider records."],
             ["Mistyped passwords, a changed automation secret, or an approved administrator session."],
             "Ask the account owner about the session and collect the permitted session/process record before calling the login unauthorized.",
             ["CIS 5: Account Management", "CIS 6: Access Control Management", "CIS 8: Audit Log Management"],
             [technique("T1110", "Brute Force"), technique("T1078", "Valid Accounts")], ["pipelines", "processes", "timeline"], ["volt"],
             "grep 'Failed password' evidence/logs/auth.log | awk '{print $(NF-3)}' | LC_ALL=C sort | uniq -c\ngrep 'Accepted password' evidence/logs/auth.log",
             {"linux": "SSH/auth records may be in auth.log, secure, or the system journal; confirm configuration and retention.", "macos": "Use approved unified-log or identity-provider exports; do not assume Linux log paths exist.", "captured": "evidence/logs/auth.log and evidence/system/processes.tsv"}),
    playbook("persistence", "Startup jobs and service persistence", ["startup-change", "unexpected-shell"],
             "Arrange for code or an unwanted task to run again after login, reboot, or a schedule.",
             ["New cron entries, services, timers, LaunchAgents, or LaunchDaemons outside the approved baseline.", "Jobs with an unexpected owner or a program in a writable or temporary path."],
             ["Compare program path, owner, install time, and change approval with the known-good baseline.", "Link a startup definition to execution evidence; mere presence does not prove it ran."],
             ["Backup schedules, update agents, a developer task, or an approved deployment."],
             "Collect the job definition and execution record; verify its owner and change ticket. Analyze its program on a permitted copy without activating it.",
             ["CIS 4: Secure Configuration", "CIS 8: Audit Log Management"],
             [technique("T1053.003", "Cron"), technique("T1543.002", "Systemd Service"), technique("T1543.001", "Launch Agent")], ["persistence-hunt", "processes"], [],
             "# In the persistence-hunt lab only:\nawk -F '\t' 'NR > 1 && $6 == \"unapproved\" {print $3}' evidence/hunts/startup.tsv | LC_ALL=C sort",
             {"linux": "Review authorized exports of cron, systemd services, timers, and user services. Paths and active schedulers vary.", "macos": "Review authorized exports of user/system LaunchAgents and LaunchDaemons. A plist needs execution context as well as content.", "captured": "The persistence-hunt lesson provides inert startup definitions and a baseline table."}),
    playbook("web-shell", "Web application compromise", ["unexpected-shell", "writable-config", "package-drift"],
             "Turn an exposed application into access under its service identity.",
             ["A web-service process spawning an unexpected shell or utility.", "New or changed executable application files outside an approved release."],
             ["Correlate web requests, deployment history, file digests, and process parents.", "Check independent telemetry when a local integrity tool may have been modified."],
             ["A legitimate application invokes a helper, a deployment changes files, or a diagnostic endpoint is intentionally enabled."],
             "Obtain permitted request and process-tree records and compare the application with a trusted release. Do not request or execute a suspected web shell.",
             ["CIS 4: Secure Configuration", "CIS 8: Audit Log Management", "CIS 16: Application Software Security"],
             [technique("T1190", "Exploit Public-Facing Application"), technique("T1505.003", "Web Shell")], ["text-tools", "processes", "hashes"], ["ivanti"],
             "# This fixture has a process lead, not proof of a web shell.\ncat evidence/system/processes.tsv\ncat evidence/system/listeners.tsv",
             {"linux": "Application/access logs, application release artifacts, and approved process/audit records; locations depend on the service.", "macos": "Application logs and release baselines, plus permitted process/endpoint telemetry.", "captured": "The base lab lacks request logs and full command lines. Record that gap instead of inventing them."}),
    playbook("living-off-land", "Suspicious use of trusted tools", ["unexpected-shell", "egress-change"],
             "Use existing tools and service identities to discover, retrieve, or move material while looking routine.",
             ["A familiar tool with an unfamiliar parent, destination, identity, or execution time.", "A download followed by execution, or discovery outside that identity's normal job."],
             ["Compare activity with deployment and administrative workflows.", "Connect the source, destination, resulting file, parent process, and user/session."],
             ["A package update, CI job, support session, or backup operation."],
             "Verify the workflow owner and obtain the approved process/network records. Inspect a copied artifact's metadata and digest; do not run it to see what happens.",
             ["CIS 8: Audit Log Management", "CIS 13: Network Monitoring and Defense"],
             [technique("T1059.004", "Unix Shell"), technique("T1105", "Ingress Tool Transfer")], ["http", "processes", "scripts"], ["volt"],
             "cat evidence/system/processes.tsv\n# curl and wget are legitimate tools; this snapshot lacks their command lines.",
             {"linux": "Approved audit/endpoint exports, process parents, service identities, and network records.", "macos": "Approved endpoint/unified-log exports and application provenance, correlated with identity and destination.", "captured": "Use the fixed process snapshot and explicitly record missing ancestry/command-line detail."}),
    playbook("identity", "New accounts, SSH keys, and privileges", ["account-change", "login-spike"],
             "Preserve access through an added key or account, or expand the authority of an existing identity.",
             ["Unapproved keys or accounts; unexpected changes to groups, roles, or login policy.", "A service identity gaining interactive login or administrative rights."],
             ["Compare account/key inventories with an approved baseline and a change record.", "Use key fingerprints and account owners; avoid collecting private keys or tokens."],
             ["Key rotation, account provisioning, emergency access, or a scheduled role change."],
             "Collect the permitted account-change record and ask the identity owner to validate it. Map the effective permissions and the boundary they cross.",
             ["CIS 5: Account Management", "CIS 6: Access Control Management", "CIS 8: Audit Log Management"],
             [technique("T1098.004", "SSH Authorized Keys"), technique("T1078", "Valid Accounts")], ["scope", "permissions", "attack-paths"], [],
             "grep 'Accepted password' evidence/logs/auth.log\n# The base lab has no key inventory: record the needed evidence, not a key-based verdict.",
             {"linux": "Authorized account/group, login-policy, and public-key fingerprint exports; inspect only approved identities.", "macos": "Authorized local/directory-account, role, Remote Login, and public-key fingerprint exports.", "captured": "Account approval and SSH-key data are missing from the base fixture. Request them as the next test."}),
    playbook("permission-risk", "Writable configuration and trust boundaries", ["writable-config", "account-change"],
             "Influence a more trusted service through configuration or files an ordinary actor can change.",
             ["Configuration writable by lower-trust users or groups.", "A privileged consumer trusting a writable program path or job definition."],
             ["Inspect owner, group, ACLs, directory access, consumer privileges, and the exact data flow.", "Establish whether access is effective and whether the consumer uses that setting."],
             ["A nonprivileged service, a harmless sample, or a deliberately shared workflow with compensating controls."],
             "Determine the consumer's effective identity and permissions on an authorized copy. Propose a restricted-write control and verify ordinary users cannot alter the trusted setting.",
             ["CIS 4: Secure Configuration", "CIS 6: Access Control Management", "STRIDE: Tampering / Elevation of Privilege"],
             [], ["permissions", "threat-model", "attack-paths"], [],
             "find ./evidence -type f -perm -002\ncat evidence/config/worker.conf",
             {"linux": "Bounded mode/owner/ACL inventory and the consumer's effective service identity. Mode bits alone are incomplete.", "macos": "Bounded owner, mode, ACL, and service-context exports; effective access differs from displayed mode bits.", "captured": "worker.conf has the other-write bit. The fixture does not establish elevated service authority or an executed abuse."}),
    playbook("data-egress", "Unexpected data movement", ["egress-change", "unexpected-shell"],
             "Collect protected information and move it beyond its authorized boundary.",
             ["Transfers or archive creation inconsistent with the service's purpose.", "Unapproved destinations, data classes, or access by unusual identities."],
             ["Connect process/session identity, source data, destination, bytes, and business approval.", "Use permitted proxy, DNS, network, and application records; a connection alone cannot identify transferred content."],
             ["Backups, analytics exports, a deployment, or a new approved integration."],
             "Verify the destination and workflow owner, then request permitted transfer metadata. Preserve the uncertainty about content when only a connection record exists.",
             ["CIS 3: Data Protection", "CIS 8: Audit Log Management", "CIS 13: Network Monitoring and Defense"],
             [technique("T1048", "Exfiltration Over Alternative Protocol")], ["http", "timeline", "investigation-evaluation"], [],
             "cat evidence/system/listeners.tsv\n# Listeners are not outbound-flow records. Do not claim exfiltration from this table.",
             {"linux": "Approved outbound-flow/proxy/DNS records and application access logs; link them to process identity.", "macos": "Approved network/endpoint records plus identity and data-access context.", "captured": "The base case lacks outbound transfer records; choose the evidence needed to test the hypothesis."}),
    playbook("ransomware", "File disruption and ransomware indicators", ["file-disruption", "startup-change"],
             "Disrupt service or data availability and undermine recovery.",
             ["Broad unexpected file changes, inaccessible data, disrupted services, or ransom messages.", "Process activity and changes affecting backup or recovery access."],
             ["Correlate affected paths, time, process identity, service status, and independent logs.", "Evaluate the integrity and availability of protected recovery copies through the response owner."],
             ["An authorized bulk migration, compression, backup rotation, or storage fault."],
             "Promptly involve the incident-response owner if disruption may be ongoing. Preserve permitted evidence; let the authorized response process choose containment and recovery actions.",
             ["CIS 10: Malware Defenses", "CIS 11: Data Recovery", "CIS 17: Incident Response Management"],
             [technique("T1486", "Data Encrypted for Impact")], ["hashes", "timeline", "investigation-evaluation"], ["lockbit"],
             "cat evidence/logs/events.tsv\n# This synthetic timeline does not contain encryption evidence.",
             {"linux": "File-change, process, service, and backup-system records. Avoid interacting with suspect binaries.", "macos": "Endpoint/file-change records and approved recovery status. A note or extension does not identify the actor.", "captured": "Practice with observation records and stated gaps; no encryption code is included."}),
    playbook("supply-chain", "Package drift and dependency trust", ["package-drift", "unexpected-shell"],
             "Place unwanted behavior in a trusted package, build, or deployment dependency.",
             ["Unexpected packages or executable changes outside the approved baseline.", "A dependency origin, signature, build, or release record that cannot be verified."],
             ["Check exact build provenance and current distributor advisories, not just a package name or upstream version.", "Compare trusted release artifacts with acquired copies and document how the baseline was established."],
             ["A sanctioned update, local build, package rename, or stale inventory."],
             "Preserve package inventory and copied artifacts, verify the build against distributor guidance, and review the deployment change before modifying the host.",
             ["CIS 2: Software Asset Inventory", "CIS 4: Secure Configuration", "CIS 16: Application Software Security"],
             [technique("T1195.002", "Compromise Software Supply Chain")], ["packages", "hashes", "investigation-evaluation"], ["xz"],
             "awk -F '\t' 'NR > 1 && $3 == \"unexpected\" {print $1}' evidence/system/packages.tsv",
             {"linux": "Distributor package/build metadata, repository origin, signatures, installation records, and known-good artifacts.", "macos": "Approved package/application origin and signing/deployment records, including Homebrew provenance when relevant.", "captured": "worker-helper is marked unexpected; this alone does not establish supply-chain compromise."}),
]
PLAYBOOK_MAP = {item["id"]: item for item in PLAYBOOKS}

RISK_GUIDANCE = {
    "impact": "What happens to confidentiality, integrity, availability, or the business mission if the proposed path succeeds? Explain the affected asset and scope.",
    "likelihood": "What starting access, exposure, preconditions, and working controls make this path plausible? Unknown preconditions must remain explicit.",
    "confidence": "How reliable and independent is the evidence supporting your observation and interpretation? More alerts do not necessarily mean stronger evidence.",
    "decision": "Choose the next permitted test and the escalation owner. High impact with low confidence can merit urgent investigation. These are training judgments, not a calculated probability or official risk score.",
}


def catalog():
    return {"reviewed_at": REVIEWED_AT, "method": METHOD, "profiles": PROFILES, "platforms": PLATFORMS,
            "signals": SIGNALS, "playbooks": PLAYBOOKS, "cases": CASES, "references": REFERENCES,
            "risk_guidance": RISK_GUIDANCE}


def build_plan(industry="general", platform="captured", signals=None):
    if not isinstance(industry, str) or industry not in PROFILE_MAP:
        raise ValueError("Unknown industry context")
    if not isinstance(platform, str) or platform not in {item["id"] for item in PLATFORMS}:
        raise ValueError("Unknown platform context")
    signals = [] if signals is None else signals
    if not isinstance(signals, list) or len(signals) > len(SIGNALS) or any(not isinstance(id, str) or id not in SIGNAL_MAP for id in signals):
        raise ValueError("Choose only the listed observation signals")
    signals = list(dict.fromkeys(signals))
    profile = PROFILE_MAP[industry]
    selected = set(signals)
    order = {id: index for index, id in enumerate(profile["priority"])}
    candidates = [item for item in PLAYBOOKS if not selected or selected.intersection(item["signals"])]
    candidates.sort(key=lambda item: (-len(selected.intersection(item["signals"])), order.get(item["id"], len(order)), PLAYBOOKS.index(item)))
    return {"industry": industry, "platform": platform, "signals": signals, "context": profile,
            "guides": [{"id": item["id"], "matches": [SIGNAL_MAP[id]["label"] for id in signals if id in item["signals"]], "evidence_context": item["paths"][platform]} for item in candidates],
            "basis": "Guides are ordered by overlap with the observations you selected, then by this illustrative sector's asset priorities. No host was scanned and no attack likelihood was calculated.",
            "first_step": "Define the asset, authorized scope, baseline, and time window before following a lead."}
