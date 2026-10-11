'use strict';

const icons = {
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  path: '<path d="M5 4v16m0-12h8a4 4 0 0 1 0 8H5"/><circle cx="5" cy="4" r="2"/><circle cx="5" cy="20" r="2"/><circle cx="18" cy="8" r="2"/>',
  terminal: '<rect x="2" y="4" width="20" height="16" rx="3"/><path d="m6 9 3 3-3 3m7 0h5"/>',
  practice: '<path d="m13 2-9 12h7l-1 8 10-13h-7z"/>',
  book: '<path d="M4 3h13a2 2 0 0 1 2 2v16H6a3 3 0 0 1 0-6h13M4 3v15m4-11h7m-7 4h5"/>',
  box: '<path d="M3 7h18v13H3zM2 3h20v4H2zm7 8h6"/>',
  arrow: '<path d="M4 12h15m-5-5 5 5-5 5"/>',
  back: '<path d="M20 12H5m5-5-5 5 5 5"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  search: '<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>',
  copy: '<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>',
  shield: '<path d="m12 2 8 4v6c0 5-8 10-8 10S4 17 4 12V6z"/><path d="m8 11 3 3 5-6"/>',
  plus: '<path d="M12 4v16M4 12h16"/>',
  download: '<path d="M12 3v12m-4-4 4 4 4-4M4 16v5h16v-5"/>',
  light: '<path d="M8 17h8m-7 3h6M8 14a6 6 0 1 1 8 0v3H8z"/>',
};
const icon = name => `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.terminal}</svg>`;
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[ch]));
const navItems = [['overview', 'Overview', 'grid'], ['learn', 'Learning path', 'path'], ['coach', 'Investigation coach', 'shield'], ['commands', 'Command library', 'terminal'], ['practice', 'Daily practice', 'practice'], ['journal', 'Field journal', 'book'], ['toolbox', 'Script toolbox', 'box']];
let state;
let filters = {track: 'All', commands: 'All', search: ''};
let activeLabs = {};
let labResults = {};
let practice = {cards: [], index: 0, correct: 0, feedback: null, loading: false, busy: false};
let toastTimer;
let coachTab = 'plan';
let coachPrefs = {industry:'general', platform:'captured', signals:[]};
let coachPlan = null;
let worksheetDraft = {};

function toast(message) {
  const node = document.getElementById('toast');
  node.textContent = message;
  node.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove('visible'), 4000);
}

async function api(path, body) {
  const options = body ? {method: 'POST', headers: {'Content-Type': 'application/json', 'X-ScriptJunky-Token': state.csrf}, body: JSON.stringify(body)} : {};
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'The workspace could not complete that action.');
  return data;
}

async function refreshState() { state = await api('/api/state'); }
function completed() { return new Set(state.progress.completed.map(item => item.lesson_id)); }
function nextLesson() { return state.lessons.find(item => !completed().has(item.id)) || state.lessons[state.lessons.length - 1]; }
function dateLabel(value) { return new Date(value).toLocaleString(undefined, {month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'}); }
function tag(text, style = '') { return `<span class="tag ${style}">${escapeHTML(text)}</span>`; }
function heading(eyebrow, title, description, action = '') { return `<div class="page-heading"><div><div class="eyebrow">${escapeHTML(eyebrow)}</div><h1>${escapeHTML(title)}</h1><p>${escapeHTML(description)}</p></div>${action}</div>`; }
function codeBlock(code, id, label = 'TERMINAL · SHELL') { return `<div class="code-block"><div class="code-header"><span>${escapeHTML(label)}</span><button class="copy-button" data-copy-target="${escapeHTML(id)}" aria-label="Copy ${escapeHTML(label.toLowerCase())}">${icon('copy')} Copy</button></div><pre><code id="${escapeHTML(id)}">${escapeHTML(code)}</code></pre></div>`; }
function searchBox(placeholder) { return `<div class="search">${icon('search')}<label class="visually-hidden" for="search-input">${escapeHTML(placeholder)}</label><input id="search-input" data-search placeholder="${escapeHTML(placeholder)}" value="${escapeHTML(filters.search)}" autocomplete="off"></div>`; }
function emptyState(title, body, action = '') { return `<div class="empty">${icon('book')}<h3>${escapeHTML(title)}</h3><p>${escapeHTML(body)}</p>${action}</div>`; }
function cli(action) { return `${state.cli} --home ${shellQuote(state.data_home)} --labs-dir ${shellQuote(state.labs_dir)} ${action}`; }
function shellQuote(value) { return "'" + String(value).replace(/'/g, "'\"'\"'") + "'"; }

function overview() {
  const next = nextLesson();
  const count = completed().size;
  const stages = [
    ['Foundations', 'Orientation, quoting, and data pipelines'],
    ['System investigation', 'Permissions, packages, HTTP, and processes'],
    ['Automation', 'Parameters, validation, and reliable scripts'],
    ['Forensics', 'Integrity, timelines, and evidence-linked findings'],
    ['Adversarial thinking', 'Attack paths, persistence, and threat evaluation'],
  ];
  return `<section class="hero"><div class="hero-content"><div class="eyebrow"><span class="status-dot"></span> SESSION READY / CURIOSITY REQUIRED</div><h1>WELCOME TO<br><span>THE MACHINE.</span></h1><p>A terminal is a language. Learn the commands, follow the evidence, and build the scripts you’ll reach for in the field.</p><div class="hero-actions"><a class="button orange" href="#lesson:${next.id}">${count ? 'Continue learning' : 'Start your first lesson'} ${icon('arrow')}</a><a class="button ghost" href="#learn">Explore the path ${icon('arrow')}</a></div><div class="hero-note">MAC + LINUX / REAL TOOLS / YOUR OWN TERMINAL</div></div><div class="terminal-illustration" aria-label="Illustrated training output from an evidence analysis pipeline"><div class="terminal-top"><span class="terminal-dot"></span><span class="terminal-dot"></span><span class="terminal-dot"></span><span>CASE_001 / LAB PREVIEW</span></div><div class="terminal-body"><span class="line terminal-greeting">SCRIPT JUNKY :: FIELD TERMINAL</span><span class="line comment"># a question becomes a pipeline</span><span class="line"><span class="prompt">$</span> grep 'Failed' auth.log |</span><span class="line">  awk '{print $(NF-3)}' |</span><span class="line">  sort | uniq -c</span><span class="line terminal-output">4 192.0.2.23</span><span class="line terminal-output">2 198.51.100.8</span><span class="line comment"># a lead, not a verdict.</span><span class="line"><span class="prompt">$</span> <span class="cursor"></span></span></div><div class="terminal-bottom"><span>ILLUSTRATED TRAINING OUTPUT</span><span>READ / REASON / REPEAT</span></div></div></section>
    <div class="stats">${[[icon('path'), 'LABS VERIFIED', count, `/ ${state.lessons.length}`, 'Build a foundation that lasts'], [icon('terminal'), 'COMMAND FAMILIES', state.commands.length, '', 'Small tools, endless combinations'], [icon('practice'), 'CARDS DUE', state.due_count, '', 'Practice recall, then apply it'], [icon('box'), 'SAVED SCRIPTS', state.snippets.length, '', 'Your personal field toolbox']].map(([i,l,v,s,f]) => `<div class="stat"><div class="stat-label">${i}${l}</div><span class="stat-value">${v}<small>${s}</small></span><span class="stat-foot">${f}</span></div>`).join('')}</div>
    <div class="overview-grid"><section><div class="section-heading"><h2>Your next mission</h2><a href="#learn">View learning path ${icon('arrow')}</a></div><div class="card current-lesson"><div class="tags">${tag(next.track)}${tag(count === state.lessons.length ? 'Review' : 'Up next', 'orange')}</div><h3>${escapeHTML(next.title)}</h3><p>${escapeHTML(next.goal)}</p><div class="lesson-meta"><span>${icon('clock')} ${next.minutes} min</span><span>${icon('terminal')} ${escapeHTML(next.commands.slice(0, 3).join(' · '))}</span></div><div class="divider"></div><div class="progress-line"><span>Your learning path</span><span>${count} of ${state.lessons.length} verified</span></div><progress value="${count}" max="${state.lessons.length}" aria-label="Verified lab progress"></progress><div class="card-foot"><span class="hero-note">READ → PRACTICE → VERIFY → REFLECT</span><a class="button tiny" href="#lesson:${next.id}">Open lesson ${icon('arrow')}</a></div></div></section>
    <section><div class="section-heading"><h2>Training directory</h2></div><div class="card"><div class="stage-list">${stages.map(([name, desc], i) => {const labs = state.lessons.filter(item => item.track === name); return `<a class="stage" href="#learn"><span class="stage-number">0${i+1}</span><div><div class="stage-title">${name}</div><div class="stage-desc">${desc}</div></div><span class="stage-status">${labs.filter(item => completed().has(item.id)).length}/${labs.length}</span></a>`;}).join('')}</div></div><div class="field-tip"><div class="eyebrow">${icon('light')} FIELD NOTE 001</div><p>A good investigator separates what they observed from what they suspect. Let your scripts collect evidence. Let your reasoning connect it.</p></div></section></div>
    <a class="card small-card coach-entry" href="#coach"><span class="tile-icon">${icon('shield')}</span><div><h3>Learn what an adversary would look for.</h3><p>Connect reported observations to evidence hunts, defensive controls, and lessons from documented attacks.</p></div><span class="arrow">↗</span></a><div class="bottom-grid"><a class="card small-card" href="#journal"><span class="tile-icon">${icon('book')}</span><div><h3>Leave a trail you can follow.</h3><p>Record commands, observations, and the questions that come next.</p></div><span class="arrow">↗</span></a><a class="card small-card" href="#toolbox"><span class="tile-icon">${icon('box')}</span><div><h3>Keep the scripts that work.</h3><p>Turn a useful pipeline into a reusable tool. Tag it. Find it. Improve it.</p></div><span class="arrow">↗</span></a></div>`;
}

function learningPath() {
  return `${heading('THE LEARNING PATH', 'From curious to capable.', 'Learn the building blocks, then combine them into repeatable security work. Each lesson includes a terminal exercise, an artifact check, and references explaining the basis of its objective.')}
    <div class="search-row">${searchBox('Find a lesson or command…')}<div class="filters">${['All', 'Foundations', 'System investigation', 'Automation', 'Forensics', 'Adversarial thinking'].map(name => `<button class="filter ${filters.track === name ? 'active' : ''}" data-track="${name}">${name}</button>`).join('')}</div></div><div id="lesson-results" class="path-list">${lessonRows()}</div><div class="info-strip">${icon('shield')}<span>All practice evidence is synthetic. Your terminal is real: stay inside the generated lab and preserve original files.</span></div>`;
}

function lessonRows() {
  const done = completed();
  const lessons = state.lessons.filter(item => (filters.track === 'All' || item.track === filters.track) && `${item.title} ${item.goal} ${item.commands.join(' ')}`.toLowerCase().includes(filters.search.toLowerCase()));
  return lessons.map(item => `<div class="path-entry"><a class="path-item" href="#lesson:${item.id}"><span class="path-number ${done.has(item.id) ? 'complete' : ''}">${done.has(item.id) ? icon('check') : String(state.lessons.indexOf(item) + 1).padStart(2, '0')}</span><div class="path-copy"><h3>${escapeHTML(item.title)}</h3><p>${escapeHTML(item.goal)}</p></div><div class="path-side">${tag(item.track)}<span>${item.minutes} min</span>${icon('arrow')}</div></a><div class="path-sources"><span>READ THE BASIS</span>${referenceLinks(item.provenance.references.slice(0, 2))}<a href="#lesson:${item.id}">Why this objective? →</a></div></div>`).join('') || emptyState('No lessons match.', 'Try another command name or clear the track filter.');
}

function referenceLinks(references) {
  return references.map(ref => sourceLink(ref, ref.short_title)).join('<span class="source-separator" aria-hidden="true">/</span>');
}

function objectiveProvenance(item) {
  const basis = item.provenance;
  return `<section class="card lesson-section objective-provenance" aria-labelledby="objective-origin-title"><div class="eyebrow">SOURCE NOTES</div><h2 id="objective-origin-title">Where this objective comes from</h2><div class="tags">${basis.domains.map(domain=>tag(domain, 'gray')).join('')}</div><p>${escapeHTML(basis.context)}</p><p class="source-authorship"><strong>Course wording.</strong> ${escapeHTML(basis.authorship)}</p><div class="objective-readings">${basis.references.map(ref=>`<article class="objective-reading"><div class="mini-label">${escapeHTML(ref.role)}</div><h3>${sourceLink(ref)}</h3><div class="reading-meta">${escapeHTML(ref.publisher)} · ${escapeHTML(ref.kind)}</div><p class="reading-section"><strong>Read:</strong> ${escapeHTML(ref.section)}</p><p>${escapeHTML(ref.supports)}</p></article>`).join('')}</div><div class="course-adaptation"><div class="mini-label">HOW THE COURSE ADAPTS IT</div><p>${escapeHTML(basis.adaptation)}</p></div><div class="form-help">References reviewed ${escapeHTML(basis.reviewed_at)}. Section names help you find the passage if a site or PDF viewer does not jump to it.</div></section>`;
}

function labWorkspace(item, lab) {
  if (!lab) return `<section class="card lesson-section"><h2>Practice files need attention</h2><p>${escapeHTML(state.lab_errors[item.id] || 'The practice folder is unavailable.')}</p><button class="button secondary" data-lab-start="${item.id}">Prepare supplied files</button></section>`;
  const fileButtons = kind => lab.files.filter(file=>file.kind === kind).sort((a,b)=>a.path.localeCompare(b.path)).map(file=>`<button class="lab-file" data-lab-file="${escapeHTML(file.path)}" data-lesson="${item.id}" aria-label="Preview ${escapeHTML(file.path)}">${icon(kind === 'evidence' ? 'search' : 'book')}<span>${escapeHTML(file.path)}</span><span class="file-view-label">View</span></button>`).join('');
  return `<section class="card lesson-section practice-files" aria-labelledby="practice-files-title"><div class="eyebrow">YOUR FILES ARE READY</div><h2 id="practice-files-title">Open your practice folder</h2><p>All <code>evidence/</code> and <code>output/</code> paths in this exercise start here. The evidence and result templates are supplied; you do not need to create the folders.</p>${codeBlock(`cd ${shellQuote(lab.path)}`, 'lab-cd', 'START HERE · YOUR TERMINAL')}<div class="lab-files-grid"><details class="lab-file-list" open><summary>Evidence to inspect · ${lab.files.filter(file=>file.kind === 'evidence').length} files</summary><p class="form-help">Provided fictional evidence. Inspect these files without editing them.</p><div class="file-buttons">${fileButtons('evidence')}</div></details><div class="lab-file-list"><h3>Your result files</h3><p class="form-help">Blank starter files. Fill them in, or let your commands write the results.</p><div class="file-buttons">${fileButtons('output')}</div><p class="form-help">Preview a file here; edit your working copy in your terminal or text editor.</p></div></div></section>`;
}

async function openLabFile(lessonId, path) {
  const file = await api(`/api/lab/file?lesson_id=${encodeURIComponent(lessonId)}&path=${encodeURIComponent(path)}`);
  const node = document.getElementById('editor');
  node.innerHTML = `<div class="dialog-top"><h2 id="editor-title">${file.kind === 'evidence' ? 'Evidence file' : 'Your result file'}</h2><button type="button" data-close-editor aria-label="Close file preview">×</button></div><p class="file-preview-path">${escapeHTML(file.absolute_path)}</p><p>${file.kind === 'evidence' ? 'Supplied fictional evidence. Keep this source intact while you inspect it.' : 'This is your working result file. Blank fields are provided for you to complete in your terminal or editor.'}</p>${file.content ? codeBlock(file.content, 'file-preview-content', file.path) : '<div class="empty-file">This starter file is empty. The exercise commands will write your results here.</div>'}<p class="form-help">Read-only preview of the file on disk.</p>`;
  node.showModal();
}

function lessonPage(id) {
  const item = state.lessons.find(item => item.id === id);
  if (!item) return emptyState('Lesson not found.', 'Choose a lesson from the learning path.', '<a class="button" href="#learn">Learning path</a>');
  const lab = activeLabs[id] || state.labs[id];
  const result = labResults[id];
  const done = completed().has(id);
  const command = `${cli(`lab check ${id}`)}`;
  const idx = state.lessons.indexOf(item);
  const next = state.lessons[idx+1];
  const recipe = item.recipe.replace('SJ_URL=http://127.0.0.1:8765', `SJ_URL=${state.base_url}`);
  const guides = state.coach.playbooks.filter(guide=>guide.lessons.includes(id));
  return `<a class="back-link" href="#learn">${icon('back')} Back to the learning path</a><div class="lesson-layout"><div class="lesson-body"><section class="lesson-intro"><div class="tags">${tag(`LESSON ${String(idx+1).padStart(2,'0')}`)}${tag(item.track, 'gray')}${done ? tag('Verified') : ''}</div><h1>${escapeHTML(item.title)}</h1><p>${escapeHTML(item.goal)}</p><div class="objective-links" aria-label="Learning objective references"><span>REFERENCES</span>${referenceLinks(item.provenance.references)}</div><div class="lesson-meta"><span>${icon('clock')} ${item.minutes} minutes</span><span>${icon('terminal')} ${escapeHTML(item.commands.join(' · '))}</span></div></section>
    ${labWorkspace(item, lab)}
    ${objectiveProvenance(item)}
    <section class="card lesson-section"><h2>The building blocks</h2>${item.explain.map(text => `<p>${escapeHTML(text)}</p>`).join('')}</section>
    <section class="card lesson-section"><h2>Your field exercise</h2><ol class="step-list">${item.steps.map(text => `<li>${escapeHTML(text)}</li>`).join('')}</ol><div class="info-strip">${icon('terminal')}<span>Use the practice folder shown above. Supplied evidence is under evidence/; save your findings in the provided output/ files.</span></div>
    <details class="code-details"><summary>Show a worked command recipe</summary>${codeBlock(recipe, 'lesson-recipe')}<p>Try the exercise first, then use this recipe to compare approaches. Save useful pieces to your toolbox.</p><button class="button secondary tiny" data-save-recipe="${id}">${icon('plus')} Save recipe to toolbox</button></details></section>
    ${result ? `<section class="card lesson-section"><h2>${result.passed ? 'Artifacts verified' : 'Keep investigating'}</h2><div class="check-list">${result.checks.map(c => `<div class="check ${c.passed ? 'passed' : ''}"><strong>${c.passed ? '✓' : '↳'} ${escapeHTML(c.label)}</strong><p>${escapeHTML(c.message)}</p></div>`).join('')}</div><p>Checks inspect results and source integrity. They do not execute your scripts or judge every inference.</p>${result.passed && next ? `<a class="button" href="#lesson:${next.id}">Next lesson ${icon('arrow')}</a>` : ''}</section>` : ''}
    <section class="card lesson-section"><div class="eyebrow">THINK LIKE AN ADVERSARY</div><h2>A command is only the beginning.</h2><p>${escapeHTML(item.adversary)}</p>${guides.length ? `<div class="mini-label">FOLLOW THIS LEAD</div><div class="guide-links">${guides.map(guide=>`<a href="#hunt:${guide.id}">${escapeHTML(guide.title)} ↗</a>`).join('')}</div>` : '<a class="note-link" href="#coach">Open the Investigation coach ↗</a>'}<div class="divider"></div><h3>Reflect in your journal</h3><p>${escapeHTML(item.reflection)}</p><button class="button secondary" data-reflect="${id}">${icon('book')} Write a field note</button></section></div>
    <aside class="lesson-aside"><div class="card"><h3>${done ? 'Revisit your practice files' : 'Your practice files are ready'}</h3><p>Evidence and blank result files are already in your lesson folder. Open that folder in your terminal, complete the exercise, then check your work.</p>${lab ? `<div class="lab-path">${escapeHTML(lab.path)}</div>` : `<button class="button orange" data-lab-start="${id}">Prepare supplied files</button>`}<div class="divider"></div><div class="mini-label">RESULT FILES TO COMPLETE</div><div class="artifact">${escapeHTML(item.output)}</div><button class="button orange" data-lab-check="${id}">${icon('check')} Check my work</button><details><summary>Check from the terminal</summary>${codeBlock(command, 'check-command', 'CLI CHECK')}</details></div><div class="card"><div class="eyebrow">IN THE REAL WORLD</div><p>${escapeHTML(item.fieldwork)}</p><div class="fieldwork-references"><div class="mini-label">SOURCE BASIS</div>${referenceLinks(item.provenance.references)}<p class="form-help">An original course application. The source notes explain the connection and its limits.</p></div><div class="divider"></div><div class="mini-label">PLATFORM NOTES</div><p>${escapeHTML(item.portability)}</p><a class="note-link" href="#commands">Open the command library ↗</a></div></aside></div>`;
}

const coachTabs = [['plan','Plan an investigation'], ['method','Adversarial thinking'], ['patterns','Attack patterns'], ['cases','Historical cases'], ['worksheet','Threat worksheet']];
function sourceLink(item, label = item.title) { return `<a href="${escapeHTML(item.url)}" title="${escapeHTML(item.section || item.title)}" target="_blank" rel="noopener noreferrer">${escapeHTML(label)} ↗</a>`; }
function bulletList(items) { return `<ul class="hunt-list">${items.map(text=>`<li>${escapeHTML(text)}</li>`).join('')}</ul>`; }
function coachReferences() {
  return `<details class="card coach-sources"><summary>Frameworks and source material</summary><p>This curriculum uses these sources to guide questions and evidence collection. The mappings are teaching aids, not a compliance assessment. ATT&CK describes behaviors; NIST and CIS help organize risk and defenses.</p><div class="reference-grid">${state.coach.references.map(ref=>`<div><strong>${sourceLink(ref)}</strong><p>${escapeHTML(ref.purpose)}</p></div>`).join('')}</div><div class="form-help">Curated references reviewed ${escapeHTML(state.coach.reviewed_at)}. Historical cases are dated reports, not a live threat feed.</div></details>`;
}

function coachPage() {
  const tabs = `<div class="coach-tabs" role="group" aria-label="Investigation coach sections">${coachTabs.map(([id,label])=>`<button class="filter ${coachTab === id ? 'active' : ''}" data-coach-tab="${id}" aria-pressed="${coachTab === id}">${label}</button>`).join('')}</div>`;
  const content = {plan: investigationPlanner, method: adversarialMethod, patterns: attackPatterns, cases: historicalCases, worksheet: threatWorksheet}[coachTab]();
  return `${heading('THE INVESTIGATION COACH', 'A suspicious detail is a starting point.', 'Think in attacker goals. Follow the trust boundary. Look for corroboration, consider ordinary explanations, and choose the next useful test.')}<div class="coach-banner"><span class="tile-icon">${icon('shield')}</span><div><strong>Observe → hypothesize → test → evaluate → record</strong><p>9 guided evidence hunts · 5 industry contexts · 4 documented case studies</p></div><a class="button secondary tiny" href="#lesson:attack-paths">Try the attack-path lab ${icon('arrow')}</a></div>${tabs}${content}${coachReferences()}`;
}

function investigationPlanner() {
  return `<div class="coach-plan-layout"><section class="card"><div class="eyebrow">START WITH WHAT YOU KNOW</div><h2>Choose your investigation context.</h2><p>Use observed changes to narrow the questions. Select no observations to explore all nine patterns.</p><form id="coach-plan-form"><div class="form-field"><label for="coach-industry">Industry / asset context</label><select id="coach-industry" name="industry">${state.coach.profiles.map(p=>`<option value="${p.id}" ${coachPrefs.industry === p.id ? 'selected' : ''}>${escapeHTML(p.name)}</option>`).join('')}</select></div><div class="form-field"><label for="coach-platform">Evidence context</label><select id="coach-platform" name="platform">${state.coach.platforms.map(p=>`<option value="${p.id}" ${coachPrefs.platform === p.id ? 'selected' : ''}>${escapeHTML(p.name)}</option>`).join('')}</select></div><fieldset class="signal-options"><legend>What have you observed?</legend>${state.coach.signals.map(s=>`<label><input type="checkbox" name="signal" value="${s.id}" ${coachPrefs.signals.includes(s.id) ? 'checked' : ''}><span>${escapeHTML(s.label)}</span></label>`).join('')}</fieldset><button type="submit" class="button orange">Build investigation plan ${icon('arrow')}</button><p class="form-help">The plan uses your selections. It does not inspect your machine.</p><div id="coach-plan-error" class="form-error" role="alert"></div></form></section><section id="coach-plan-results" aria-live="polite">${investigationResults()}</section></div>`;
}

function investigationResults() {
  if (!coachPlan) return `<div class="card plan-intro"><div class="eyebrow">ASK A BETTER QUESTION</div><h2>What would an attacker need?</h2><p>Start with an asset and a plausible goal. Then ask which identity, input, or configuration could provide a path to it.</p><div class="question-stack"><div><span>01</span><p>What does this machine do, and what must keep working?</p></div><div><span>02</span><p>What access would make abuse possible?</p></div><div><span>03</span><p>What evidence could confirm or challenge that hypothesis?</p></div></div><a class="note-link" href="#lesson:investigation-evaluation">Practice evaluating a finding ↗</a></div>`;
  const ctx = coachPlan.context;
  return `<div class="card context-card"><div class="eyebrow">${escapeHTML(ctx.name.toUpperCase())}</div><h2>Protect the asset. Explain the path.</h2><p><strong>Assets:</strong> ${escapeHTML(ctx.assets)}</p><p>${escapeHTML(ctx.focus)}</p>${bulletList(ctx.questions)}<div class="divider"></div><p class="plan-basis">${escapeHTML(coachPlan.basis)}</p><p class="form-help">${escapeHTML(coachPlan.first_step)}</p></div><div class="section-heading hunt-results-heading"><h2>${coachPlan.guides.length} evidence hunts to explore</h2></div><div class="plan-hunts">${coachPlan.guides.map((result,i)=>{const guide = state.coach.playbooks.find(g=>g.id===result.id);return `<article class="card"><div class="mini-label">LEAD ${String(i+1).padStart(2,'0')}</div><h3><a href="#hunt:${guide.id}">${escapeHTML(guide.title)} ↗</a></h3><p>${escapeHTML(guide.attacker_goal)}</p><div class="tags">${result.matches.map(label=>tag(label,'gray')).join('') || tag('Exploration prompt','gray')}</div><p class="evidence-context">${escapeHTML(result.evidence_context)}</p><a class="button secondary tiny" href="#hunt:${guide.id}">Follow the evidence ${icon('arrow')}</a></article>`;}).join('')}</div>`;
}

function adversarialMethod() {
  return `<div class="method-list">${state.coach.method.map((step,i)=>`<article class="card method-step"><span class="method-number">${String(i+1).padStart(2,'0')}</span><div><h2>${escapeHTML(step.title)}</h2><h3>${escapeHTML(step.question)}</h3><p>${escapeHTML(step.action)}</p></div></article>`).join('')}</div><div class="card practice-links"><h3>Turn the reasoning into practice.</h3><div class="guide-links">${['attack-paths','persistence-hunt','investigation-evaluation'].map(id=>`<a href="#lesson:${id}">${escapeHTML(state.lessons.find(l=>l.id===id).title)} ↗</a>`).join('')}</div></div>`;
}

function patternRows() {
  const items = state.coach.playbooks.filter(g=>`${g.title} ${g.attacker_goal} ${g.look_for.join(' ')} ${g.techniques.map(t=>t.name).join(' ')}`.toLowerCase().includes(filters.search.toLowerCase()));
  return items.map(guide=>`<a class="card pattern-card" href="#hunt:${guide.id}"><div class="eyebrow">${guide.techniques.length ? 'POSSIBLE ADVERSARY BEHAVIOR' : 'EXPOSURE / TRUST BOUNDARY'}</div><h3>${escapeHTML(guide.title)} ${icon('arrow')}</h3><p>${escapeHTML(guide.attacker_goal)}</p><div class="tags">${guide.techniques.map(t=>tag(t.id,'gray')).join('') || tag('Condition to evaluate','gray')}</div><div class="pattern-foot">${guide.look_for.length} observation prompts · corroboration · alternatives · next test</div></a>`).join('') || emptyState('No patterns match.', 'Try an observation such as keys, configuration, package, or login.');
}
function attackPatterns() {
  return `<div class="search-row">${searchBox('Find an attack pattern or observation…')}</div><div id="pattern-results" class="pattern-grid">${patternRows()}</div><div class="info-strip">${icon('light')}<span>A pattern is a hypothesis to test. An unfamiliar file, a failed login, or a matching technique does not by itself establish an attack.</span></div>`;
}

function caseCard(item) {
  return `<article class="card case-card"><div class="tags">${tag('Historical case','orange')}${tag(item.period,'gray')}</div><h3>${escapeHTML(item.title)}</h3><div class="mini-label">REPORTED OBSERVATIONS</div><p>${escapeHTML(item.observed)}</p><div class="case-lesson"><div class="mini-label">TRANSFERABLE INVESTIGATION HABIT</div><p>${escapeHTML(item.lesson)}</p></div><p class="case-limit">${escapeHTML(item.limit)}</p><div class="case-source">Published ${escapeHTML(item.published)} · ${sourceLink(item,item.publisher)}</div></article>`;
}
function historicalCases() {
  return `<div class="info-strip">${icon('book')}<span>Learn the reasoning from documented incidents. Verify current product exposure and remediation using current vendor guidance.</span></div><div class="case-grid">${state.coach.cases.map(caseCard).join('')}</div>`;
}

const worksheetFields = [
  ['title','Investigation title','Name the question you are investigating.',false],
  ['asset','Asset and business function','What must remain confidential, accurate, or available?',true],
  ['scope','Authorized scope and time window','Host / case, permitted evidence, time zone, collection limits.',true],
  ['goal','Possible attacker goal and starting access','What could an adversary gain? What access would they need?',true],
  ['entry_point','Entry point','Which input, identity, service, or dependency provides a possible route?',true],
  ['trust_boundary','Trust boundary and preconditions','What crosses into a more trusted component? What remains unverified?',true],
  ['observation','Observed facts and evidence references','Record paths, IDs, timestamps, commands used, and the facts they establish.',true],
  ['hypothesis','Testable hypothesis','If this interpretation is true, what else should exist?',true],
  ['alternative','Alternative explanation / counterevidence','What ordinary activity or missing context could explain the observation?',true],
  ['next_test','Next permitted test and decision owner','Choose the observation that reduces uncertainty; name who should decide or respond.',true],
  ['conclusion','Finding, limitations, and a control to verify','State what is supported, what is unknown, and how you would test the proposed defense.',true],
];
function worksheetField([name,label,help,multiline]) {
  const id = `worksheet-${name}`;
  const required = true;
  return `<div class="form-field"><label for="${id}">${escapeHTML(label)}${required ? ' *' : ''}</label>${multiline ? `<textarea id="${id}" name="${name}" maxlength="3500" ${required ? 'required' : ''}>${escapeHTML(worksheetDraft[name] || '')}</textarea>` : `<input id="${id}" name="${name}" maxlength="140" required value="${escapeHTML(worksheetDraft[name] || '')}">`}<div class="form-help">${escapeHTML(help)}</div></div>`;
}
function threatWorksheet() {
  const ratings = [['impact',['low','moderate','high','critical']], ['likelihood',['unknown','unlikely','plausible','likely']], ['confidence',['low','moderate','high']]];
  return `<section class="card worksheet"><div class="eyebrow">REASONING YOU CAN REVIEW</div><h2>Write an evidence-led threat assessment.</h2><p>Each judgment needs its own reason. Save the worksheet as an editable field note; it is included in notebook exports. Required fields are marked *.</p><form id="threat-worksheet-form"><div class="worksheet-grid">${worksheetFields.slice(0,9).map(worksheetField).join('')}</div><div class="rating-grid">${ratings.map(([name,options])=>`<div class="rating-panel"><div class="form-field"><label for="worksheet-${name}">${name[0].toUpperCase()+name.slice(1)} *</label><select id="worksheet-${name}" name="${name}" required>${name !== 'likelihood' ? `<option value="" disabled ${worksheetDraft[name] ? '' : 'selected'}>Choose ${name}…</option>` : ''}${options.map(value=>`<option ${worksheetDraft[name] === value ? 'selected' : ''}>${value}</option>`).join('')}</select><div class="form-help">${escapeHTML(state.coach.risk_guidance[name])}</div></div><div class="form-field"><label for="worksheet-${name}_reason">Reason for ${name} *</label><textarea id="worksheet-${name}_reason" name="${name}_reason" maxlength="3500" required>${escapeHTML(worksheetDraft[name+'_reason'] || '')}</textarea></div></div>`).join('')}</div><div class="worksheet-grid">${worksheetFields.slice(9).map(worksheetField).join('')}</div><p class="form-help">${escapeHTML(state.coach.risk_guidance.decision)}</p><div id="worksheet-error" class="form-error" role="alert"></div><div class="actions-row"><button type="submit" class="button orange">${icon('book')} Save assessment to journal</button><a class="button secondary" href="#journal">Open field journal</a></div><p class="form-help">Save to keep your work between visits. Unsaved drafts stay in this page until you reload or close it.</p></form></section>`;
}

function huntPage(id) {
  const guide = state.coach.playbooks.find(g=>g.id===id);
  if (!guide) return emptyState('Investigation guide not found.', 'Choose a pattern from the Investigation coach.', '<a class="button" href="#coach">Investigation coach</a>');
  return `<a class="back-link" href="#coach">${icon('back')} Back to the Investigation coach</a>${heading('FOLLOW THE EVIDENCE',guide.title,guide.attacker_goal,`<button class="button orange" data-guide-note="${guide.id}">${icon('book')} Record this investigation</button>`)}<div class="hunt-layout"><div><section class="card"><div class="eyebrow">OBSERVATION IS NOT A VERDICT</div><h2>What to look for</h2>${bulletList(guide.look_for)}<div class="divider"></div><h3>Seek corroboration</h3>${bulletList(guide.corroborate)}<h3>Consider other explanations</h3>${bulletList(guide.alternatives)}<div class="next-test"><div class="mini-label">NEXT USEFUL TEST</div><p>${escapeHTML(guide.next_test)}</p></div></section><section class="card"><h2>Practice with captured evidence.</h2><p>Run this example inside the linked generated lab. These files are training evidence; the command does not collect from a live host.</p>${codeBlock(guide.lab_command,'hunt-command','CAPTURED LAB EVIDENCE')}<div class="guide-links">${guide.lessons.map(id=>`<a href="#lesson:${id}">${escapeHTML(state.lessons.find(l=>l.id===id).title)} ↗</a>`).join('')}</div></section>${guide.cases.length ? `<section class="hunt-cases"><h2>Learn from a documented incident</h2>${guide.cases.map(id=>caseCard(state.coach.cases.find(c=>c.id===id))).join('')}</section>` : ''}</div><aside><section class="card"><h3>Where the evidence comes from</h3>${state.coach.platforms.map(p=>`<div class="evidence-source"><div class="mini-label">${escapeHTML(p.name)}</div><p>${escapeHTML(guide.paths[p.id])}</p></div>`).join('')}</section><section class="card"><h3>Controls to investigate</h3>${bulletList(guide.controls)}<div class="divider"></div><h3>Related ATT&CK behaviors</h3>${guide.techniques.length ? `<ul class="source-links">${guide.techniques.map(t=>`<li>${sourceLink(t,t.id+' · '+t.name)}</li>`).join('')}</ul><p>These are possible behavior mappings. Use the linked technique details to test whether the evidence fits.</p>` : '<p>Writable configuration is a condition. The fixture does not show an attacker changing permissions or exploiting it.</p>'}</section></aside></div>${coachReferences()}`;
}

function commandLibrary() {
  return `${heading('YOUR REFERENCE SHELF', 'Know your tools.', 'Learn what each command does, when to use it, and where platform differences matter. Examples use bounded lab paths.')}
  <div class="search-row">${searchBox('Search tools, tasks, or syntax…')}<div class="filters">${['All','Text','Shell','HTTP','Packages','Forensics'].map(name => `<button class="filter ${filters.commands === name ? 'active' : ''}" data-category="${name}">${name}</button>`).join('')}</div></div><div id="command-results" class="command-grid">${commandRows()}</div>`;
}

function commandRows() {
  const items = state.commands.filter(item => (filters.commands === 'All' || item.category === filters.commands) && `${item.name} ${item.purpose} ${item.example} ${item.note} ${item.platform} ${item.references.map(ref=>ref.title).join(' ')}`.toLowerCase().includes(filters.search.toLowerCase()));
  return items.map(item => `<article class="card command-card">${tag(item.category)}<h3>${escapeHTML(item.name)}</h3><p>${escapeHTML(item.purpose)}</p>${codeBlock(item.example.replaceAll('http://127.0.0.1:8765', state.base_url), `command-${state.commands.indexOf(item)}`, item.platform.toUpperCase())}<p class="note">${escapeHTML(item.note)}</p><div class="command-references"><div class="mini-label">READ THE MANUAL</div>${referenceLinks(item.references)}<p class="form-help">Check the manual's platform and your local man page; GNU/Linux and macOS options can differ.</p></div></article>`).join('') || emptyState('No tools match.', 'Search for a task, like logs, files, packages, or hashes.');
}

function journalPage() {
  return `${heading('YOUR FIELD NOTEBOOK', 'Leave a useful trail.', 'Capture the question, scope, commands, observations, and next steps. Verified labs also add a record here.', `<button class="button orange" data-new="journal">${icon('plus')} New field note</button>`)}<div class="search-row">${searchBox('Search your notes…')}<a class="button secondary tiny" href="/api/export?format=markdown">${icon('download')} Export notebook</a></div><div id="journal-results" class="journal-list">${journalRows()}</div>`;
}

function journalRows() {
  const items = state.journal.filter(item => `${item.title} ${item.body} ${item.lesson_id}`.toLowerCase().includes(filters.search.toLowerCase()));
  return items.map(item => `<article class="card"><div class="entry-top"><h3>${escapeHTML(item.title)}</h3>${tag(item.kind === 'lab' ? 'Lab verified' : 'Field note', item.kind === 'lab' ? '' : 'gray')}</div><div class="entry-meta"><span>${escapeHTML(dateLabel(item.created_at))}</span>${item.lesson_id ? `<a class="note-link" href="#lesson:${item.lesson_id}">${escapeHTML(item.lesson_id)} ↗</a>` : '<span>General notes</span>'}</div><div class="entry-body">${escapeHTML(item.body)}</div><div class="entry-actions"><button class="text-button" data-edit-kind="journal" data-id="${item.id}">Edit note</button><button class="text-button danger" data-delete-kind="journal" data-id="${item.id}">Delete</button></div></article>`).join('') || emptyState('Your next finding starts here.', 'Write down what you tried, what you observed, and what you would do next. Your notebook stays on this machine.', '<button class="button" data-new="journal">Write your first note</button>');
}

function toolboxPage() {
  return `${heading('YOUR PERSONAL TOOLBOX', 'Build once. Reach for it again.', 'Save scripts with a purpose, assumptions, and searchable tags. Copy or download a snippet when you need it.', `<button class="button orange" data-new="snippets">${icon('plus')} Save a script</button>`)}<div class="search-row">${searchBox('Find a script, function, or tag…')}<span class="results-count">${state.snippets.length} scripts in your toolbox</span></div><div id="snippet-results" class="toolbox-grid">${snippetRows()}</div>`;
}

function snippetRows() {
  const items = state.snippets.filter(item => `${item.title} ${item.description} ${item.code} ${item.tags}`.toLowerCase().includes(filters.search.toLowerCase()));
  return items.map(item => `<article class="card snippet-card"><h3>${escapeHTML(item.title)}</h3><p class="description">${escapeHTML(item.description || 'Add assumptions, inputs, and expected output when you edit this snippet.')}</p><div class="tags">${item.tags.split(',').filter(t=>t.trim()).map(t => tag(t.trim(),'gray')).join('')}</div>${codeBlock(item.code, `snippet-${item.id}`, 'SAVED SHELL SNIPPET')}<div class="entry-actions"><button class="text-button" data-edit-kind="snippets" data-id="${item.id}">Edit script</button><button class="text-button" data-download="${item.id}">Download .sh</button><button class="text-button danger" data-delete-kind="snippets" data-id="${item.id}">Delete</button></div></article>`).join('') || emptyState('Make your first tool.', 'Save a useful command pipeline with its input format, failure modes, and intended scope.', '<button class="button" data-new="snippets">Save a script</button>');
}

function practicePage() {
  const head = heading('A LITTLE EVERY DAY', 'Make the commands stick.', 'Recall the building blocks, understand the reasoning, then apply them in a lab. Correct answers return after 1, 2, 4, 8, 16, then 30 days; misses return after 10 minutes.');
  if (practice.loading) return head + emptyState('Opening your practice deck…', 'Your review schedule is saved locally.');
  const card = practice.cards[practice.index];
  if (!card) return head + emptyState(practice.index ? 'Practice session complete.' : 'You’re up to date.', practice.index ? `${practice.correct} of ${practice.index} answers correct. Apply a command in your next lab while these cards settle.` : 'Your next reviews will appear when they are due. Continue learning or revisit the command library.', '<a class="button" href="#learn">Go to the learning path</a>');
  const f = practice.feedback;
  return head + `<div class="practice-wrap"><div class="practice-header"><span>Card ${practice.index+1} of ${practice.cards.length}</span><span>${practice.correct} correct this session</span></div><progress value="${practice.index}" max="${practice.cards.length}" aria-label="Practice session progress"></progress><section class="card practice-card"><div class="eyebrow">${escapeHTML(card.lesson_id.replaceAll('-',' '))} · COMMAND RECALL</div><h2>${escapeHTML(card.question)}</h2><div class="choices">${card.choices.map((choice,i)=>`<button class="choice ${f && choice === f.answer ? 'correct' : f && choice === f.selected && !f.correct ? 'wrong' : ''}" data-answer="${i}" ${f || practice.busy ? 'disabled' : ''}><span>${String.fromCharCode(65+i)}</span>${escapeHTML(choice)}</button>`).join('')}</div>${f ? `<div class="review-feedback ${f.correct ? '' : 'wrong'}"><strong>${f.correct ? 'You’ve got it.' : 'A useful one to revisit.'}</strong><p>${escapeHTML(f.explanation)}</p><small>Next review: ${escapeHTML(dateLabel(f.due_at))}</small></div><div class="actions-row"><button class="button" data-next-card>Next card ${icon('arrow')}</button><a class="button secondary" href="#lesson:${card.lesson_id}">Explore the lesson</a></div>` : ''}</section></div>`;
}

function systemPage() {
  const d = state.doctor;
  const port = escapeHTML(new URL(state.base_url).port);
  return `${heading('LOCAL WORKSPACE', 'Ready for your machine.', 'Your curriculum, notes, and scripts live locally. The dashboard serves only on loopback and runs without third-party Python packages.')}
    <div class="system-grid"><section class="card"><h2>Your environment</h2><p>${escapeHTML(d.platform)} ${escapeHTML(d.release)} · Python ${escapeHTML(d.python)}</p><div class="mini-label">DETECTED PACKAGE MANAGERS</div><div class="tags">${d.package_managers.map(item=>tag(item.name)).join('') || tag('None detected', 'gray')}</div><div class="tools-list">${d.tools.map(item=>`<div class="tool-row"><code>${escapeHTML(item.name)}</code><span class="${item.path ? '' : 'missing'}">${item.path ? 'Available' : item.required ? 'Needed for core labs' : 'Optional · not installed'}</span></div>`).join('')}</div></section>
    <div><section class="card"><h2>Your work is yours.</h2><p>SQLite stores your journal, scripts, verified labs, attempts, and review schedule. Export JSON for a portable record or Markdown for a readable field notebook.</p><div class="mini-label">DATA DIRECTORY</div><div class="local-path">${escapeHTML(state.data_home)}</div><div class="mini-label workspace-path-label">PRACTICE FOLDERS</div><div class="local-path">${escapeHTML(state.labs_dir)}</div><div class="mini-label workspace-path-label">SUPPLIED TRAINING LIBRARY</div><div class="local-path">${escapeHTML(state.training_dir)}</div><div class="actions-row"><a class="button secondary tiny" href="/api/export?format=json">${icon('download')} Export all data</a><a class="button secondary tiny" href="/api/export?format=markdown">${icon('book')} Export notebook</a></div><div class="divider"></div><h3>Take it on the go</h3><p>Use an SSH client with local port forwarding on your iPad to reach this Mac/Linux workspace. Forward the device’s localhost port ${port} to this host’s 127.0.0.1:${port}, then open http://127.0.0.1:${port} in Safari. Keep the tunnel active while Safari is open. Terminal commands run on the host through SSH. A native iPad shell is a future port.</p><p>The terminal you use is real. The app generates practice files and checks artifacts; it does not sandbox manually entered commands.</p></section>
    <section class="card code-details"><h2>Read the source material</h2><p>The curriculum teaches practical applications; local man pages and official manuals document the exact behavior on your system.</p><ul class="source-links">${state.sources.map(item=>`<li><a href="${escapeHTML(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(item.title)} ↗</a></li>`).join('')}</ul></section></div></div>`;
}

async function render() {
  if (!state) return;
  const route = (location.hash.slice(1) || 'overview').split(':');
  const view = route[0];
  const navView = view === 'lesson' ? 'learn' : view === 'hunt' ? 'coach' : view;
  document.getElementById('navigation').innerHTML = navItems.map(([id,label,i])=>`<a class="nav-link ${navView === id ? 'active' : ''}" href="#${id}" ${navView === id ? 'aria-current="page"' : ''} aria-label="${label}">${icon(i)}<span class="nav-text">${label}</span>${id === 'practice' && state.due_count ? `<span class="nav-count">${state.due_count}</span>` : ''}</a>`).join('');
  const label = navItems.find(([id])=>id === navView)?.[1] || 'Local workspace';
  document.getElementById('breadcrumb').textContent = label;
  document.getElementById('platform').textContent = `${state.doctor.platform === 'Darwin' ? 'macOS' : state.doctor.platform} · Local`;
  document.title = `${label} · Script Junky`;
  let body;
  if (view === 'overview') body = overview();
  else if (view === 'learn') body = learningPath();
  else if (view === 'lesson') body = lessonPage(route[1]);
  else if (view === 'coach') body = coachPage();
  else if (view === 'hunt') body = huntPage(route[1]);
  else if (view === 'commands') body = commandLibrary();
  else if (view === 'journal') body = journalPage();
  else if (view === 'toolbox') body = toolboxPage();
  else if (view === 'practice') body = practicePage();
  else body = systemPage();
  document.getElementById('main').innerHTML = body;
}

function updateSearchResults() {
  const view = location.hash.slice(1) || 'overview';
  const mappings = {learn: ['lesson-results', lessonRows], commands: ['command-results', commandRows], journal: ['journal-results', journalRows], toolbox: ['snippet-results', snippetRows], coach: ['pattern-results', patternRows]};
  const mapping = mappings[view];
  if (mapping && document.getElementById(mapping[0])) document.getElementById(mapping[0]).innerHTML = mapping[1]();
}

function openEditor(kind, item = {}) {
  const journal = kind === 'journal';
  const node = document.getElementById('editor');
  node.innerHTML = `<form id="entry-form" data-kind="${kind}"><div class="dialog-top"><h2 id="editor-title">${item.id ? 'Edit' : 'New'} ${journal ? 'field note' : 'saved script'}</h2><button type="button" data-close-editor aria-label="Close editor">×</button></div><input type="hidden" name="id" value="${item.id || ''}"><div class="form-field"><label for="entry-title">Title</label><input id="entry-title" name="title" maxlength="140" required value="${escapeHTML(item.title || '')}" placeholder="${journal ? 'What did you investigate?' : 'What does this script do?'}"></div>
    ${journal ? `<div class="form-field"><label for="entry-lesson">Related lesson</label><select id="entry-lesson" name="lesson_id"><option value="">General field notes</option>${state.lessons.map(l=>`<option value="${l.id}" ${item.lesson_id === l.id ? 'selected' : ''}>${escapeHTML(l.title)}</option>`).join('')}</select></div><div class="form-field"><label for="entry-body">Commands, observations, and next steps</label><textarea id="entry-body" name="body" maxlength="60000" required placeholder="Scope → Commands → Observations → Hypothesis → Next steps">${escapeHTML(item.body || '')}</textarea><div class="form-help">Record timestamps and evidence paths. Keep credentials out of notes.</div></div>` : `<div class="form-field"><label for="entry-description">Purpose, inputs, and assumptions</label><input id="entry-description" name="description" maxlength="4000" value="${escapeHTML(item.description || '')}" placeholder="Expected input, supported platform, and failure behavior"></div><div class="form-field"><label for="entry-tags">Tags, separated by commas</label><input id="entry-tags" name="tags" maxlength="300" value="${escapeHTML(item.tags || '')}" placeholder="logs, triage, portable"></div><div class="form-field"><label for="entry-code">Shell script or snippet</label><textarea class="script" id="entry-code" name="code" maxlength="60000" required spellcheck="false" placeholder="#!/bin/sh">${escapeHTML(item.code || '')}</textarea><div class="form-help">Saved as text. Download and review before running in your terminal.</div></div>`}
    <div id="form-error" class="form-error" role="alert"></div><div class="dialog-actions"><button type="button" class="button secondary" data-close-editor>Cancel</button><button type="submit" class="button">${journal ? 'Save field note' : 'Save script'}</button></div></form>`;
  node.showModal();
}

document.addEventListener('input', event => {
  if (event.target.matches('[data-search]')) { filters.search = event.target.value; updateSearchResults(); }
  const worksheet = event.target.closest('#threat-worksheet-form');
  if (worksheet) worksheetDraft = Object.fromEntries(new FormData(worksheet));
});

document.addEventListener('change', event => {
  const worksheet = event.target.closest('#threat-worksheet-form');
  if (worksheet) worksheetDraft = Object.fromEntries(new FormData(worksheet));
  const planner = event.target.closest('#coach-plan-form');
  if (planner) {
    const data = new FormData(planner);
    coachPrefs = {industry:data.get('industry'), platform:data.get('platform'), signals:data.getAll('signal')};
  }
});

document.addEventListener('submit', async event => {
  const formId = event.target.getAttribute('id');
  if (formId === 'coach-plan-form' || formId === 'threat-worksheet-form') {
    event.preventDefault();
    const form = event.target;
    const button = form.querySelector('[type="submit"]');
    button.disabled = true;
    const data = new FormData(form);
    try {
      if (formId === 'coach-plan-form') {
        coachPrefs = {industry: data.get('industry'), platform: data.get('platform'), signals: data.getAll('signal')};
        coachPlan = await api('/api/coach/plan', coachPrefs);
        document.getElementById('coach-plan-results').innerHTML = investigationResults();
        document.getElementById('coach-plan-error').textContent = '';
      } else {
        worksheetDraft = Object.fromEntries(data);
        const fields = [...worksheetFields.slice(1,9), ...['impact','likelihood','confidence'].flatMap(name=>[[name,name[0].toUpperCase()+name.slice(1)],[name+'_reason','Reason for '+name]]), ...worksheetFields.slice(9)];
        const body = fields.map(([name,label])=>`${label}:\n${worksheetDraft[name] || '(not recorded)'}`).join('\n\n');
        await api('/api/journal/save',{title:worksheetDraft.title,body,lesson_id:'investigation-evaluation'});
        worksheetDraft = {};
        await refreshState();
        location.hash = '#journal';
        toast('Threat assessment saved to your field journal.');
      }
    } catch(error) { document.getElementById(formId === 'coach-plan-form' ? 'coach-plan-error' : 'worksheet-error').textContent = error.message; }
    finally { if (button.isConnected) button.disabled = false; }
    return;
  }
  if (event.target.getAttribute('id') !== 'entry-form') return;
  event.preventDefault();
  const form = event.target;
  const button = form.querySelector('[type="submit"]');
  button.disabled = true;
  const body = Object.fromEntries(new FormData(form));
  if (body.id) body.id = Number(body.id); else delete body.id;
  try {
    await api(`/api/${form.dataset.kind}/save`, body);
    document.getElementById('editor').close();
    await refreshState();
    render();
    toast(form.dataset.kind === 'journal' ? 'Field note saved.' : 'Script saved to your toolbox.');
  } catch (error) { document.getElementById('form-error').textContent = error.message; }
  finally { button.disabled = false; }
});

document.addEventListener('click', async event => {
  if (event.target.closest('.skip-link')) {
    event.preventDefault();
    document.getElementById('main').focus();
    return;
  }
  const button = event.target.closest('button');
  if (!button) return;
  const d = button.dataset;
  try {
    if (d.copyTarget) {
      await navigator.clipboard.writeText(document.getElementById(d.copyTarget).textContent);
      toast('Copied. Review the command before running it.');
    } else if (d.track) { filters.track = d.track; render(); }
    else if (d.coachTab) { coachTab = d.coachTab; filters.search = ''; render(); }
    else if (d.guideNote) {
      const guide = state.coach.playbooks.find(g=>g.id===d.guideNote);
      worksheetDraft = {...worksheetDraft, title:worksheetDraft.title || `Investigation: ${guide.title}`, goal:worksheetDraft.goal || guide.attacker_goal};
      coachTab = 'worksheet';
      location.hash = '#coach';
    }
    else if (d.category) { filters.commands = d.category; render(); }
    else if (d.labFile) {
      button.disabled = true;
      await openLabFile(d.lesson, d.labFile);
    } else if (d.labStart) {
      button.disabled = true;
      activeLabs[d.labStart] = await api('/api/lab/start', {lesson_id: d.labStart});
      render(); toast('Practice lab ready. Open its directory in your terminal.');
    } else if (d.labCheck) {
      button.disabled = true;
      const result = await api('/api/lab/check', {lesson_id: d.labCheck});
      labResults[d.labCheck] = result;
      await refreshState(); delete activeLabs[d.labCheck]; render();
      toast(result.passed ? 'Artifacts verified. A record was added to your journal on first completion.' : 'Feedback ready. Adjust your artifacts and try again.');
    } else if (d.new) openEditor(d.new);
    else if ('closeEditor' in d) document.getElementById('editor').close();
    else if (d.editKind) {
      const items = d.editKind === 'journal' ? state.journal : state.snippets;
      openEditor(d.editKind, items.find(item=>item.id === Number(d.id)));
    } else if (d.deleteKind) {
      if (!confirm('Delete this saved entry? Export first if you want to keep a copy.')) return;
      await api(`/api/${d.deleteKind}/delete`, {id: Number(d.id)});
      await refreshState(); render(); toast('Entry deleted.');
    } else if (d.reflect) {
      const lesson = state.lessons.find(item=>item.id === d.reflect);
      openEditor('journal', {title: `Field notes: ${lesson.title}`, lesson_id: lesson.id, body: `Question: ${lesson.reflection}\n\nScope:\n\nCommands used:\n\nObservations (with evidence paths):\n\nHypothesis and confidence:\n\nLimitations:\n\nNext steps:\n`});
    } else if (d.saveRecipe) {
      const lesson = state.lessons.find(item=>item.id === d.saveRecipe);
      openEditor('snippets', {title: lesson.title, description: `${lesson.goal} Uses the generated Script Junky fixture format.`, tags: `${lesson.id},lab`, code: lesson.recipe});
    } else if (d.download) {
      const item = state.snippets.find(item=>item.id === Number(d.download));
      const url = URL.createObjectURL(new Blob([item.code+'\n'], {type:'text/plain;charset=utf-8'}));
      const anchor = document.createElement('a'); anchor.href = url; anchor.download = `scriptjunky-${item.id}.sh`; anchor.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
      toast('Script downloaded. Review its inputs and scope before executing.');
    } else if ('answer' in d && !practice.feedback && !practice.busy) {
      practice.busy = true; render();
      const card = practice.cards[practice.index];
      const answer = card.choices[Number(d.answer)];
      try {
        const result = await api('/api/review', {card_id: card.id, answer});
        practice.feedback = {...result, selected: answer};
        if (result.correct) practice.correct++;
        await refreshState();
      } finally { practice.busy = false; render(); }
    } else if ('nextCard' in d) { practice.index++; practice.feedback = null; render(); }
  } catch (error) { toast(error.message); }
  finally { if (button.isConnected) button.disabled = false; }
});

async function onRoute() {
  filters.search = '';
  if (location.hash === '#practice' && practice.index >= practice.cards.length && !practice.loading) {
    practice = {cards: [], index: 0, correct: 0, feedback: null, loading: true, busy: false};
    render();
    try { await refreshState(); practice.cards = await api('/api/cards'); }
    catch(error) { toast(error.message); }
    finally { practice.loading = false; }
  }
  render();
  window.scrollTo({top:0,behavior:'instant'});
}
window.addEventListener('hashchange', onRoute);
async function boot() {
  try { await refreshState(); await onRoute(); }
  catch(error) { document.getElementById('main').innerHTML = emptyState('The workspace could not open.', 'Keep the Python server running, then reload this page. ' + error.message); }
}
boot();
