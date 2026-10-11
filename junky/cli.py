"""Dependency-free CLI matching the dashboard's storage and assessment."""
import argparse
import json
import secrets
import shlex
import sys
from pathlib import Path

from .content import COMMANDS, LESSONS, LESSON_MAP
from .coach import CASES, METHOD, PLATFORMS, PLAYBOOK_MAP, PROFILES, SIGNALS, build_plan
from .labs import check_lab, prepare_labs, start_lab
from .server import doctor, serve
from .storage import Store


def parser():
    root = argparse.ArgumentParser(description="Script Junky · learn the shell, follow the evidence")
    root.add_argument("--home", type=Path, help="Local data directory (or set SCRIPTJUNKY_HOME)")
    root.add_argument("--labs-dir", type=Path, help="Practice folder location; defaults to project labs/ or the explicit data home")
    commands = root.add_subparsers(dest="command", required=True)
    ui = commands.add_parser("serve", help="Start the local companion dashboard")
    ui.add_argument("--port", type=int, default=8765)
    commands.add_parser("doctor", help="Detect Unix tools and package managers without installing anything")
    commands.add_parser("learn", help="Show the learning path and verified lessons")
    show = commands.add_parser("lesson", help="Read a lesson and its terminal recipe")
    show.add_argument("lesson_id", choices=list(LESSON_MAP))
    lab = commands.add_parser("lab", help="Prepare or assess the supplied practice files")
    lab.add_argument("action", choices=["start", "check", "prepare"])
    lab.add_argument("lesson_id", nargs="?", choices=list(LESSON_MAP))
    ref = commands.add_parser("commands", help="Search command reference cards")
    ref.add_argument("query", nargs="?", default="")
    commands.add_parser("practice", help="Review due command-fluency cards interactively")
    coach = commands.add_parser("investigate", help="Plan evidence-led hunts and learn adversarial reasoning")
    coach_actions = coach.add_subparsers(dest="action", required=True)
    coach_plan = coach_actions.add_parser("plan", help="Choose guides from reported observations and asset context")
    coach_plan.add_argument("--industry", choices=[item["id"] for item in PROFILES], default="general")
    coach_plan.add_argument("--platform", choices=[item["id"] for item in PLATFORMS], default="captured")
    coach_plan.add_argument("--signal", choices=[item["id"] for item in SIGNALS], action="append", default=[])
    coach_show = coach_actions.add_parser("show", help="Read one investigation playbook")
    coach_show.add_argument("playbook_id", choices=list(PLAYBOOK_MAP))
    coach_actions.add_parser("method", help="Read the adversarial reasoning method")
    coach_actions.add_parser("cases", help="Read source-linked historical case lessons")
    for kind in ("journal", "snippet"):
        group = commands.add_parser(kind, help=f"Manage your {'field journal' if kind == 'journal' else 'script toolbox'}")
        actions = group.add_subparsers(dest="action", required=True)
        listing = actions.add_parser("list")
        listing.add_argument("--search", default="")
        get = actions.add_parser("show")
        get.add_argument("id", type=int)
        for action in ("add", "edit"):
            edit = actions.add_parser(action)
            if action == "edit":
                edit.add_argument("id", type=int)
            edit.add_argument("--title", required=True)
            edit.add_argument("--file", type=Path, required=True, help="Read note text or script code from this UTF-8 file")
            if kind == "journal":
                edit.add_argument("--lesson", default="", choices=["", *LESSON_MAP])
            else:
                edit.add_argument("--tags", default="")
                edit.add_argument("--description", default="")
        delete = actions.add_parser("delete")
        delete.add_argument("id", type=int)
        if kind == "snippet":
            out = actions.add_parser("export")
            out.add_argument("id", type=int)
            out.add_argument("--output", type=Path, required=True)
    export = commands.add_parser("export", help="Export your notebook, snippets, progress, attempts, and reviews")
    export.add_argument("--format", choices=["json", "markdown"], default="json")
    export.add_argument("--output", type=Path, required=True)
    return root


def write_new(path, body):
    """Never silently replace an existing user file."""
    with path.expanduser().open("x", encoding="utf-8") as handle:
        handle.write(body)
    path.expanduser().chmod(0o600)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "doctor":
            info = doctor()
            print(f"{info['platform']} {info['release']} · Python {info['python']}")
            for item in info["tools"]:
                print(f"{'OK' if item['path'] else '--':2}  {item['name']:12} {item['path'] or 'not installed'}")
            print("Package managers: " + (", ".join(item["name"] for item in info["package_managers"]) or "none detected"))
            print("Core runtime: Python 3.11+. Optional tools are taught with platform notes.")
            return
        if args.command == "investigate":
            if args.action == "method":
                for index, item in enumerate(METHOD, 1):
                    print(f"\n{index}. {item['title']}\n{item['question']}\n{item['action']}")
            elif args.action == "cases":
                for item in CASES:
                    print(f"\n{item['title']} · {item['period']}\nPublished: {item['published']} · {item['publisher']}\n{item['observed']}\nLesson: {item['lesson']}\nLimits: {item['limit']}\nSource: {item['url']}")
            elif args.action == "show":
                item = PLAYBOOK_MAP[args.playbook_id]
                print(f"\n{item['title']}\nPossible attacker goal: {item['attacker_goal']}")
                for label, key in (("Look for", "look_for"), ("Corroborate", "corroborate"), ("Alternative explanations", "alternatives"), ("Defensive controls", "controls")):
                    print(f"\n{label}:")
                    for text in item[key]:
                        print(f"- {text}")
                print(f"\nNext test: {item['next_test']}\n\nCaptured-lab example (run only inside a matching practice lab):\n{item['lab_command']}")
                for source in item["techniques"]:
                    print(f"Possible behavior: {source['id']} {source['name']} · {source['url']}")
                for platform in PLATFORMS:
                    print(f"\n{platform['name']}: {item['paths'][platform['id']]}")
                print("\nPractice lessons: " + ", ".join(item["lessons"]))
                for case in CASES:
                    if case["id"] in item["cases"]:
                        print(f"Historical context: {case['title']} · {case['url']}")
            else:
                plan = build_plan(args.industry, args.platform, args.signal)
                print(f"{plan['context']['name']}\nAssets: {plan['context']['assets']}\n{plan['context']['focus']}\n\nFirst step: {plan['first_step']}")
                for guide in plan["guides"]:
                    item = PLAYBOOK_MAP[guide["id"]]
                    reason = "; ".join(guide["matches"]) or "asset-oriented baseline review"
                    print(f"\n{item['id']}: {item['title']}\nWhy: {reason}\nEvidence context: {guide['evidence_context']}\nNext test: {item['next_test']}")
                print(f"\n{plan['basis']}\nRead a guide: python3 scriptjunky.py investigate show authentication")
            return
        store = Store(args.home, labs_dir=args.labs_dir)
        if args.command == "serve":
            if not 0 <= args.port <= 65535:
                raise ValueError("Port must be between 0 and 65535")
            serve(store, args.port)
        elif args.command == "learn":
            complete = {item["lesson_id"] for item in store.progress()["completed"]}
            for index, item in enumerate(LESSONS, 1):
                print(f"{'✓' if item['id'] in complete else '·'} {index:02}  {item['id']:14} {item['title']}  ({item['minutes']} min)")
            print(f"\n{len(complete)}/{len(LESSONS)} labs verified. Read one with: python3 scriptjunky.py lesson navigation")
        elif args.command == "lesson":
            item = LESSON_MAP[args.lesson_id]
            practice_lab = start_lab(store, item["id"])
            print(f"\n{item['title']} · {item['track']} · {item['minutes']} minutes\n\n{item['goal']}\n")
            print(f"Practice files are ready. All evidence/ and output/ paths are relative to:\ncd {shlex.quote(practice_lab['path'])}\n")
            print("Evidence is supplied; result files contain blank starter templates for you to complete.\n")
            for paragraph in item["explain"]:
                print(paragraph + "\n")
            for index, step in enumerate(item["steps"], 1):
                print(f"{index}. {step}")
            print("\nWorked command recipe:\n")
            print(item["recipe"])
            print(f"\nExpected artifact: {item['output']}\n\nField application: {item['fieldwork']}\n\nThink like an adversary: {item['adversary']}\n\nJournal prompt: {item['reflection']}\n\nPortability: {item['portability']}")
            basis = item["provenance"]
            print(f"\nWhere this objective comes from · {' / '.join(basis['domains'])}\n")
            print(basis["context"] + "\n\n" + basis["authorship"])
            for ref in basis["references"]:
                print(f"\n{ref['title']}\n  Read: {ref['section']}\n  {ref['supports']}\n  {ref['url']}")
            print(f"\nCourse adaptation: {basis['adaptation']}\nReferences reviewed: {basis['reviewed_at']}")
        elif args.command == "lab":
            if args.action == "prepare":
                if args.lesson_id:
                    raise ValueError("Use lab prepare without a lesson to prepare all folders, or lab start LESSON for one")
                labs, errors = prepare_labs(store)
                print(f"{len(labs)} lesson folders ready at {store.labs}")
                for lesson_id, error in errors.items():
                    print(f"{lesson_id}: {error}", file=sys.stderr)
                if errors:
                    raise SystemExit(2)
            elif args.lesson_id is None:
                raise ValueError("Choose a lesson: lab start LESSON or lab check LESSON")
            elif args.action == "start":
                result = start_lab(store, args.lesson_id)
                print(f"{'Created' if result['created'] else 'Resuming'} synthetic lab:\ncd {shlex.quote(result['path'])}")
                home_flag = f" --home {shlex.quote(str(store.home))} --labs-dir {shlex.quote(str(store.labs))}"
                print(f"\nPractice in that directory. To check from anywhere:\n{shlex.quote(sys.executable)} {shlex.quote(str(Path(__file__).resolve().parents[1] / 'scriptjunky.py'))}{home_flag} lab check {args.lesson_id}")
                print("\nYour native shell is real; this app does not sandbox manually entered commands.")
            else:
                result = check_lab(store, args.lesson_id)
                for item in result["checks"]:
                    print(f"{'PASS' if item['passed'] else 'TRY ':4} {item['label']}: {item['message']}")
                print("\nLab verified and logged." if result["passed"] else "\nKeep practicing; see feedback above.")
                if not result["passed"]:
                    raise SystemExit(1)
        elif args.command == "commands":
            found = [item for item in COMMANDS if args.query.casefold() in
                     (" ".join(value for value in item.values() if isinstance(value, str)) + " " +
                      " ".join(ref["title"] for ref in item["references"])).casefold()]
            for item in found:
                print(f"\n{item['name']} · {item['category']} · {item['platform']}\n{item['purpose']}\n\n{item['example']}\n\n{item['note']}")
                for ref in item["references"]:
                    print(f"Read the manual: {ref['title']} · {ref['url']}")
            if not found:
                print("No matching commands.")
        elif args.command == "practice":
            cards = store.due_cards()
            secrets.SystemRandom().shuffle(cards)
            if not cards:
                print("All cards are scheduled for later. Come back when they are due.")
            for card in cards:
                choices = card["choices"][:]
                secrets.SystemRandom().shuffle(choices)
                print(f"\n{card['question']}")
                for index, choice in enumerate(choices, 1):
                    print(f"  {index}. {choice}")
                while True:
                    answer = input("Answer 1–4 (q to finish): ").strip()
                    if answer.lower() == "q":
                        return
                    if answer.isdigit() and 1 <= int(answer) <= len(choices):
                        break
                    print("Choose a listed number or q.")
                result = store.review(card["id"], choices[int(answer) - 1])
                print(f"{'Correct' if result['correct'] else 'Try again later'}: {result['answer']}\n{result['explanation']}\nNext review: {result['due_at']}")
        elif args.command in ("journal", "snippet"):
            kind = "journal" if args.command == "journal" else "snippets"
            if args.action == "list":
                items = store.list_items(kind, args.search)
                for item in items:
                    print(f"{item['id']:3}  {item['title']}  · {item['updated_at']}")
                if not items:
                    print("No entries yet.")
            elif args.action in ("show", "export"):
                item = next((item for item in store.list_items(kind) if item["id"] == args.id), None)
                if item is None:
                    raise ValueError("Entry not found")
                content = item["body"] if kind == "journal" else item["code"]
                if args.action == "export":
                    write_new(args.output, content + "\n")
                    print(f"Saved script to {args.output.resolve()}. Review before executing.")
                else:
                    print(f"{item['title']}\n\n{content}")
            elif args.action == "delete":
                store.delete_item(kind, args.id)
                print("Entry deleted.")
            else:
                body = args.file.read_text(encoding="utf-8")
                item = {"title": args.title}
                if kind == "journal":
                    item.update(body=body, lesson_id=args.lesson)
                else:
                    item.update(code=body, description=args.description, tags=args.tags)
                result = store.save_item(kind, item, args.id if args.action == "edit" else None)
                print(f"Saved entry {result['id']}: {result['title']}")
        elif args.command == "export":
            body = store.markdown() if args.format == "markdown" else json.dumps(store.export(), indent=2, ensure_ascii=False) + "\n"
            write_new(args.output, body)
            print(f"Saved {args.format} export: {args.output.resolve()}")
    except (OSError, ValueError, EOFError) as error:
        print(f"Script Junky: {error}", file=sys.stderr)
        raise SystemExit(2)
