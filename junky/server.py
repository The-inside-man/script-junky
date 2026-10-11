"""A loopback-only companion dashboard; no command-execution endpoint."""
import json
import platform
import secrets
import shutil
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from . import __version__
from .content import CARDS, COMMANDS, LESSONS, SOURCES
from .coach import build_plan, catalog
from .labs import MANIFEST, TRAINING, check_lab, prepare_labs, preview_file, start_lab

STATIC = Path(__file__).parent / "static"
TOOLS = ["sh", "bash", "zsh", "find", "file", "grep", "awk", "sed", "sort", "uniq", "curl", "wget", "sha256sum", "shasum", "ps", "lsof", "ss", "jq", "shellcheck"]
MANAGERS = ["brew", "apt-get", "dnf", "pacman", "apk", "pkg", "zypper"]


def doctor():
    tools = [{"name": name, "path": shutil.which(name), "required": name in ("sh", "find", "grep", "awk", "sort", "uniq")} for name in TOOLS]
    return {"platform": platform.system(), "release": platform.release(), "python": platform.python_version(),
            "executable": sys.executable, "tools": tools,
            "package_managers": [{"name": name, "path": shutil.which(name)} for name in MANAGERS if shutil.which(name)],
            "hash_available": bool(shutil.which("sha256sum") or shutil.which("shasum"))}


class LearningServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, store, port=8765):
        super().__init__(("127.0.0.1", port), Handler)
        self.store = store
        self.csrf = secrets.token_urlsafe(32)
        self.port = self.server_address[1]
        self.origins = {f"http://127.0.0.1:{self.port}", f"http://localhost:{self.port}"}
        self.hosts = {f"127.0.0.1:{self.port}", f"localhost:{self.port}"}
        self.labs, self.lab_errors = prepare_labs(store)


class Handler(BaseHTTPRequestHandler):
    server_version = "ScriptJunky/" + __version__

    def log_message(self, format, *args):
        # Local notes and snippets must not appear in access logs.
        pass

    def send(self, status, body, mime="application/json; charset=utf-8", attachment=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if attachment:
            self.send_header("Content-Disposition", f'attachment; filename="{attachment}"')
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def trusted_request(self):
        if self.headers.get("Host") not in self.server.hosts:
            self.send(403, {"error": "Use the loopback URL printed by Script Junky"})
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in self.server.origins:
            self.send(403, {"error": "Cross-origin requests are not permitted"})
            return False
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            self.send(403, {"error": "Cross-site requests are not permitted"})
            return False
        return True

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self.trusted_request():
            return
        url = urlsplit(self.path)
        path = url.path
        store = self.server.store
        try:
            if path in ("/", "/index.html", "/app.js", "/style.css", "/retro.css", "/favicon.svg"):
                name = "index.html" if path == "/" else path[1:]
                mime = {".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml"}[Path(name).suffix]
                self.send(200, (STATIC / name).read_bytes(), mime + "; charset=utf-8")
            elif path == "/api/state":
                progress = store.progress()
                self.send(200, {"version": __version__, "csrf": self.server.csrf,
                                "lessons": LESSONS, "commands": COMMANDS, "sources": SOURCES,
                                "coach": catalog(),
                                "labs": self.server.labs, "lab_errors": self.server.lab_errors,
                                "labs_dir": str(store.labs), "training_dir": str(TRAINING),
                                "progress": progress, "journal": store.list_items("journal"), "snippets": store.list_items("snippets"),
                                "due_count": len(store.due_cards()), "card_count": len(CARDS), "doctor": doctor(),
                                "data_home": str(store.home), "base_url": f"http://127.0.0.1:{self.server.port}",
                                "cli": f"{shlex_quote(sys.executable)} {shlex_quote(str(STATIC.parent.parent / 'scriptjunky.py'))}"})
            elif path == "/api/lab/file":
                query = parse_qs(url.query)
                self.send(200, preview_file(store, query.get("lesson_id", [""])[0], query.get("path", [""])[0]))
            elif path == "/api/cards":
                cards = []
                for card in store.due_cards():
                    choices = card["choices"][:]
                    secrets.SystemRandom().shuffle(choices)
                    cards.append({"id": card["id"], "question": card["question"], "choices": choices, "lesson_id": card["lesson_id"]})
                secrets.SystemRandom().shuffle(cards)
                self.send(200, cards)
            elif path == "/fixtures/manifest.json":
                self.send(200, MANIFEST)
            elif path == "/api/export":
                format = parse_qs(url.query).get("format", ["json"])[0]
                if format == "markdown":
                    self.send(200, store.markdown(), "text/markdown; charset=utf-8", "scriptjunky-notebook.md")
                elif format == "json":
                    self.send(200, json.dumps(store.export(), indent=2, ensure_ascii=False), attachment="scriptjunky-export.json")
                else:
                    self.send(400, {"error": "Choose json or markdown"})
            else:
                self.send(404, {"error": "Not found"})
        except (ValueError, OSError) as error:
            self.send(400, {"error": str(error)})

    def do_POST(self):
        if not self.trusted_request():
            return
        if not secrets.compare_digest(self.headers.get("X-ScriptJunky-Token", "").encode("utf-8"), self.server.csrf.encode("utf-8")):
            self.send(403, {"error": "Refresh the dashboard before saving"})
            return
        try:
            if self.headers.get("Transfer-Encoding"):
                raise ValueError("Chunked requests are not supported")
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 300000:
                self.send(413, {"error": "Request must be between 1 and 300000 bytes"})
                return
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("Expected application/json")
            self.connection.settimeout(10)
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError("Expected a JSON object")
            path = urlsplit(self.path).path
            store = self.server.store
            if path == "/api/coach/plan":
                result = build_plan(body.get("industry", "general"), body.get("platform", "captured"), body.get("signals", []))
            elif path == "/api/lab/start":
                result = start_lab(store, body.get("lesson_id"))
                self.server.labs[body["lesson_id"]] = result
                self.server.lab_errors.pop(body["lesson_id"], None)
            elif path == "/api/lab/check":
                result = check_lab(store, body.get("lesson_id"))
            elif path in ("/api/journal/save", "/api/snippets/save"):
                kind = path.split("/")[2]
                result = store.save_item(kind, body, body.get("id"))
            elif path in ("/api/journal/delete", "/api/snippets/delete"):
                store.delete_item(path.split("/")[2], body.get("id"))
                result = {"deleted": True}
            elif path == "/api/review":
                result = store.review(body.get("card_id"), body.get("answer"))
            else:
                self.send(404, {"error": "Not found"})
                return
            self.send(200, result)
        except (ValueError, OSError, TypeError, UnicodeError, TimeoutError) as error:
            self.send(400, {"error": str(error)})


def shlex_quote(value):
    import shlex
    return shlex.quote(value)


def serve(store, port=8765):
    server = LearningServer(store, port)
    print(f"Script Junky → http://127.0.0.1:{server.port}")
    print(f"Data: {store.home}\nPractice files: {store.labs}\n{len(server.labs)} lesson folders ready.\nKeep this terminal open. Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped. Your work is saved.")
    finally:
        server.server_close()
