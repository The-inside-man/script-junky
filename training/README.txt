SCRIPT JUNKY — SUPPLIED TRAINING FILES

Everything in this directory is fictional training material. It ships with the
project, so you can inspect the source files before starting the application.

evidence/
  config/.env.sample            Fictional token and hidden-file example
  config/worker.conf            Worker service settings
  logs/auth.log                Captured SSH authentication events
  logs/events.tsv              Unordered events for the timeline exercise
  system/listeners.tsv         Captured service bindings
  system/processes.tsv         Captured process inventory
  system/packages.tsv          Package inventory and a supplied baseline
  notes/incident note.txt       Filename-with-spaces exercise
  files/policy.txt              Evidence-integrity exercise
  files/report.txt              Evidence-integrity exercise
  hunts/                       Host map, observations, and inert startup records

starters/<lesson>/output/
  Blank result files with the correct filenames and JSON field names.
  These are starting points, not completed answers.

When you start the dashboard, Script Junky prepares all 17 lesson folders.
With the default checkout workflow they appear at:

  labs/scope/evidence/config/worker.conf
  labs/scope/output/scope.json
  labs/navigation/evidence/...
  labs/navigation/output/inventory.txt
  ...one working folder per lesson

The application displays the exact active directory in every lesson. Run the
provided cd command before using a relative evidence/ or output/ path.
If you choose --home, working labs go under that data directory unless you also
choose --labs-dir. Check commands in the dashboard include both locations.

Work in the lesson's labs/ copy. Keep this training/ library intact; new labs
copy from it. The permissions exercise sets the intended writable mode on the
working copy, inside a private lesson directory. Source-control checkouts do
not preserve all Unix permission bits.

Inspect the supplied evidence, then complete the provided output files using
your terminal or editor. Existing work and evidence are never overwritten when
you resume a lesson. The startup examples are inert text: do not register them
with cron, systemd, or launchd.
