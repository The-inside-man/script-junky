YOUR SCRIPT JUNKY PRACTICE FOLDERS

Start the dashboard from the project directory:

  python3 scriptjunky.py serve

It automatically prepares all 17 lesson folders here. No manual mkdir, sample
log creation, or JSON-file setup is needed. For a terminal-only session, use:

  python3 scriptjunky.py lab prepare
  python3 scriptjunky.py lesson scope

For the scope lesson, the relative paths mean:

  labs/scope/evidence/          Supplied fictional files to inspect
  labs/scope/output/scope.json  Blank JSON starter to fill in

Run the cd command shown by the lesson before entering its commands. Preview
evidence and result files directly in the dashboard with the View buttons.

Each lesson has its own working evidence and output directory. These working
folders are excluded from source control, so your results stay local. The
original evidence and starter templates are included in ../training/.

Existing results and evidence are preserved on restart. Choosing --home uses
that directory's labs/ instead; --labs-dir selects an explicit working location.
The lesson always displays the actual path selected by the running application.
