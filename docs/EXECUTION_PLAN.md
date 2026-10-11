# Execution plan and learner outcomes

## Stage 1 — Terminal-first foundation (delivered in v0.1)

Use a dependency-free Python application, POSIX shell exercises, SQLite persistence, and a loopback-only browser companion. This keeps the core usable from a terminal on a Mac or Linux machine without requiring a container, account, cloud service, or JavaScript build process.

The initial curriculum progresses through scope, navigation, quoting, pipelines, structured fields, permissions, package managers, HTTP retrieval, robust shell scripting, process inspection, hashes, timelines, threat modeling, and a capstone. Each lesson combines explanation, a specific task, a generated evidence directory, a worked recipe, feedback, a professional application, and a reasoning prompt.

Deliverables: 14 lessons, 26 command-family cards, 24 scheduled recall cards, synthetic practice evidence, artifact verification, a journal, a tagged script toolbox, full CLI access, a responsive dashboard, and JSON/Markdown/script exports.

## Stage 2 — Establish the practice loop (delivered in v0.1)

The learner reads a concept, starts a lab, enters its directory in a native terminal, and creates an output artifact using real tools. The checker compares artifacts with the case evidence and verifies the original source contents and mode bits. The first successful submission logs an evidence-check record.

The learner then writes down the commands they chose, what they observed, what they inferred, where uncertainty remains, and what they would collect next. Useful snippets become tagged toolbox entries. Recall cards revisit the syntax and reasoning on a growing interval.

Completion means the required artifacts match, not that professional competence has been certified. Written reasoning and general script reliability need human review. Commands are recorded voluntarily; the app does not secretly capture terminal history.

## Stage 3 — Build evidence-led adversarial reasoning (delivered in v0.2)

The Investigation coach starts with the business asset, an adversary's goal and starting access, the entry point, and a trust boundary. It asks what evidence the proposed path would produce, what might disprove it, and what permitted collection would reduce uncertainty. Impact, likelihood, and confidence are separate judgments with written reasons.

Nine guides cover authentication abuse, persistence, web shells, trusted-tool misuse, identity changes, writable configuration, data movement, ransomware indicators, and dependency trust. Each connects evidence prompts, corroboration, ordinary explanations, Linux/macOS collection context, defensive controls, ATT&CK behavior candidates where appropriate, and related terminal exercises.

Five illustrative industry contexts emphasize different assets: general Unix hosts, healthcare, finance, SaaS, and critical infrastructure. Selected observations determine guide relevance; asset priorities break ties. This is a transparent investigation order, not an automated likelihood estimate, host scan, or prevalence claim.

Four dated case studies use primary incident research or agency/vendor reporting: Volt Typhoon, Ivanti gateway exploitation, LockBit, and xz. They transfer investigative habits while explaining product/platform limits. Source links connect the curriculum to MITRE ATT&CK, NIST CSF 2.0, NIST SP 800-30 Rev. 1, NIST SP 800-61 Rev. 3, CIS Controls v8.1, and STRIDE. These mappings guide learning and do not certify compliance.

Three new labs practice attack paths, captured startup definitions, and an evidence-linked threat evaluation. Eight additional recall cards revisit reasoning habits. A structured worksheet saves to the existing journal and exports; CLI commands expose the method, plans, individual guides, and historical cases without requiring a browser. Totals: 17 lessons, 26 command families, 32 recall cards. Existing lab fixtures and saved work remain compatible.

## Stage 4 — Verify portability and operation (partially delivered)

The local macOS test suite passes 26 tests: shell recipes, curl retrieval, edge-case script behavior, persistence, exports, malformed artifact rejection, API protections, and CLI flows. Coach tests check transparent plan ordering, valid lesson/source links, explicit unknown likelihood, traceable evidence IDs, counterevidence, and preservation of original and inert lab sources. The dashboard receives browser checks for navigation, forms, exercises, practice, and responsive layout.

Version 0.2 browser verification covers industry/platform plan selection, guide navigation, pattern search, all four historical cases, worksheet saving and persistence after reload, draft retention between coach sections, and startup-lab verification after running its terminal recipe. All nine evidence guides fit an 820-pixel tablet viewport without page overflow. This checks layout in a desktop browser, not native iPad execution.

The repository includes GitHub Actions jobs for Linux and macOS with Python 3.11 and 3.14. These run when the project is hosted and the workflow is triggered. Linux execution has not been verified in this workspace. Other Unix systems remain best-effort until a platform-specific compatibility test is added.

For iPad, the first practical route is the same responsive dashboard through an SSH tunnel, with terminal exercises running on the Mac/Linux host. The tunnel keeps the existing persistence model. Native iPad execution and offline learning require separate work.

## Stage 5 — Expand from repeatable practice to independent fluency (proposed)

1. Add varied datasets and challenges without recipes, including different log formats, noisy evidence, Unicode filenames, and empty results. Grade goals rather than one preferred command.
2. Expand scripting into getopts, loops, reusable functions, traps, temporary directories, bounded parallelism, JSON parsing, idempotence, and explicit performance tradeoffs. Add failure-injection exercises and static lint feedback.
3. Introduce ordered task playbooks built from toolbox entries, with declared inputs, platform requirements, expected artifacts, and manual checkpoints. Validate each component before allowing any optional execution feature.
4. Add supervised host-triage modules for authorized lab machines: process parents, effective permissions, scheduled jobs, user/service inventory, and local network context. Document observation side effects and privilege requirements.
5. Add isolated VM/container investigation cases, original evidence manifests, stronger acquisition workflows, peer review of hypotheses, and a report rubric that rewards uncertainty and corroboration.
6. Add explicit import/merge and optional encrypted device sync. Build an offline iPad reader before evaluating a native shell integration.

These are roadmap items, not features included in v0.2. Additional cases should bring varied evidence and explicit source review rather than relying on old indicators. Peer review and a richer assessment rubric would help evaluate reasoning beyond the artifact checker.

## How this maps to professional work

Ethical security analysts use small scripts to make a bounded task repeatable: inventory a service, reduce logs, compare a baseline, verify copied artifacts, or prepare a report. Good scripts have clear inputs, quoted paths, deterministic outputs, visible errors, platform requirements, and documented assumptions.

Adversarial thinking develops by asking who can control an input, where it crosses into a more trusted component, what asset could be affected, and which control could be tested. The permission and threat-modeling exercises make that connection without requiring exploitation.

Forensic thinking develops by preserving originals, identifying examined bytes, keeping timestamps and source details, correlating independent observations, and distinguishing a sequence from a causal claim. The capstone asks the learner to combine those habits into a report another analyst can continue.

The desired result is a learner who can articulate a question, choose and inspect an appropriate Unix tool, build a reliable script, preserve its assumptions, collect bounded evidence, and explain both a finding and its limits.
