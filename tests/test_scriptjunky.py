import hashlib
import http.client
import json
import os
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.parse import urlparse

from junky.content import CARDS, COMMANDS, LESSONS, LESSON_MAP, SOURCES
from junky.labs import FILES, HUNT_FILES, MANIFEST, TRAINING, check_lab, fixtures_for, prepare_labs, read_bounded, start_lab, starter_files
from junky.references import COMMAND_SOURCE_IDS, LESSON_PROVENANCE, SOURCE_CATALOG
from junky.server import LearningServer
from junky.storage import Store


class ReferenceTests(unittest.TestCase):
    def test_every_objective_and_command_has_resolved_primary_references(self):
        self.assertEqual(set(LESSON_PROVENANCE), {item["id"] for item in LESSONS})
        self.assertEqual(set(COMMAND_SOURCE_IDS), {item["name"] for item in COMMANDS})
        for lesson in LESSONS:
            with self.subTest(lesson=lesson["id"]):
                basis = lesson["provenance"]
                for field in ("domains", "context", "authorship", "adaptation", "reviewed_at", "references"):
                    self.assertTrue(basis[field])
                self.assertIn("original Script Junky wording", basis["authorship"])
                for ref in basis["references"]:
                    self.assertIn(ref["id"], SOURCE_CATALOG)
                    for field in ("title", "short_title", "publisher", "kind", "section", "supports", "role"):
                        self.assertTrue(ref[field])
        for item in [*SOURCES, *(ref for lesson in LESSONS for ref in lesson["provenance"]["references"]),
                     *(ref for command in COMMANDS for ref in command["references"])]:
            with self.subTest(source=item["id"]):
                parsed = urlparse(item["url"])
                self.assertEqual(parsed.scheme, "https")
                self.assertTrue(parsed.hostname)
                self.assertIsNone(parsed.username)
        for command in COMMANDS:
            self.assertTrue(command["references"])

    def test_scope_and_rating_rubric_distinguish_guidance_from_course_design(self):
        scope = LESSON_MAP["scope"]["provenance"]
        self.assertEqual(scope["domains"], ["Security assessment", "Incident response"])
        self.assertEqual({ref["id"] for ref in scope["references"]}, {"nist-115", "nist-61"})
        self.assertIn("RS.AN-06", scope["references"][1]["section"])
        self.assertIn("broader than threat analysis", scope["context"])
        evaluation = LESSON_MAP["investigation-evaluation"]["provenance"]
        self.assertIn("not NIST's assessment scales", evaluation["adaptation"])
        self.assertIn("Task 2-4", evaluation["references"][0]["section"])


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="scriptjunky-test-")
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)

    def test_journal_and_snippets_survive_restart_and_support_crud(self):
        note = self.store.save_item("journal", {"title": "Triage observation", "body": "Observed a process; no causation established.", "lesson_id": "processes"})
        snippet = self.store.save_item("snippets", {"title": "Count a log", "code": 'wc -l "$1"', "tags": "logs,triage"})
        reloaded = Store(self.temp.name)
        self.assertEqual(reloaded.list_items("journal", "causation")[0]["id"], note["id"])
        self.assertEqual(reloaded.list_items("snippets", "triage")[0]["id"], snippet["id"])
        updated = reloaded.save_item("journal", {"title": "Revised finding", "body": "Need more evidence before attribution."}, note["id"])
        self.assertEqual(updated["created_at"], note["created_at"])
        self.assertIn("Revised finding", reloaded.markdown())
        self.assertEqual(len(reloaded.export()["snippets"]), 4)
        reloaded.delete_item("journal", note["id"])
        self.assertEqual(reloaded.list_items("journal"), [])
        self.assertEqual(os.stat(reloaded.path).st_mode & 0o777, 0o600)

    def test_validation_and_literal_search(self):
        with self.assertRaises(ValueError):
            self.store.save_item("journal", {"title": "", "body": "test"})
        with self.assertRaises(ValueError):
            self.store.save_item("journal", {"title": "Bad lesson", "body": "text", "lesson_id": "../outside"})
        with self.assertRaises(ValueError):
            self.store.save_item("snippets", {"title": "Oversized", "code": "x" * 60001})
        self.assertEqual(self.store.list_items("snippets", "' OR 1=1"), [])

    def test_spaced_reviews_use_correctness_and_persist(self):
        card = CARDS[0]
        right = card["choices"][card["answer"]]
        result = self.store.review(card["id"], right)
        self.assertTrue(result["correct"])
        self.assertNotIn(card["id"], [item["id"] for item in Store(self.temp.name).due_cards()])
        wrong = next(choice for choice in card["choices"] if choice != right)
        result = self.store.review(card["id"], wrong)
        self.assertFalse(result["correct"])
        self.assertEqual(result["answer"], right)
        with self.assertRaises(ValueError):
            self.store.review(card["id"], "unlisted answer")

    def test_markdown_code_fences_do_not_break_on_saved_fences(self):
        self.store.save_item("snippets", {"title": "A fenced snippet", "code": "# ``` is part of the text\nprintf 'ok'"})
        self.assertIn("````sh", self.store.markdown())


class LabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="scriptjunky-labs-")
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)

    def execute_recipe(self, lesson_id):
        path = Path(start_lab(self.store, lesson_id)["path"])
        run = subprocess.run(["/bin/sh", "-c", LESSON_MAP[lesson_id]["recipe"]], cwd=path,
                             capture_output=True, text=True, timeout=10, env={**os.environ, "LC_ALL": "C"})
        self.assertEqual(run.returncode, 0, f"{lesson_id}: {run.stderr}")
        return path

    def test_project_ships_evidence_and_prepares_all_blank_result_files(self):
        for name, expected in {**FILES, **HUNT_FILES}.items():
            self.assertEqual((TRAINING / name).read_text(), expected)
        labs, errors = prepare_labs(self.store)
        self.assertEqual(errors, {})
        self.assertEqual(set(labs), set(LESSON_MAP))
        for lesson_id, lab in labs.items():
            with self.subTest(lesson=lesson_id):
                path = Path(lab["path"])
                self.assertEqual({file["path"] for file in lab["files"]},
                                 set(fixtures_for(lesson_id)) | set(starter_files(lesson_id)))
                for name, content in starter_files(lesson_id).items():
                    self.assertEqual((path / name).read_text(), content)
                    if name.endswith(".json"):
                        self.assertIsInstance(json.loads(content), dict)
                result = check_lab(self.store, lesson_id)
                self.assertTrue(result["checks"][0]["passed"], "Supplied evidence must start intact")
                self.assertFalse(result["passed"], "Blank starters must not count as completed work")
        self.assertFalse(self.store.progress()["completed"])
        self.assertFalse(self.store.list_items("journal"))

    def test_preparation_preserves_work_and_does_not_restore_changed_evidence(self):
        lab = Path(start_lab(self.store, "scope")["path"])
        target = lab / "output/scope.json"
        target.write_text('{"my_draft": "keep this work"}\n')
        evidence = lab / "evidence/logs/auth.log"
        evidence.write_text("a learner changed the evidence\n")
        labs, errors = prepare_labs(self.store)
        self.assertFalse(errors)
        self.assertFalse(labs["scope"]["created"])
        self.assertIn("keep this work", target.read_text())
        self.assertEqual(evidence.read_text(), "a learner changed the evidence\n")
        target.unlink()
        start_lab(self.store, "scope")
        self.assertEqual(json.loads(target.read_text())["authorization"], "")

    def test_explicit_lab_directory_is_shared_by_generation_and_assessment(self):
        root = Path(self.temp.name) / "visible-practice"
        store = Store(Path(self.temp.name) / "data", labs_dir=root)
        lab = Path(start_lab(store, "scope")["path"])
        self.assertEqual(lab, root.resolve() / "scope")
        self.assertFalse((store.home / "labs").exists())
        self.assertEqual(check_lab(store, "scope")["path"], str(lab))

    def test_worked_recipes_produce_correct_artifacts(self):
        # Execute native shell recipes on generated fixtures, not user scripts.
        ids = [item["id"] for item in LESSONS if item["id"] not in ("http", "capstone")]
        for lesson_id in ids:
            with self.subTest(lesson=lesson_id):
                self.execute_recipe(lesson_id)
                result = check_lab(self.store, lesson_id)
                self.assertTrue(result["passed"], result["checks"])
                self.assertGreaterEqual(len(result["checks"]), 2)
        self.assertEqual(len(self.store.progress()["completed"]), len(ids))
        self.assertEqual(len(self.store.list_items("journal")), len(ids))
        check_lab(self.store, "scope")
        self.assertEqual(len(self.store.list_items("journal")), len(ids), "Repeat checks must not duplicate journal records")

    def test_script_success_zero_matches_spaces_and_missing_input(self):
        path = self.execute_recipe("scripts")
        space_log = path / "output" / "a log with spaces.txt"
        space_log.write_text("no authentication events here\n")
        result = subprocess.run(["/bin/sh", "output/triage.sh", str(space_log)], cwd=path, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "failed=0\naccepted=0\n")
        result = subprocess.run(["/bin/sh", "output/triage.sh", "absent.log"], cwd=path, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("usage", result.stderr)

    def test_assessment_never_executes_a_submitted_script(self):
        path = Path(start_lab(self.store, "scripts")["path"])
        (path / "output/triage.sh").write_text("#!/bin/sh\ntouch output/should-not-exist\n# " + "untrusted submitted code " * 8)
        (path / "output/summary.txt").write_text("failed=6\naccepted=1\n")
        self.assertTrue(check_lab(self.store, "scripts")["passed"])
        self.assertFalse((path / "output/should-not-exist").exists())

    def test_macos_hash_fallback(self):
        import shutil
        if not shutil.which("shasum"):
            self.skipTest("shasum not installed on this host")
        path = Path(start_lab(self.store, "hashes")["path"])
        result = subprocess.run(["shasum", "-a", "256", "evidence/files/policy.txt", "evidence/files/report.txt"], cwd=path, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        (path / "output/hashes.txt").write_text(result.stdout)
        self.assertTrue(check_lab(self.store, "hashes")["passed"])

    def test_missing_wrong_and_changed_evidence_do_not_pass(self):
        path = Path(start_lab(self.store, "quoting")["path"])
        self.assertFalse(check_lab(self.store, "quoting")["passed"])
        (path / "output/note.txt").write_text("wrong note")
        self.assertFalse(check_lab(self.store, "quoting")["passed"])
        (path / "output/note.txt").write_text(FILES["evidence/notes/incident note.txt"])
        (path / "evidence/logs/auth.log").write_text("tampered\n")
        self.assertFalse(check_lab(self.store, "quoting")["passed"])
        self.assertFalse(self.store.progress()["completed"])

    def test_lab_start_is_idempotent_and_refuses_unmarked_or_linked_dirs(self):
        path = self.execute_recipe("quoting")
        self.assertFalse(start_lab(self.store, "quoting")["created"])
        self.assertTrue((path / "output/note.txt").is_file())
        with self.assertRaises(ValueError):
            start_lab(self.store, "../../outside")
        (self.store.home / "labs/scope").mkdir()
        with self.assertRaises(ValueError):
            start_lab(self.store, "scope")
        (self.store.home / "labs/permissions").symlink_to(path, target_is_directory=True)
        with self.assertRaises(ValueError):
            start_lab(self.store, "permissions")

    def test_artifacts_reject_symlinks_fifos_and_large_files(self):
        path = Path(start_lab(self.store, "quoting")["path"])
        target = path / "output/note.txt"
        target.unlink()  # Replace the supplied blank starter for this rejection test.
        target.symlink_to(path / "evidence/notes/incident note.txt")
        self.assertFalse(check_lab(self.store, "quoting")["passed"])
        target.unlink()
        os.mkfifo(target)
        with self.assertRaises(ValueError):
            read_bounded(path, "output/note.txt")
        target.unlink()
        target.write_text("x" * (1024 * 1024 + 1))
        with self.assertRaises(ValueError):
            read_bounded(path, "output/note.txt")

    def test_capstone_assesses_key_facts_and_reasoning_fields(self):
        path = Path(start_lab(self.store, "capstone")["path"])
        report = {"failing_ip": "192.0.2.23", "successful_ip": "192.0.2.23", "suspicious_pid": 4242,
                  "evidence_hash": MANIFEST["sha256"],
                  "conclusion": "The observed sequence warrants investigation but does not prove compromise.",
                  "limitations": "Captured snapshots lack process command lines and independent clock verification.",
                  "recommendations": "Collect authorized parent-process and configuration ownership evidence next."}
        target = path / "output/case-report.json"
        target.write_text(json.dumps(report))
        self.assertTrue(check_lab(self.store, "capstone")["passed"])
        report["evidence_hash"] = "0" * 64
        target.write_text(json.dumps(report))
        self.assertFalse(check_lab(self.store, "capstone")["passed"])


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="scriptjunky-http-")
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.server = LearningServer(self.store, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close_server)

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.port, timeout=5)
        self.addCleanup(connection.close)
        defaults = {"Content-Type": "application/json", "X-ScriptJunky-Token": self.server.csrf}
        defaults.update(headers or {})
        connection.request(method, path, json.dumps(body) if body is not None else None, defaults)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()

    def test_actual_http_lab_recipe(self):
        path = Path(start_lab(self.store, "http")["path"])
        recipe = LESSON_MAP["http"]["recipe"].replace(":8765", f":{self.server.port}")
        result = subprocess.run(["/bin/sh", "-c", recipe], cwd=path, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(check_lab(self.store, "http")["passed"])

    def test_state_and_drills_do_not_disclose_answers(self):
        status, headers, body = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)["lessons"]), len(LESSONS))
        self.assertEqual(len(json.loads(body)["coach"]["playbooks"]), 9)
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        status, _, body = self.request("GET", "/api/cards")
        cards = json.loads(body)
        self.assertEqual(len(cards), len(CARDS))
        self.assertTrue(all("answer" not in card and "explanation" not in card for card in cards))

    def test_state_delivers_objective_provenance_and_command_manuals(self):
        status, _, body = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        state = json.loads(body)
        self.assertEqual(len(state["lessons"]), len(LESSONS))
        for lesson in state["lessons"]:
            self.assertEqual(lesson["provenance"], LESSON_MAP[lesson["id"]]["provenance"])
        self.assertEqual(len(state["commands"]), len(COMMANDS))
        for command in state["commands"]:
            self.assertTrue(command["references"])

    def test_dashboard_provides_ready_files_and_bounded_live_previews(self):
        state = json.loads(self.request("GET", "/api/state")[2])
        self.assertEqual(set(state["labs"]), set(LESSON_MAP))
        self.assertEqual(state["lab_errors"], {})
        status, _, body = self.request("GET", "/api/lab/file?lesson_id=scope&path=evidence/config/worker.conf")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["content"], FILES["evidence/config/worker.conf"])
        result_path = Path(state["labs"]["scope"]["path"]) / "output/scope.json"
        result_path.write_text('{"draft": "this is the real working file"}\n')
        status, _, body = self.request("GET", "/api/lab/file?lesson_id=scope&path=output/scope.json")
        self.assertEqual(status, 200)
        self.assertIn("real working file", json.loads(body)["content"])
        for path in ("../learning.sqlite3", "/etc/passwd", "evidence/../../learning.sqlite3", ".scriptjunky-lab.json"):
            with self.subTest(path=path):
                self.assertEqual(self.request("GET", f"/api/lab/file?lesson_id=scope&path={path}")[0], 400)
        result_path.unlink()
        result_path.symlink_to(self.store.path)
        self.assertEqual(self.request("GET", "/api/lab/file?lesson_id=scope&path=output/scope.json")[0], 400)

    def test_mutations_require_token_and_same_origin(self):
        body = {"title": "HTTP note", "body": "A bounded synthetic observation."}
        self.assertEqual(self.request("POST", "/api/journal/save", body, {"X-ScriptJunky-Token": "wrong"})[0], 403)
        self.assertEqual(self.request("POST", "/api/journal/save", body, {"X-ScriptJunky-Token": "é"})[0], 403)
        self.assertEqual(self.request("POST", "/api/journal/save", body, {"Origin": "https://other.invalid"})[0], 403)
        self.assertEqual(self.request("GET", "/api/state", headers={"Host": "other.invalid"})[0], 403)
        self.assertEqual(self.request("POST", "/api/journal/save", body)[0], 200)
        self.assertEqual(len(self.store.list_items("journal")), 1)

    def test_coach_plan_validates_context_and_preserves_protection(self):
        request = {"industry": "finance", "platform": "macos", "signals": ["account-change", "login-spike"]}
        status, _, body = self.request("POST", "/api/coach/plan", request)
        self.assertEqual(status, 200)
        plan = json.loads(body)
        self.assertEqual(plan["guides"][0]["id"], "authentication")
        self.assertIn("independent", plan["context"]["questions"][1])
        self.assertIn("macos", plan["platform"])
        self.assertEqual(self.request("POST", "/api/coach/plan", request, {"X-ScriptJunky-Token": "wrong"})[0], 403)
        for key, value in [("industry", []), ("platform", "windows"), ("signals", ["invented"]), ("signals", "login-spike")]:
            with self.subTest(key=key, value=value):
                self.assertEqual(self.request("POST", "/api/coach/plan", {**request, key: value})[0], 400)

    def test_routes_exports_and_malformed_inputs(self):
        for path in ("/", "/app.js", "/style.css", "/favicon.svg", "/api/export?format=json", "/api/export?format=markdown"):
            with self.subTest(path=path):
                self.assertEqual(self.request("GET", path)[0], 200)
        self.assertEqual(self.request("GET", "/../storage.py")[0], 404)
        self.assertEqual(self.request("GET", "/api/export?format=unknown")[0], 400)
        self.assertEqual(self.request("POST", "/api/lab/start", {"lesson_id": "../bad"})[0], 400)
        self.assertEqual(self.request("POST", "/api/lab/start", {"lesson_id": []})[0], 400)
        self.assertEqual(self.request("POST", "/api/journal/save", {"title": "Bad", "body": 42})[0], 400)
        self.assertEqual(self.request("POST", "/api/review", {"card_id": CARDS[0]["id"], "answer": "bad"})[0], 400)


class CLITests(unittest.TestCase):
    def test_cli_explains_origins_and_prints_manual_urls(self):
        with tempfile.TemporaryDirectory(prefix="scriptjunky-references-cli-") as temp:
            cli = [os.sys.executable, str(Path(__file__).resolve().parents[1] / "scriptjunky.py"), "--home", temp]
            scope = subprocess.run([*cli, "lesson", "scope"], capture_output=True, text=True)
            self.assertEqual(scope.returncode, 0, scope.stderr)
            for text in ("Where this objective comes from", "original Script Junky wording", "§6.5", "RS.AN-06",
                         "nistspecialpublication800-115.pdf#page=51", "NIST.SP.800-61r3.pdf#page=37"):
                self.assertIn(text, scope.stdout)
            commands = subprocess.run([*cli, "commands", "curl"], capture_output=True, text=True)
            self.assertEqual(commands.returncode, 0, commands.stderr)
            self.assertIn("https://curl.se/docs/manpage.html", commands.stdout)
            search = subprocess.run([*cli, "commands", "Coreutils"], capture_output=True, text=True)
            self.assertEqual(search.returncode, 0, search.stderr)
            self.assertIn("sort / uniq / wc", search.stdout)

    def test_cli_workflow_and_nonclobbering_exports(self):
        with tempfile.TemporaryDirectory(prefix="scriptjunky-cli-") as temp:
            cli = [os.environ.get("PYTHON", os.sys.executable), str(Path(__file__).resolve().parents[1] / "scriptjunky.py"), "--home", temp]
            for args in (["learn"], ["lesson", "navigation"], ["commands", "curl"], ["lab", "start", "navigation"]):
                result = subprocess.run([*cli, *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([*cli, "lab", "check", "navigation"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, "Unfinished labs must return a failure status")
            file = Path(temp) / "note.txt"
            file.write_text("Observed a synthetic event; need more evidence.\n")
            result = subprocess.run([*cli, "journal", "add", "--title", "Case note", "--file", str(file)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            export = Path(temp) / "export.json"
            result = subprocess.run([*cli, "export", "--output", str(export)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(export.read_text())["format"], "scriptjunky-export")
            result = subprocess.run([*cli, "export", "--output", str(export)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, "Exports must not silently replace files")


if __name__ == "__main__":
    unittest.main()
