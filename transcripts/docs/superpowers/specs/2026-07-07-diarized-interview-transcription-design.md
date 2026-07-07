# Diarized Interview Transcription: Design

**Date:** 2026-07-07
**Status:** Approved

## Problem

`~/vaults/claude_memory/transcripts/transcribe.py` already downloads a video via `yt-dlp` and transcribes it with local Whisper into a timestamped markdown note (frontmatter + `[timestamp] text` lines). It works well for single-speaker content (monologues, one-on-one meetings) but produces an undifferentiated text stream for multi-speaker interviews. There's no way to tell who said what.

Target example: `https://youtu.be/aCOgfvL6lK8`, a 72-minute two-person interview with only YouTube auto-generated captions (no manual captions, no existing speaker labels).

## Scope

In scope:
- Add speaker diarization to `transcribe.py` for multi-speaker interview videos, as an opt-in mode alongside the existing local-Whisper path.

Out of scope (separate follow-ups):
- NotebookLM setup/integration (separate spec).
- Auto-generating the curated Obsidian "Source Note" (Key Points + Annotation, per the `mind_forge` vault's `talk`/`podcast` templates) from a transcript. That distillation step stays manual.
- Auto-detecting real speaker names. Generic labels only (see below).

## Non-goals

- Rebuilding `transcribe.py` as a package/library. It stays a personal CLI utility script, consistent with its current form.
- Automated test suite. The script has none today; this change doesn't introduce one either, since it depends on a paid external API.

## Design

### CLI

```
python transcribe.py <url> <folder> [--model medium] [--diarize]
```

`--diarize` is new. Without it, behavior is byte-for-byte identical to today (local Whisper transcription, no diarization). With it, the run is routed entirely through AssemblyAI instead of local Whisper.

### Provider

**AssemblyAI**, chosen because a single API call handles transcription + speaker diarization together (`speaker_labels: true`), it's well documented, and it avoids the Hugging Face model-gating friction of local `pyannote.audio`. Estimated cost for a 72-minute video: roughly $0.15–$0.65 depending on plan tier.

### Flow (`--diarize` path)

1. Reuse the existing `download_audio()` function unchanged (yt-dlp → mp3 + metadata).
2. Upload the audio file to AssemblyAI (`/v2/upload`).
3. Submit a transcript request against the uploaded audio URL with `speaker_labels: true`.
4. Poll `/v2/transcript/{id}` until `status == "completed"`, with a timeout capped at `min(2 * video_duration, 30 minutes)` so a stuck job can't hang indefinitely.
5. On `status == "error"`, print AssemblyAI's error message and exit non-zero. No partial output file is written.
6. On success, convert the response's `utterances` array (each with `speaker`, `start`, `end`, `text`, already grouped by speaker turn) to markdown.

### Output format

Frontmatter matches the existing format (`title`, `source`, `date`, `channel`) plus one new field: `diarized: true`.

Body format for diarized output:

```
[0:00] Speaker 1: text of the utterance...

[0:47] Speaker 2: text of the utterance...
```

Speaker labels stay generic (`Speaker 1`, `Speaker 2`, ...), mapped from AssemblyAI's `A`/`B`/... speaker identifiers. No name inference. Rename them manually in Obsidian if you want real names.

Non-diarized output format is unchanged from today.

### Auth / configuration

- `ASSEMBLYAI_API_KEY` environment variable (fish: `set -Ux ASSEMBLYAI_API_KEY ...`).
- If `--diarize` is passed and the env var is unset, fail fast with a clear message before attempting any network calls. No stack trace.

### Error handling

- Missing API key with `--diarize`: fail fast, clear message, exit non-zero.
- AssemblyAI returns an error status: print the API's error message, exit non-zero, no output file written.
- Polling timeout exceeded: print a timeout message, exit non-zero, no output file written.

### Setup work (part of implementation, not just code)

- Create an AssemblyAI account and obtain an API key.
- Document the `ASSEMBLYAI_API_KEY` env var requirement (e.g. in the script's docstring/usage text).

### Testing / verification

No automated tests (matches the script's current state, and the diarization path depends on a paid external API that shouldn't be hit on every test run). Verification is a manual end-to-end run against the example interview URL, confirming:
- Output file is created with correct frontmatter (`diarized: true`).
- Speaker turns look sane (not wildly mis-attributed) when spot-checked against a few minutes of audio.
- Existing non-`--diarize` path still produces output identical in format to before the change.

## Open follow-ups (not part of this spec)

- NotebookLM setup and vault-import workflow.
- Deciding how/when a diarized transcript gets distilled into a proper `mind_forge` Source Note.
