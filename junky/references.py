"""Primary-source reading paths for the original Script Junky curriculum.

Each mapping explains an instructional connection, not a quotation or a
compliance crosswalk. Keep source editions and section names explicit.
"""

REVIEWED_AT = "2026-10-09"
AUTHORSHIP = (
    "The learning objective and field application are original Script Junky wording, "
    "informed by the references below. They are not quotations from a standard."
)


def _source(title, short_title, publisher, kind, url):
    return dict(title=title, short_title=short_title, publisher=publisher, kind=kind, url=url)


SOURCE_CATALOG = {
    "nist-115": _source("NIST SP 800-115 · Technical Guide to Information Security Testing and Assessment (2008)", "NIST 800-115", "NIST", "Security assessment guidance", "https://csrc.nist.gov/pubs/sp/800/115/final"),
    "nist-61": _source("NIST SP 800-61 Rev. 3 · Incident Response Recommendations (2025)", "NIST 800-61 r3", "NIST", "Incident response guidance", "https://csrc.nist.gov/pubs/sp/800/61/r3/final"),
    "nist-86": _source("NIST SP 800-86 · Integrating Forensic Techniques into Incident Response (2006)", "NIST 800-86", "NIST", "Forensic process guidance", "https://csrc.nist.gov/pubs/sp/800/86/final"),
    "nist-30": _source("NIST SP 800-30 Rev. 1 · Guide for Conducting Risk Assessments (2012)", "NIST 800-30 r1", "NIST", "Risk assessment guidance", "https://csrc.nist.gov/pubs/sp/800/30/r1/final"),
    "cis": _source("CIS Critical Security Controls v8.1", "CIS Controls v8.1", "Center for Internet Security", "Defensive control framework", "https://www.cisecurity.org/controls/CIS-controls-navigator"),
    "ms-model": _source("Microsoft Threat Modeling Tool · Getting started", "Microsoft threat modeling", "Microsoft", "Threat modeling method", "https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-getting-started"),
    "stride": _source("Microsoft Threat Modeling Tool · STRIDE threats", "Microsoft STRIDE", "Microsoft", "Threat classification method", "https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats"),
    "cron": _source("MITRE ATT&CK T1053.003 · Scheduled Task/Job: Cron", "ATT&CK: Cron", "MITRE", "Adversary behavior knowledge base", "https://attack.mitre.org/techniques/T1053/003/"),
    "launch-agent": _source("MITRE ATT&CK T1543.001 · Create or Modify System Process: Launch Agent", "ATT&CK: Launch Agent", "MITRE", "Adversary behavior knowledge base", "https://attack.mitre.org/techniques/T1543/001/"),
    "bash": _source("GNU Bash Reference Manual", "Bash manual", "GNU Project", "Shell implementation manual", "https://www.gnu.org/software/bash/manual/bash.html"),
    "coreutils": _source("GNU Coreutils manual", "Coreutils manual", "GNU Project", "GNU utility manual", "https://www.gnu.org/software/coreutils/manual/coreutils.html"),
    "find": _source("GNU Findutils manual", "Findutils manual", "GNU Project", "GNU utility manual", "https://www.gnu.org/software/findutils/manual/html_mono/find.html"),
    "grep": _source("GNU Grep manual", "grep manual", "GNU Project", "GNU utility manual", "https://www.gnu.org/software/grep/manual/grep.html"),
    "awk": _source("The GNU Awk User's Guide", "awk manual", "GNU Project", "GNU utility manual", "https://www.gnu.org/software/gawk/manual/gawk.html"),
    "sed": _source("GNU sed · A stream editor", "sed manual", "GNU Project", "GNU utility manual", "https://www.gnu.org/software/sed/manual/sed.html"),
    "ip": _source("Linux ip(7) · IPv4 protocol implementation", "Linux ip(7)", "Linux man-pages project", "Linux networking manual", "https://man7.org/linux/man-pages/man7/ip.7.html"),
    "curl": _source("curl · Official command manual", "curl manual", "curl project", "Tool manual", "https://curl.se/docs/manpage.html"),
    "wget": _source("GNU Wget manual", "wget manual", "GNU Project", "Tool manual", "https://www.gnu.org/software/wget/manual/wget.html"),
    "brew": _source("Homebrew · brew(1) manual", "Homebrew manual", "Homebrew", "Package manager manual", "https://docs.brew.sh/Manpage"),
    "apt": _source("Debian · apt-get(8) manual", "APT manual", "Debian / APT project", "Package manager manual", "https://manpages.debian.org/stable/apt/apt-get.8.en.html"),
    "dpkg": _source("Debian · dpkg-query(1) manual", "dpkg-query manual", "Debian / dpkg project", "Package inventory manual", "https://manpages.debian.org/stable/dpkg/dpkg-query.1.en.html"),
    "dnf": _source("DNF · Command reference", "DNF reference", "DNF project", "Package manager manual", "https://dnf.readthedocs.io/en/latest/command_ref.html"),
    "rpm": _source("Maximum RPM · Query mode (historical manual)", "RPM query manual", "RPM project", "Package inventory manual", "https://ftp.rpm.org/max-rpm/s1-rpm-commands-query-mode.html"),
    "pacman": _source("Arch Linux · pacman(8) manual", "pacman manual", "Arch Linux", "Package manager manual", "https://man.archlinux.org/man/pacman.8.en"),
    "apk": _source("Alpine Linux · Working with the Alpine Package Keeper", "apk handbook", "Alpine Linux", "Package manager handbook", "https://docs.alpinelinux.org/user-handbook/0.1a/Working/apk.html"),
    "man": _source("man-db · man(1) manual", "man(1)", "man-db project", "Linux utility manual", "https://man7.org/linux/man-pages/man1/man.1.html"),
    "file": _source("file(1) · Determine file type", "file(1)", "file project", "Tool manual", "https://man7.org/linux/man-pages/man1/file.1.html"),
    "ps": _source("procps-ng · ps(1) manual", "Linux ps(1)", "procps-ng project", "Linux process manual", "https://man7.org/linux/man-pages/man1/ps.1.html"),
    "lsof": _source("lsof · Official manpage", "lsof manual", "lsof project", "Tool manual", "https://lsof.readthedocs.io/en/stable/manpage/"),
    "ss": _source("iproute2 · ss(8) manual", "Linux ss(8)", "iproute2 project", "Linux socket manual", "https://man7.org/linux/man-pages/man8/ss.8.html"),
    "shasum": _source("Perl shasum · Print or check SHA checksums", "shasum manual", "Perl documentation", "Tool manual", "https://perldoc.perl.org/shasum"),
    "tar": _source("GNU tar manual", "tar manual", "GNU Project", "GNU utility manual", "https://www.gnu.org/software/tar/manual/tar.html"),
    "shellcheck": _source("ShellCheck · Project documentation", "ShellCheck docs", "ShellCheck project", "Static analysis documentation", "https://github.com/koalaman/shellcheck#readme"),
    "jq": _source("jq · Official manual", "jq manual", "jq project", "JSON processing manual", "https://jqlang.org/manual/"),
    "json": _source("Python · json module documentation", "Python JSON docs", "Python Software Foundation", "Standard library documentation", "https://docs.python.org/3/library/json.html"),
}


def _ref(source_id, section, supports, role, url=None):
    source = SOURCE_CATALOG[source_id]
    return dict(source, id=source_id, section=section, supports=supports, role=role,
                url=url or source["url"])


def _basis(domains, context, adaptation, *references):
    return dict(domains=domains, context=context, adaptation=adaptation,
                authorship=AUTHORSHIP, reviewed_at=REVIEWED_AT, references=list(references))


LESSON_PROVENANCE = {
    "scope": _basis(
        ["Security assessment", "Incident response"],
        "This combines authorization boundaries for security assessments with investigation records for incident response. It applies across security work, including ethical hacking and forensics; it is broader than threat analysis alone. These references are guidance, not a universal requirement for every organization.",
        "The generated-directory boundary, stop condition, and scope.json format are course choices. Use your engagement's authorization and your organization's evidence procedures in real work.",
        _ref("nist-115", "§6.5 · Assessment Plan Development; Appendix B · Rules of Engagement Template", "Supports agreeing on authorized systems, permitted activities, exclusions, and data handling before assessment work.", "Scope and authorization", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf#page=51"),
        _ref("nist-61", "RS.AN-06 and RS.AN-07 · Investigation records and incident data", "Supports recording investigation actions and preserving the integrity and provenance of records and collected data.", "Investigation records", "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf#page=37")),
    "navigation": _basis(
        ["Unix fundamentals", "Forensic examination"],
        "Directory navigation is a general computing skill. This lesson applies it to discovering evidence sources before collection.",
        "The hidden-file exercise and sorted line-based inventory are course examples, not a prescribed forensic acquisition method. Check local man pages for BSD, GNU, and BusyBox differences.",
        _ref("nist-86", "§3.1.1 · Identifying Possible Sources of Data", "Explains identifying data sources before collection.", "Professional application", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf#page=26"),
        _ref("find", "Finding Files; Unusual Characters in File Names; Safe File Name Handling", "Documents file selection and why arbitrary filenames need careful handling.", "Command mechanics"),
        _ref("coreutils", "pwd invocation; ls invocation", "Documents working-directory and directory-listing behavior in GNU utilities.", "Command mechanics")),
    "quoting": _basis(
        ["Shell scripting"],
        "Quoting is a general shell-language skill used by administrators, developers, and security practitioners. Its use in evidence collection is our application of that skill.",
        "The filename-with-spaces exercise is course design. Bash documents shared shell concepts as well as Bash extensions; check your actual sh implementation before using extensions.",
        _ref("bash", "§3.1.2 · Quoting; §3.5.7 · Word Splitting; §3.5.8 · Filename Expansion; §3.7.5 · Exit Status", "Explains how quoting, expansion, and exit status affect the arguments and results of shell commands.", "Language behavior")),
    "pipelines": _basis(
        ["Shell scripting", "Authentication triage"],
        "Pipelines and aggregation are general data-processing techniques. Counting SSH failures is a course application for investigation leads, not a standard's compromise verdict or detection threshold.",
        "The log format, extracted field, and counts are specific to the synthetic fixture. A changed log schema needs a changed parser.",
        _ref("nist-86", "§3.2 · Examination; §3.3 · Analysis", "Connects filtering records with subsequent evidence analysis.", "Professional application", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf#page=30"),
        _ref("bash", "§3.2.3 · Pipelines", "Documents connected input/output streams and pipeline exit status, including Bash pipefail.", "Command mechanics"),
        _ref("awk", "Examining Fields; Specifying How Fields Are Separated", "Explains field extraction and the effect of the input separator.", "Command mechanics"),
        _ref("coreutils", "sort invocation; uniq invocation; wc invocation", "Documents sorting, adjacent duplicate counts, and line counts.", "Command mechanics")),
    "text-tools": _basis(
        ["Text processing", "Host attack surface"],
        "Structured-text parsing is general scripting. Applying it to listeners helps form exposure questions; a captured binding address alone does not measure reachability.",
        "The TSV schema and exposed-services.txt name belong to the lab. The output lists wildcard bindings, which still require routing and firewall investigation.",
        _ref("ip", "DESCRIPTION · bind and INADDR_ANY", "Explains that INADDR_ANY binds an IPv4 socket to all local interfaces.", "Socket semantics"),
        _ref("awk", "Specifying How Fields Are Separated; Patterns and Actions", "Documents delimiter selection and selecting/projecting fields.", "Command mechanics")),
    "permissions": _basis(
        ["Unix permissions", "Secure configuration", "Threat modeling"],
        "Mode-bit checks are Unix fundamentals. Secure-configuration guidance and threat modeling explain why writable settings deserve a review of who can influence which process.",
        "The world-writable fixture and trust-boundary explanation are a teaching scenario. Effective access also needs identity, ownership, ACL, and consumer context.",
        _ref("cis", "Control 4 · Secure Configuration of Enterprise Assets and Software", "Provides the defensive context for reviewing configurations and configuration processes.", "Defensive practice"),
        _ref("find", "File Permissions; Mode Bits", "Documents permission predicates, including testing specified mode bits with -perm.", "Command mechanics"),
        _ref("ms-model", "Create a model · Data flow diagrams and trust boundaries", "Explains modeling where control crosses between entities.", "Threat modeling method")),
    "packages": _basis(
        ["Software inventory", "Package management"],
        "Package management is system administration. Comparing installed software with an approved baseline supports security inventory; unfamiliar software alone is not proof of an attack.",
        "The unexpected marker is supplied by the lab, not an automatic threat classification. Each package manager documents its own commands and side effects.",
        _ref("cis", "Control 2 · Inventory and Control of Software Assets", "Provides the basis for maintaining software inventory and reviewing unauthorized software.", "Defensive practice"),
        _ref("brew", "list; info; install", "Documents Homebrew inventory, inspection, and installation commands.", "macOS / Homebrew commands"),
        _ref("apt", "DESCRIPTION · update and install", "Documents APT operations that change metadata or installed packages.", "Debian / Ubuntu commands"),
        _ref("dnf", "List Command; Info Command; Install Command", "Documents DNF package queries and changes.", "RPM-family commands"),
        _ref("pacman", "OPERATIONS · Query (-Q), Sync (-S)", "Documents Arch package inventory and coordinated synchronization operations.", "Arch commands"),
        _ref("apk", "Searching for Packages; Installing Packages; Querying Package Information", "Documents Alpine package discovery, inspection, and installation.", "Alpine commands")),
    "http": _basis(
        ["HTTP tooling", "Evidence collection"],
        "Controlled downloads are general tooling. The investigation application adds a record of the resource and collection method.",
        "The loopback manifest, ten-second curl limit, and output filename are lab choices. Wget's network timeouts do not have the same semantics as curl's total-transfer limit.",
        _ref("curl", "--fail; --silent; --show-error; --max-time; --output; TLS verification", "Documents the request's failure, diagnostics, timeout, output, and certificate behavior.", "Command mechanics"),
        _ref("wget", "Download Options · --tries, --output-document, --timeout; HTTPS Options", "Documents the alternative download command and its operation-specific timeouts.", "Command mechanics"),
        _ref("nist-61", "RS.AN-07 · Incident data and metadata", "Connects collection with preserving integrity and provenance.", "Professional application", "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf#page=37")),
    "scripts": _basis(
        ["Shell scripting", "Investigation automation"],
        "Input checks, explicit errors, and quoted arguments are general scripting practices. Applying them to triage helps another analyst repeat your work.",
        "The script interface, return codes 2/3, and edge-case exercise are original course design. The artifact checker does not certify script correctness.",
        _ref("bash", "Shell Functions; Conditional Constructs; Bourne Shell Builtins; Exit Status", "Documents the constructs used to validate input and propagate command failures.", "Language behavior"),
        _ref("grep", "Exit Status", "Explains the distinction between a match, no matches, and an operational error.", "Command behavior", "https://www.gnu.org/s/grep/manual/html_node/Exit-Status.html")),
    "processes": _basis(
        ["Host investigation", "Volatile evidence"],
        "Process and socket inspection supports incident investigation and everyday troubleshooting. The lab teaches choosing a lead rather than declaring a process malicious from its path.",
        "The /tmp prefix is a synthetic lead, not a universal indicator of compromise. Captured snapshots avoid the volatility and collection effects of live process inspection.",
        _ref("nist-86", "§5.2.1 · Collecting Volatile OS Data; §5.3 · Examining and Analyzing OS Data", "Covers collecting and analyzing process and connection evidence.", "Professional application", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf#page=53"),
        _ref("ps", "DESCRIPTION; STANDARD FORMAT SPECIFIERS", "Documents Linux process snapshots and selectable process fields.", "Linux command mechanics"),
        _ref("lsof", "DESCRIPTION; -i; -n; -P", "Documents associating open files and network endpoints with processes.", "Command mechanics"),
        _ref("ss", "DESCRIPTION; -l; -n; -t; -u; -p", "Documents Linux socket and process-owner inspection.", "Linux command mechanics")),
    "hashes": _basis(
        ["Forensic integrity", "Unix tooling"],
        "Digest comparison is a general integrity technique used in forensic workflows. The digest needs a collection record to help explain provenance.",
        "SHA-256 and the two-file exercise are course choices. The 2006 forensic guide explains integrity workflows; its historical algorithm examples are not a current algorithm policy.",
        _ref("nist-86", "§4.2.2 · Data File Integrity", "Explains integrity checks during forensic copying and examination.", "Professional application", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf#page=39"),
        _ref("coreutils", "sha2 utilities", "Documents SHA-256 digest computation and checking with GNU tools.", "GNU/Linux command mechanics"),
        _ref("shasum", "SYNOPSIS; OPTIONS · -a, --algorithm", "Documents selecting SHA-256 using shasum -a 256.", "macOS-compatible command mechanics")),
    "timeline": _basis(
        ["Forensic analysis", "Event correlation"],
        "Timelines support incident reconstruction across evidence sources. Time normalization and uncertainty matter beyond any one threat-analysis framework.",
        "The lab supplies fixed-width UTC timestamps, making lexical sorting sufficient here. Its sequence-versus-causation prompt is a course reasoning exercise.",
        _ref("nist-86", "§4.2.3 · File Modification, Access, and Creation Times; §8 · Using Data from Multiple Sources", "Discusses timestamp limitations and correlating evidence sources.", "Professional application", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf#page=41"),
        _ref("coreutils", "sort invocation; date invocation", "Documents ordering records and formatting dates, including UTC output.", "Command mechanics")),
    "threat-model": _basis(
        ["Threat modeling", "Secure design"],
        "This is explicitly threat modeling: describe the system, how trust changes, and a possible abuse before proposing a control. STRIDE is one named method, not the only industry approach.",
        "The five-part JSON model and writable-worker scenario are course simplifications, not Microsoft's required output format.",
        _ref("ms-model", "Create a model; Analyze threats; Threat properties", "Connects data flows and trust boundaries with threat analysis and mitigations.", "Threat modeling method"),
        _ref("stride", "STRIDE model", "Defines the six threat categories used to question a design.", "Threat classification")),
    "capstone": _basis(
        ["Incident triage", "Forensic reporting"],
        "Reporting belongs to incident response and forensic analysis. The capstone combines earlier terminal skills into a reviewable finding.",
        "The JSON report schema, supplied facts, and grader are original teaching design. Automated checks cover artifacts, not the quality of every inference.",
        _ref("nist-86", "§3.3 · Analysis; §3.4 · Reporting", "Explains analysis, reporting, and considering alternative explanations.", "Professional application", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf#page=30"),
        _ref("nist-61", "RS.AN-06 and RS.AN-07 · Investigation records and incident data", "Supports retaining reviewable actions, data, and provenance.", "Incident response records", "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf#page=37")),
    "attack-paths": _basis(
        ["Adversarial reasoning", "Threat modeling", "Risk assessment"],
        "Thinking like an adversary here means explaining a feasible goal, starting access, and route across a boundary. It combines design-oriented threat modeling with risk-assessment questions.",
        "The attack-path JSON and request for a contradicting observation are our learning structure, not a standardized assessment template.",
        _ref("ms-model", "Create a model; Analyze threats", "Provides a method for reasoning about data flows, boundaries, and threats.", "Threat modeling method"),
        _ref("nist-30", "§3.2 · Tasks 2-1, 2-2, and 2-3", "Organizes threat sources, threat events, vulnerabilities, and predisposing conditions.", "Risk assessment method", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf#page=38")),
    "persistence-hunt": _basis(
        ["Threat hunting", "Host investigation"],
        "ATT&CK describes observed adversary uses of ordinary schedulers and startup mechanisms. These patterns guide evidence questions; matching a pattern alone does not establish compromise.",
        "The inert cron and LaunchAgent captures, approval labels, and presence-versus-execution check are course design. Real investigations need execution and ownership context.",
        _ref("cron", "Description; Detection Strategies", "Documents adversary use of cron and detection considerations.", "Observed adversary behavior"),
        _ref("launch-agent", "Description; Detection Strategies", "Documents adversary use of macOS LaunchAgents and detection considerations.", "Observed adversary behavior")),
    "investigation-evaluation": _basis(
        ["Risk assessment", "Forensic reasoning"],
        "Risk assessment asks about consequences and likelihood; investigation asks how well the evidence supports a finding. Keeping those questions separate helps choose a useful next observation.",
        "The rating labels, separate confidence field, unknown option, and next-test worksheet are Script Junky's teaching rubric. They are not NIST's assessment scales or a calculated probability.",
        _ref("nist-30", "§3.2 · Task 2-4 (likelihood), Task 2-5 (impact), Task 2-6 (risk)", "Separates likelihood and adverse impact when assessing risk.", "Risk assessment method", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf#page=42"),
        _ref("nist-86", "§3.3 · Analysis; §3.4 · Reporting, Alternative Explanations", "Supports testing explanations when information is incomplete.", "Investigation reasoning", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf#page=30")),
}


COMMAND_SOURCE_IDS = {
    "pwd / cd / ls": ["coreutils", "bash"],
    "man / command -v": ["man", "bash"],
    "find": ["find"],
    "file / stat": ["file", "coreutils"],
    "cat / head / tail": ["coreutils"],
    "grep": ["grep"],
    "awk": ["awk"],
    "sed / cut": ["sed", "coreutils"],
    "sort / uniq / wc": ["coreutils"],
    "printf / redirection": ["bash", "coreutils"],
    "test / loops / functions": ["bash"],
    "xargs / find -exec": ["find"],
    "curl": ["curl"],
    "wget": ["wget"],
    "brew": ["brew"],
    "apt / apt-get / dpkg": ["apt", "dpkg"],
    "dnf / rpm": ["dnf", "rpm"],
    "pacman": ["pacman"],
    "apk": ["apk"],
    "ps / lsof / ss": ["ps", "lsof", "ss"],
    "id / uname / env": ["coreutils"],
    "chmod / umask": ["coreutils", "bash"],
    "sha256sum / shasum": ["coreutils", "shasum"],
    "date / tar / cp": ["coreutils", "tar"],
    "shellcheck / sh -n": ["shellcheck", "bash"],
    "jq / python3": ["jq", "json"],
}


def command_references(name):
    return [dict(SOURCE_CATALOG[key], id=key) for key in COMMAND_SOURCE_IDS[name]]
