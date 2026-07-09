# NotebookLM Integration for mind_forge: Design

**Date:** 2026-07-09
**Status:** Approved

## Problem

Diarized interview transcripts (from the just-built `transcribe.py --diarize`) and Zoom meeting transcripts already exist as raw files in `~/vaults/claude_memory/transcripts/`. There's no way to interrogate them with grounded Q&A, and no path from "raw transcript" to a proper, filed note in `mind_forge`, the vault that holds curated knowledge.

An existing Claude Code skill, `notebooklm` (at `~/.claude/plugins/marketplaces/personal-os-skills/skills/notebooklm/`), wraps the third-party `notebooklm-py` CLI to create NotebookLM notebooks, add sources, ask questions, and import the results into an Obsidian vault as linked files with resolved citations. It is not installed or authenticated yet. Its own folder/frontmatter conventions (`Notes/NotebookLM/{slug}/Sources/`, `Notes/NotebookLM/{slug}/QA/`, `Notes/Dashboards/`) do not match `mind_forge`'s actual structure (flat `01 - Notes/`, category/subject frontmatter navigated via `02 - Categories/` Bases queries).

## Scope

In scope:
- Set up `notebooklm-py` and authenticate.
- Route the skill's existing `import`/`ask` workflows into `mind_forge/00 - Inbox/` (its designated transit zone) without modifying the skill's own scripts.
- Write a `[[Protocols]]` runbook note documenting how to promote a specific Inbox NotebookLM file into a properly filed `01 - Notes/` note, matching mind_forge's category/type/subjects conventions.
- Support any local transcript file as a source, not just YouTube interviews. This covers Zoom meeting transcripts from `claude_memory/transcripts/Meetings/` with no extra work, since the mechanism is file-type-agnostic.

Out of scope:
- Automatic triggering from `transcribe.py`. This is a manual, per-video/per-meeting decision.
- A NotebookLM-specific dashboard. Redundant: the `Source Notes`, `Meeting Notes`, and `Reference` category pages already auto-surface anything linking to them via `file.hasLink(this.file)`.
- Forking or patching the `notebooklm-py` package or the `notebooklm` skill's scripts.
- Automatically mapping NotebookLM's AI-extracted topics onto mind_forge's fixed 16-item `subjects:` taxonomy. They're different vocabularies and shouldn't be conflated.

## Non-goals

- A fully automated promotion script. Deciding which category a source belongs to (`Source Notes` vs. `Meeting Notes`) and which parts of an AI-generated guide go where requires judgment; promotion is a Claude Code-assisted manual step guided by the runbook, not a deterministic script.
- Building a general-purpose importer for source types beyond what the existing skill already supports (PDFs, web pages, Google Docs, etc.). Transcript files are the only target here.

## Design

### Architecture

The `notebooklm` skill's `import.md` and `ask.md` workflows already write relative to `Path.cwd()` (their scripts treat cwd as "vault root"). Running them with the working directory set to `mind_forge/00 - Inbox/` instead of the vault root means their output (`Notes/NotebookLM/{slug}/Sources/*.md`, `Notes/NotebookLM/{slug}/QA/*.md`) lands inside Inbox, mind_forge's own designated "process new files here, then move them to `01 - Notes/`" zone. No script in the third-party skill changes; only the working directory used when invoking them differs from the skill's own documentation. This means the skill survives future updates untouched.

Concretely, invocation shifts from (per the skill's own docs, run from vault root):
```bash
python3 .claude/skills/notebooklm/scripts/import_sources.py --sources ... --slug ...
```
to (run with cwd set to Inbox, using an absolute path to the script since the relative `.claude/skills/...` path assumes vault-root cwd):
```bash
cd "/Users/spencerduran/vaults/mind_forge/00 - Inbox"
python3 "/Users/spencerduran/vaults/mind_forge/.claude/skills/notebooklm/scripts/import_sources.py" --sources ... --slug ...
```
The exact commands (including whether `import_sources.py`'s `--dashboard` argument can be omitted, given dashboards are out of scope) get finalized during implementation planning, not in this spec.

### Promotion runbook

A new note, `01 - Notes/Promote a NotebookLM Note.md`, with `category: [[Protocols]]`, `type: runbook`. It documents:
1. Read the Inbox source/QA file you want to keep.
2. Decide category based on content type:
   - Interview → `category: [[Source Notes]]`, `type: video` (or `podcast`), reshaped into the existing `talk.md`/`podcast.md` template structure (quote callout, Key Points, Annotation) using the NotebookLM guide's summary and topics as raw material.
   - Meeting transcript → `category: [[Meeting Notes]]`, reshaped into the `meeting.md` template structure (Context/Discussion/Decisions/Action Items).
   - Q&A note (either source type) → `category: [[Reference]]`, `type: audit` ("point-in-time analysis or investigation output," matching mind_forge's own definition).
3. Leave `subjects: []` for manual fill (controlled taxonomy); keep NotebookLM's AI-extracted topics as a plain bullet list in the note body instead of forcing them into `subjects:`.
4. Set `created:` to today's date in the `YYYY-MM-DD` format the Source Notes/Meeting Notes templates use.
5. Move the rewritten file from Inbox into flat `01 - Notes/`.
6. Delete (or leave, at the user's discretion) the original Inbox copy.

### Setup

- `pip install "notebooklm-py[browser]"`
- `playwright install chromium`
- `notebooklm login` (opens a real browser window for Google auth; session cookies saved to `~/.notebooklm/storage_state.json`)
- Dataview plugin: already confirmed installed in `mind_forge`. No action needed.

### Error handling

- If `notebooklm status` reports an auth error at the start of a session, the runbook/workflow directs to re-run `notebooklm login` before proceeding. This is the skill's own existing behavior, unchanged.
- If a transcript file fails to add as a source (unsupported format, upload failure), that surfaces as a `notebooklm-py` CLI error; no new handling is introduced beyond what the skill already provides.

### Testing / verification

No automated tests. This is a CLI/workflow setup, not application code. Verification is a manual end-to-end run once setup is complete:
1. Add the already-generated diarized interview transcript (`claude_memory/transcripts/Interviews/2026-06-22_the-genius-who-outsmarted-the-prop-firm-game-and-made-15m-in.md`) as a source in a new notebook.
2. Ask it one question.
3. Confirm the import lands in `mind_forge/00 - Inbox/Notes/NotebookLM/{slug}/` with resolved `[[wikilinks]]` citations.
4. Promote the source file using the new runbook; confirm it ends up in `01 - Notes/` with correct category/type frontmatter and shows up on the `Source Notes` category page.

## Open follow-ups (not part of this spec)

- Whether to also promote Zoom meeting transcripts through this same pipeline in practice (the mechanism supports it; actually doing it is a future per-meeting decision, not part of this build).
