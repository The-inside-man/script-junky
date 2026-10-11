import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from junky.coach import CASES, METHOD, PLAYBOOKS, build_plan
from junky.content import CARDS, LESSON_MAP
from junky.labs import FILES, HUNT_FILES, check_lab, start_lab
from junky.storage import Store


class CoachTests(unittest.TestCase):
    def test_plans_select_observation_overlap_before_asset_priority(self):
        plan = build_plan("healthcare", "linux", ["login-spike", "account-change", "login-spike"])
        self.assertEqual(plan["signals"], ["login-spike", "account-change"])
        self.assertEqual([g["id"] for g in plan["guides"]], ["identity", "authentication", "permission-risk"])
        self.assertEqual(len(plan["guides"][0]["matches"]), 2)
        self.assertEqual(plan["guides"][0]["evidence_context"], PLAYBOOKS[4]["paths"]["linux"])
        # Industry context may change the investigation order, but cannot invent a signal or verdict.
        self.assertNotIn("likelihood", plan)
        self.assertNotIn("risk_score", plan)
        self.assertEqual(len(build_plan()["guides"]), len(PLAYBOOKS))

    def test_unknown_inputs_are_rejected(self):
        for kwargs in [{"industry": {}}, {"platform": None}, {"signals": {}}, {"signals": [None]},
                       {"signals": ["typo"]}, {"signals": ["login-spike"] * 9}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_plan(**kwargs)

    def test_playbooks_offer_counterevidence_and_resolvable_learning_links(self):
        case_ids = {c["id"] for c in CASES}
        for guide in PLAYBOOKS:
            with self.subTest(guide=guide["id"]):
                self.assertTrue(guide["look_for"] and guide["corroborate"] and guide["alternatives"] and guide["next_test"])
                self.assertEqual(set(guide["paths"]), {"linux", "macos", "captured"})
                self.assertTrue(set(guide["lessons"]) <= set(LESSON_MAP))
                self.assertTrue(set(guide["cases"]) <= case_ids)
                self.assertTrue(all(t["url"].startswith("https://attack.mitre.org/techniques/") for t in guide["techniques"]))
        self.assertTrue(all(card["lesson_id"] in LESSON_MAP for card in CARDS))
        self.assertTrue(all(c["url"].startswith("https://") and c["published"] and c["limit"] for c in CASES))
        self.assertEqual(len(METHOD), 7)

    def test_terminal_coach_is_read_only_and_needs_no_workspace_database(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "not-created"
            entry = Path(__file__).resolve().parents[1] / "scriptjunky.py"
            for action in [["plan", "--industry", "finance", "--signal", "login-spike"],
                           ["show", "persistence"], ["method"], ["cases"]]:
                result = subprocess.run([os.sys.executable, str(entry), "--home", str(home), "investigate", *action],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertGreater(len(result.stdout), 100)
            self.assertFalse(home.exists())


class HuntLabTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="scriptjunky-hunts-")
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)

    def worked_report(self, lesson_id, artifact):
        path = Path(start_lab(self.store, lesson_id)["path"])
        result = subprocess.run(["/bin/sh", "-c", LESSON_MAP[lesson_id]["recipe"]], cwd=path,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        target = path / "output" / artifact
        self.assertTrue(check_lab(self.store, lesson_id)["passed"])
        return path, target, json.loads(target.read_text())

    def test_attack_path_requires_a_boundary_and_counterevidence(self):
        _, target, report = self.worked_report("attack-paths", "attack-path.json")
        del report["counterevidence"]
        target.write_text(json.dumps(report))
        self.assertFalse(check_lab(self.store, "attack-paths")["passed"])
        report["counterevidence"] = "Consumer privileges are absent from the permitted capture."
        report["entry_point"] = "Some unspecified configuration file."
        target.write_text(json.dumps(report))
        self.assertFalse(check_lab(self.store, "attack-paths")["passed"])

    def test_evaluation_rejects_untraceable_evidence_and_conflated_ratings(self):
        _, target, original = self.worked_report("investigation-evaluation", "evaluation.json")
        for changes in [{"evidence_ids": ["E01", "E01"]}, {"evidence_ids": ["E01", "E99"]},
                        {"evidence_ids": ["E01", {}]}, {"likelihood": "high"}, {"confidence": "likely"},
                        {"alternative": ""}, {"likelihood_reason": ""}, {"next_test": ""}]:
            with self.subTest(changes=changes):
                target.write_text(json.dumps({**original, **changes}))
                self.assertFalse(check_lab(self.store, "investigation-evaluation")["passed"])
        # Unknown likelihood is a valid explicit judgment, even with high potential impact.
        target.write_text(json.dumps({**original, "impact": "high", "likelihood": "unknown", "confidence": "low"}))
        self.assertTrue(check_lab(self.store, "investigation-evaluation")["passed"])

    def test_startup_hunt_excludes_approved_job_and_preserves_inert_sources(self):
        path = Path(start_lab(self.store, "persistence-hunt")["path"])
        result = subprocess.run(["/bin/sh", "-c", LESSON_MAP["persistence-hunt"]["recipe"]], cwd=path,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(check_lab(self.store, "persistence-hunt")["passed"])
        target = path / "output/startup-leads.txt"
        target.write_text(target.read_text() + "evidence/hunts/cron/backup.sample\n")
        self.assertFalse(check_lab(self.store, "persistence-hunt")["passed"])
        target.write_text("evidence/hunts/cron/worker.sample\nevidence/hunts/launchagents/worker.sample.plist\n")
        source = path / "evidence/hunts/cron/worker.sample"
        source.write_text(source.read_text() + "# changed\n")
        self.assertFalse(check_lab(self.store, "persistence-hunt")["passed"])

    def test_existing_lessons_keep_their_original_fixture_set(self):
        path = Path(start_lab(self.store, "navigation")["path"])
        actual = {str(p.relative_to(path)) for p in (path / "evidence").rglob("*") if p.is_file()}
        self.assertEqual(actual, set(FILES))
        self.assertFalse(actual.intersection(HUNT_FILES))
        self.assertFalse(start_lab(self.store, "navigation")["created"])


if __name__ == "__main__":
    unittest.main()
