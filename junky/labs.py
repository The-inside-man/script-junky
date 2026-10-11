"""Generate bounded evidence and assess output artifacts, never submitted code."""
import hashlib
import json
import os
import re
import stat
from pathlib import Path

from .content import LESSON_MAP
from .storage import now

TRAINING = Path(__file__).resolve().parents[1] / "training"

AUTH = """2026-06-12T09:00:00Z lab sshd[101]: Failed password for invalid user backup from 192.0.2.23 port 44510 ssh2
2026-06-12T09:00:15Z lab sshd[101]: Failed password for invalid user backup from 192.0.2.23 port 44511 ssh2
2026-06-12T09:01:00Z lab sshd[102]: Failed password for analyst from 198.51.100.8 port 52101 ssh2
2026-06-12T09:01:20Z lab sshd[101]: Failed password for worker from 192.0.2.23 port 44512 ssh2
2026-06-12T09:01:30Z lab sshd[101]: Failed password for worker from 192.0.2.23 port 44513 ssh2
2026-06-12T09:02:00Z lab sshd[103]: Accepted password for worker from 192.0.2.23 port 44514 ssh2
2026-06-12T09:02:15Z lab sshd[102]: Failed password for analyst from 198.51.100.8 port 52102 ssh2
"""
FILES = {
    "evidence/logs/auth.log": AUTH,
    "evidence/logs/events.tsv": "timestamp\tsource\tevent\n2026-06-12T09:04:00Z\tfilewatch\tworker.conf modified\n2026-06-12T09:00:00Z\tsshd\tfailed login from 192.0.2.23\n2026-06-12T09:03:00Z\tprocess\tPID 4242 /tmp/worker-helper started\n2026-06-12T09:02:00Z\tsshd\taccepted login for worker from 192.0.2.23\n",
    "evidence/system/listeners.tsv": "pid\tprocess\tservice\taddress\tport\n100\tsshd\tssh\t0.0.0.0\t22\n300\tpython\tdebug-api\t0.0.0.0\t8080\n200\tpostgres\tdatabase\t127.0.0.1\t5432\n",
    "evidence/system/processes.tsv": "pid\towner\texecutable\tparent\n1\troot\t/sbin/init\t0\n100\troot\t/usr/sbin/sshd\t1\n300\tworker\t/usr/bin/python3\t1\n4242\tworker\t/tmp/worker-helper\t300\n",
    "evidence/system/packages.tsv": "name\tversion\tbaseline\nopenssh\t9.0-lab\texpected\npython3\t3.12-lab\texpected\nworker-helper\t0.1-lab\tunexpected\n",
    "evidence/config/worker.conf": "# Fictional worker configuration\nlisten=0.0.0.0\nport=8080\ndebug=true\njob_dir=/srv/worker/jobs\n",
    "evidence/config/.env.sample": "# Synthetic example, never a real credential\nLAB_TOKEN=fictional-training-value\n",
    "evidence/notes/incident note.txt": "Case 001: repeated login failures, then a successful worker login.\nInvestigate without assuming the process is malicious. All evidence is synthetic.\n",
    "evidence/files/policy.txt": "Lab policy: configurations may only be changed by the service owner.\n",
    "evidence/files/report.txt": "Synthetic evidence: worker activity needs additional validation.\n",
}
MANIFEST = {"case": "SJ-001", "synthetic": True, "artifact": "report.txt",
            "sha256": hashlib.sha256(FILES["evidence/files/report.txt"].encode()).hexdigest()}
MAX_ARTIFACT = 1024 * 1024

HUNT_FILES = {
    "evidence/hunts/host-map.tsv": "component\tasset\tinput\tidentity\tknown_limit\nworker\tjob integrity\tworker.conf\tworker\teffective privileges not captured\ndebug-api\tjob submissions\tnetwork requests\tworker\trouting and firewall not captured\n",
    "evidence/hunts/startup.tsv": "platform\tkind\tartifact\towner\tprogram\tbaseline\nlinux\tcron\tevidence/hunts/cron/worker.sample\tworker\t/tmp/worker-helper\tunapproved\nmacos\tlaunchagent\tevidence/hunts/launchagents/worker.sample.plist\tanalyst\t/tmp/worker-helper\tunapproved\nlinux\tcron\tevidence/hunts/cron/backup.sample\tbackup\t/usr/local/bin/approved-backup\tapproved\n",
    "evidence/hunts/cron/worker.sample": "# INERT SYNTHETIC EVIDENCE: do not install this captured definition\n*/5 * * * * worker /tmp/worker-helper --status\n",
    "evidence/hunts/cron/backup.sample": "# Approved synthetic backup definition, captured as text\n0 2 * * * backup /usr/local/bin/approved-backup\n",
    "evidence/hunts/launchagents/worker.sample.plist": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!-- INERT SYNTHETIC EVIDENCE: do not load this captured definition -->\n<plist version=\"1.0\"><dict><key>Label</key><string>lab.worker.helper</string><key>ProgramArguments</key><array><string>/tmp/worker-helper</string><string>--status</string></array><key>RunAtLoad</key><true/></dict></plist>\n",
    "evidence/hunts/observations.tsv": "id\tobservation\tlimitation\nE01\tFour failed SSH events from 192.0.2.23\tFailure alone does not establish access\nE02\tAn accepted worker login from the same address\tAccount owner approval is not captured\nE03\tPID 4242 runs from /tmp/worker-helper\tFull command line and session link are absent\nE04\tCaptured worker startup jobs are unapproved\tNo execution record was acquired\nE05\tA backup job is in the approved baseline\tApproval is a stated fixture fact\nE06\tworker.conf has the other-write mode bit\tEffective ACLs and consumer authority are unknown\nE07\tworker-helper package is outside the baseline\tPackage provenance is missing\nE08\tNo outbound-flow evidence was acquired\tAbsence of a source is not evidence of no transfer\n",
}
HUNT_LESSONS = {"attack-paths", "persistence-hunt", "investigation-evaluation"}


def fixtures_for(lesson_id):
    # Preserve the original fixture set for existing learner labs.
    return {**FILES, **HUNT_FILES} if lesson_id in HUNT_LESSONS else FILES


def validate_id(lesson_id):
    if lesson_id not in LESSON_MAP:
        raise ValueError("Unknown lesson")


def lab_path(store, lesson_id):
    validate_id(lesson_id)
    root = store.labs
    if root.is_symlink() or (root / lesson_id).is_symlink():
        raise ValueError("A lab directory cannot be a symbolic link")
    return root / lesson_id


def start_lab(store, lesson_id):
    path = lab_path(store, lesson_id)
    marker = path / ".scriptjunky-lab.json"
    if path.exists():
        if not marker.is_file() or marker.is_symlink():
            raise ValueError("Existing directory is not a Script Junky lab; no files were changed")
        record = json.loads(read_bounded(path, ".scriptjunky-lab.json"))
        if not isinstance(record, dict) or record.get("lesson_id") != lesson_id:
            raise ValueError("Lab marker does not match this lesson; no files were changed")
        seed_outputs(path, lesson_id)
        return lab_details(store, lesson_id)
    # Actual source files ship in the project, rather than existing only as
    # strings in Python. Keep their contents synchronized with the curriculum.
    evidence = {}
    for name, expected in fixtures_for(lesson_id).items():
        body = (TRAINING / name).read_text(encoding="utf-8")
        if body != expected:
            raise ValueError(f"Bundled training file changed: training/{name}")
        evidence[name] = body
    starters = starter_files(lesson_id)
    path.mkdir(parents=True, mode=0o700)
    for name, body in evidence.items():
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        target.chmod(0o666 if name == "evidence/config/worker.conf" else 0o600)
    seed_outputs(path, lesson_id, starters)
    marker.write_text(json.dumps({"lesson_id": lesson_id, "version": 1, "created_at": now()}, indent=2), encoding="utf-8")
    (path / "README.txt").write_text(
        "Script Junky synthetic training lab. All evidence is fictional.\n"
        "Work only in this directory. Preserve evidence; write artifacts in output/.\n"
        "Evidence and blank output templates are supplied. Fill in the templates or\n"
        "use the exercise commands to replace their contents with your findings.\n"
        "Your native terminal is real and is not sandboxed by this app.\n"
        "Artifact checks never execute scripts. Save commands and reasoning in the journal.\n", encoding="utf-8")
    return lab_details(store, lesson_id, created=True)


def starter_files(lesson_id):
    validate_id(lesson_id)
    return {name: (TRAINING / "starters" / lesson_id / name).read_text(encoding="utf-8")
            for name in LESSON_MAP[lesson_id]["output"].split(" + ")}


def seed_outputs(path, lesson_id, starters=None):
    """Add missing starter files without replacing a learner's existing work."""
    output = path / "output"
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise ValueError("The output directory must be a real lab directory")
    output.mkdir(mode=0o700, exist_ok=True)
    for name, body in (starters if starters is not None else starter_files(lesson_id)).items():
        target = path / name
        try:
            with target.open("x", encoding="utf-8") as handle:
                handle.write(body)
            target.chmod(0o600)
        except FileExistsError:
            # This also leaves dangling symbolic links untouched; previews and
            # assessment reject them through read_bounded.
            pass


def lab_details(store, lesson_id, created=False):
    path = lab_path(store, lesson_id)
    files = [{"path": name, "kind": kind}
             for kind, names in (("evidence", fixtures_for(lesson_id)),
                                 ("output", LESSON_MAP[lesson_id]["output"].split(" + ")))
             for name in names]
    return {"path": str(path), "created": created, "lesson_id": lesson_id, "files": files}


def prepare_labs(store):
    labs, errors = {}, {}
    for lesson_id in LESSON_MAP:
        try:
            labs[lesson_id] = start_lab(store, lesson_id)
        except (OSError, ValueError) as error:
            errors[lesson_id] = str(error)
    return labs, errors


def preview_file(store, lesson_id, relative):
    path = lab_path(store, lesson_id)
    allowed = {item["path"] for item in lab_details(store, lesson_id)["files"]}
    if relative not in allowed:
        raise ValueError("Choose an evidence or result file listed for this lesson")
    content = read_bounded(path, relative)
    return {"path": relative, "kind": "evidence" if relative in fixtures_for(lesson_id) else "output",
            "content": content, "absolute_path": str(path / relative)}


def read_bounded(path, relative):
    """Reject traversal, symlinks, devices, FIFOs, and excessive artifacts."""
    target = path / relative
    if not target.resolve().is_relative_to(path.resolve()):
        raise ValueError("Artifact points outside the lab")
    for part in [target, *list(target.parents)[:len(Path(relative).parts) - 1]]:
        if part.is_symlink():
            raise ValueError("Symbolic-link artifacts are not accepted")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(target, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Artifact must be a regular file")
        if info.st_size > MAX_ARTIFACT:
            raise ValueError("Artifact exceeds the 1 MiB limit")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            data = handle.read(MAX_ARTIFACT + 1)
        if len(data) > MAX_ARTIFACT:
            raise ValueError("Artifact exceeds the 1 MiB limit")
        return data.decode("utf-8")
    finally:
        os.close(fd)


def normalize_paths(text):
    return {line.strip().removeprefix("./") for line in text.splitlines() if line.strip()}


def object_artifact(path, filename):
    result = json.loads(read_bounded(path, filename))
    if not isinstance(result, dict):
        raise ValueError("Expected a JSON object")
    return result


def substantial_fields(obj, fields):
    return all(isinstance(obj.get(field), str) and len(obj[field].strip()) >= 16 for field in fields)


def check_lab(store, lesson_id):
    path = lab_path(store, lesson_id)
    if not path.exists():
        raise ValueError("Start this lab first")
    checks = []

    def check(label, predicate, success, hint):
        try:
            passed = bool(predicate())
            message = success if passed else hint
        except (OSError, ValueError, UnicodeError, TypeError, KeyError) as error:
            passed = False
            message = f"{hint} ({error})"
        checks.append({"label": label, "passed": passed, "message": message})

    def integrity():
        for name, original in fixtures_for(lesson_id).items():
            if read_bounded(path, name) != original:
                return False
            expected_mode = 0o666 if name == "evidence/config/worker.conf" else 0o600
            if stat.S_IMODE((path / name).stat().st_mode) != expected_mode:
                return False
        return True

    check("Source evidence intact", integrity, "Fixture contents and mode bits match the generated originals.",
          "Source evidence changed or is missing. Restore the original lab from a fresh data home; keep your work first.")

    read = lambda name: read_bounded(path, "output/" + name)
    obj = lambda name: object_artifact(path, "output/" + name)
    if lesson_id == "attack-paths":
        def attack_path():
            report = obj("attack-path.json")
            return substantial_fields(report, ["actor", "starting_access", "asset", "entry_point", "trust_boundary", "abuse_path", "preconditions", "counterevidence", "next_test"]) and "worker.conf" in report["entry_point"]
        check("Testable attack-path structure", attack_path,
              "Actor, asset, boundary, preconditions, counterevidence, and next test are recorded. Review feasibility manually.",
              "Write attack-path.json with all nine fields (16+ characters each) and identify worker.conf as the entry point.")
    elif lesson_id == "persistence-hunt":
        check("Startup leads", lambda: normalize_paths(read("startup-leads.txt")) == {"evidence/hunts/cron/worker.sample", "evidence/hunts/launchagents/worker.sample.plist"},
              "Both unapproved definitions are listed; the approved backup is excluded. Presence does not establish execution.",
              "Select rows marked unapproved in column 6 and save the artifact paths from column 3.")
    elif lesson_id == "investigation-evaluation":
        def evidence_ids():
            ids = obj("evaluation.json").get("evidence_ids")
            return isinstance(ids, list) and len(ids) >= 2 and all(isinstance(id, str) and id in {f"E{i:02}" for i in range(1, 9)} for id in ids) and len(set(ids)) == len(ids)
        def ratings():
            report = obj("evaluation.json")
            return report.get("impact") in ("low", "moderate", "high", "critical") and report.get("likelihood") in ("unknown", "unlikely", "plausible", "likely") and report.get("confidence") in ("low", "moderate", "high")
        check("Traceable observation references", evidence_ids, "At least two distinct observation IDs are referenced; evaluate their relevance yourself.", "Reference at least two distinct IDs from E01–E08 in evidence_ids.")
        check("Separate threat judgments", ratings, "Impact, likelihood, and confidence are distinct fields. No probability was calculated.", "Choose allowed values for impact, likelihood (including unknown), and confidence.")
        check("Alternative and next test", lambda: substantial_fields(obj("evaluation.json"), ["asset", "hypothesis", "alternative", "impact_reason", "likelihood_reason", "confidence_reason", "next_test", "conclusion"]),
              "Reasons, alternative, and next test are present; substantive analysis still needs human review.", "Write substantive reasons, an alternative explanation, a next test, and a bounded conclusion (16+ characters each).")
    elif lesson_id == "scope":
        check("Scope document", lambda: substantial_fields(obj("scope.json"), ["authorization", "target", "excluded", "stop_condition", "preservation"]),
              "All five scope fields contain substantive text; review their meaning yourself.", "Write scope.json with authorization, target, excluded, stop_condition, and preservation (at least 16 characters each).")
    elif lesson_id == "navigation":
        check("Complete file inventory", lambda: normalize_paths(read("inventory.txt")) == set(FILES),
              "All evidence files, including the dotfile, are included.", "Use find ./evidence -type f and include hidden files. Save only evidence paths.")
    elif lesson_id == "quoting":
        check("Quoted filename", lambda: read("note.txt") == FILES["evidence/notes/incident note.txt"],
              "The note's complete content matches.", "Read the full filename with quotes and save its content as note.txt.")
    elif lesson_id == "pipelines":
        def counts():
            rows = [line.split() for line in read("failures.txt").splitlines() if line.strip()]
            return len(rows) == 2 and all(len(row) == 2 for row in rows) and {ip: int(count) for count, ip in rows} == {"192.0.2.23": 4, "198.51.100.8": 2}
        check("Failure counts by source", counts, "Counts match: 4 for 192.0.2.23; 2 for 198.51.100.8.", "Filter failed events only, extract source IPs, sort, then uniq -c; write failures.txt.")
    elif lesson_id == "text-tools":
        check("All-interface services", lambda: read("exposed-services.txt").split() == ["debug-api", "ssh"],
              "debug-api and ssh bind to all IPv4 interfaces in this snapshot.", "Select column 4 equal to 0.0.0.0, print column 3, and sort the names.")
    elif lesson_id == "permissions":
        check("Writable configuration", lambda: normalize_paths(read("writable.txt")) == {"evidence/config/worker.conf"},
              "The world-writable worker configuration is identified.", "Find regular files with -perm -002 under ./evidence; do not chmod the originals.")
    elif lesson_id == "packages":
        check("Baseline deviation", lambda: read("unexpected-packages.txt").split() == ["worker-helper"],
              "worker-helper is the package marked unexpected.", "Select unexpected from column 3 and print the package name from column 1.")
    elif lesson_id == "http":
        check("Retrieved manifest", lambda: obj("manifest.json") == MANIFEST,
              "The local manifest matches the expected case and digest.", "Fetch /fixtures/manifest.json from the running dashboard and save output/manifest.json.")
    elif lesson_id == "scripts":
        check("Reusable script present", lambda: read("triage.sh").startswith("#!/bin/sh\n") and len(read("triage.sh")) > 100,
              "A POSIX shell script is present; its contents were not executed.", "Write output/triage.sh with a #!/bin/sh shebang, parameters, and input validation.")
        check("Triage results", lambda: read("summary.txt").splitlines() == ["failed=6", "accepted=1"],
              "Summary matches six failed events and one accepted event.", "Run your script manually and save its stdout to summary.txt.")
    elif lesson_id == "processes":
        check("Process lead", lambda: read("suspicious-processes.txt").split() == ["4242"],
              "PID 4242 executes from /tmp in the captured snapshot.", "Select executable paths beginning with /tmp/ and write only matching PIDs.")
    elif lesson_id == "hashes":
        def hashes():
            lines = [line.strip() for line in read("hashes.txt").splitlines() if line.strip()]
            actual = {}
            for line in lines:
                match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(?:\./)?(evidence/files/(?:policy|report)\.txt)", line)
                if not match:
                    return False
                actual[match[2]] = match[1].lower()
            expected = {name: hashlib.sha256(FILES[name].encode()).hexdigest() for name in ("evidence/files/policy.txt", "evidence/files/report.txt")}
            return len(lines) == 2 and actual == expected
        check("Evidence digests", hashes, "Both SHA-256 fingerprints match the source evidence.", "Hash policy.txt and report.txt and preserve the digest plus relative path in hashes.txt.")
    elif lesson_id == "timeline":
        rows = FILES["evidence/logs/events.tsv"].splitlines()
        check("Chronological events", lambda: read("timeline.tsv").splitlines() == [rows[0], *sorted(rows[1:])],
              "All events are present in UTC order, with the header preserved.", "Keep the first line as the header, sort the remaining rows, and write timeline.tsv.")
    elif lesson_id == "threat-model":
        check("Threat-model structure", lambda: substantial_fields(obj("threat-model.json"), ["asset", "entry_point", "trust_boundary", "abuse_case", "evidence", "mitigation", "verification", "confidence"]),
              "Eight required fields have substantive text. Evaluate assumptions and reasoning manually.", "Add asset, entry_point, trust_boundary, abuse_case, evidence, mitigation, verification, and confidence (16+ characters each).")
    elif lesson_id == "capstone":
        def facts():
            report = obj("case-report.json")
            return (report.get("failing_ip") == "192.0.2.23" and report.get("successful_ip") == "192.0.2.23"
                    and str(report.get("suspicious_pid")) == "4242" and report.get("evidence_hash") == MANIFEST["sha256"])
        check("Evidence-linked findings", facts, "The dominant source, successful login source, process lead, and report digest match.", "Check failing_ip, successful_ip, suspicious_pid, and evidence_hash against the source evidence.")
        check("Report reasoning fields", lambda: substantial_fields(obj("case-report.json"), ["conclusion", "limitations", "recommendations"]),
              "Reasoning fields are present. Review whether the conclusion is supported and appropriately bounded.", "Add substantive conclusion, limitations, and recommendations (16+ characters each).")
    result = {"lesson_id": lesson_id, "path": str(path), "passed": all(item["passed"] for item in checks), "checks": checks}
    store.record_check(lesson_id, result)
    return result
