# Diarized Interview Transcription Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in `--diarize` flag to `transcribe.py` that produces a speaker-labeled transcript via AssemblyAI for multi-speaker interview videos, while leaving the existing local-Whisper path unchanged.

**Architecture:** One function per AssemblyAI REST call (upload, submit, poll), one pure function to convert AssemblyAI's `utterances` into the existing markdown body style, and a small `main()` branch that routes to either the existing Whisper path or the new AssemblyAI path based on the flag.

**Tech Stack:** Python 3.13 (pyenv), `requests` (already installed, no new dependency), AssemblyAI REST API v2 (`/v2/upload`, `/v2/transcript`), existing `yt-dlp` + `openai-whisper` stack.

## Global Constraints

- Target file: `/Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py`. This directory is **not** a git repository, so this plan has no `git commit` steps. Instead, back up the file before the first change and remove the backup only after the final end-to-end verification (Task 6) passes.
- Non-diarize behavior (no `--diarize` flag) must produce byte-for-byte identical output to today's script. Every task that touches shared code (`build_markdown`, `main`) must verify this explicitly.
- No automated test suite. This matches the script's current state and the spec's decision (diarization depends on a paid external API that shouldn't be hit on every test run). Verification steps use direct `python3 -c` invocations instead of pytest.
- No new pip dependency: use `requests` (already present in the pyenv environment used to run this script) for all AssemblyAI HTTP calls.
- Speaker labels are generic (`Speaker 1`, `Speaker 2`, ...), assigned in order of first appearance. No name inference.

---

### Task 1: Backup, CLI flag, and fail-fast API key check

**Files:**
- Modify: `/Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py`

**Interfaces:**
- Produces: `args.diarize` (bool, from argparse) and an `api_key` variable available in `main()` before any download/network work happens, for later tasks to consume.

- [ ] **Step 1: Back up the file**

Run:
```bash
cp /Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py /Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py.bak-pre-diarize
```
Expected: new file `transcribe.py.bak-pre-diarize` exists alongside the original.

- [ ] **Step 2: Add the `--diarize` argparse flag**

In `main()`, change:
```python
    parser = argparse.ArgumentParser(description="Transcribe a video URL to markdown")
    parser.add_argument("url", help="YouTube or Rumble URL")
    parser.add_argument("folder", help="Output subfolder name")
    parser.add_argument("--model", default="medium", help="Whisper model size")
    args = parser.parse_args()
```
to:
```python
    parser = argparse.ArgumentParser(description="Transcribe a video URL to markdown")
    parser.add_argument("url", help="YouTube or Rumble URL")
    parser.add_argument("folder", help="Output subfolder name")
    parser.add_argument("--model", default="medium", help="Whisper model size")
    parser.add_argument(
        "--diarize",
        action="store_true",
        help="Use AssemblyAI for speaker-diarized transcription instead of local Whisper (requires ASSEMBLYAI_API_KEY)",
    )
    args = parser.parse_args()

    api_key = None
    if args.diarize:
        api_key = os.environ.get("ASSEMBLYAI_API_KEY")
        if not api_key:
            print(
                "Error: --diarize requires the ASSEMBLYAI_API_KEY environment variable.\n"
                "Get a key at https://www.assemblyai.com/ and set it, e.g.:\n"
                "  fish:      set -Ux ASSEMBLYAI_API_KEY your-key-here\n"
                "  bash/zsh:  export ASSEMBLYAI_API_KEY=your-key-here",
                file=sys.stderr,
            )
            sys.exit(1)
```

- [ ] **Step 3: Verify `--help` shows the new flag**

Run: `python3 /Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py --help`
Expected: output includes a `--diarize` line with the help text above.

- [ ] **Step 4: Verify fail-fast behavior with no API key set and no network activity**

Run:
```bash
env -u ASSEMBLYAI_API_KEY python3 /Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py "https://example.com/video" testfolder --diarize
```
Expected: prints the `Error: --diarize requires...` message to stderr, exits with status 1, and never prints `Downloading audio from...` (confirming the check happens before `download_audio()` runs). Check the exit code with `echo $status` (fish) immediately after; expect `1`.

---

### Task 2: Utterance-to-markdown conversion (pure function)

**Files:**
- Modify: `/Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py`

**Interfaces:**
- Consumes: `format_timestamp(seconds: float) -> str` (existing function, unchanged).
- Produces: `utterances_to_markdown(utterances: list[dict]) -> str`, where each utterance dict has keys `speaker` (str, e.g. `"A"`), `start` (int, milliseconds), `end` (int, milliseconds), `text` (str). Later tasks (Task 5) call this with AssemblyAI's raw `utterances` response.

- [ ] **Step 1: Add the function**

Add below `segments_to_markdown()`:
```python
def utterances_to_markdown(utterances: list[dict]) -> str:
    """Convert AssemblyAI diarized utterances to timestamped, speaker-labeled markdown text."""
    speaker_labels: dict[str, str] = {}
    lines = []
    for utt in utterances:
        code = utt["speaker"]
        if code not in speaker_labels:
            speaker_labels[code] = f"Speaker {len(speaker_labels) + 1}"
        label = speaker_labels[code]
        ts = format_timestamp(utt["start"] / 1000)
        text = utt["text"].strip()
        lines.append(f"[{ts}] {label}: {text}")
    return "\n\n".join(lines)
```

- [ ] **Step 2: Verify with a hand-built utterance list**

Run:
```bash
python3 -c "
import sys
sys.path.insert(0, '/Users/spencerduran/vaults/claude_memory/transcripts')
from transcribe import utterances_to_markdown

utterances = [
    {'speaker': 'A', 'start': 0, 'end': 2000, 'text': 'Hi there.'},
    {'speaker': 'B', 'start': 2000, 'end': 4500, 'text': 'Hey, thanks for having me.'},
    {'speaker': 'A', 'start': 4500, 'end': 6000, 'text': 'Of course.'},
]
print(utterances_to_markdown(utterances))
"
```
Expected output (exact):
```
[0:00] Speaker 1: Hi there.

[0:02] Speaker 2: Hey, thanks for having me.

[0:04] Speaker 1: Of course.
```
Confirm speaker `A` maps to `Speaker 1` both times it appears (label reuse, not a fresh number each turn).

---

### Task 3: AssemblyAI upload, submit, and poll functions

**Files:**
- Modify: `/Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py`

**Interfaces:**
- Consumes: `requests` (add `import requests` and `import time` to the top imports, alongside the existing `import` block).
- Produces: `diarize_with_assemblyai(audio_path: str, api_key: str, video_duration: float) -> list[dict]`, returning the `utterances` list consumed by Task 2's `utterances_to_markdown()`. Raises `AssemblyAIError` or `TranscriptionTimeoutError` (both defined here) on failure, caught by `main()` in Task 5.

- [ ] **Step 1: Add imports**

At the top of the file, change:
```python
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
```
to:
```python
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests
```

- [ ] **Step 2: Add exception classes and the three functions**

Add below the imports (or just above `download_audio`, matching existing top-to-bottom flow order):
```python
class AssemblyAIError(Exception):
    """Raised when AssemblyAI returns a transcription error."""


class TranscriptionTimeoutError(Exception):
    """Raised when polling AssemblyAI exceeds the allowed timeout."""


def upload_audio_to_assemblyai(audio_path: str, api_key: str) -> str:
    """Upload a local audio file to AssemblyAI, return its hosted upload_url."""
    headers = {"authorization": api_key}
    with open(audio_path, "rb") as f:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=f,
        )
    response.raise_for_status()
    return response.json()["upload_url"]


def submit_transcript_request(upload_url: str, api_key: str) -> str:
    """Submit a diarized transcription request, return the transcript id."""
    headers = {"authorization": api_key, "content-type": "application/json"}
    response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers=headers,
        json={"audio_url": upload_url, "speaker_labels": True},
    )
    response.raise_for_status()
    return response.json()["id"]


def poll_transcript(transcript_id: str, api_key: str, timeout_seconds: float) -> dict:
    """Poll AssemblyAI until the transcript completes, errors, or times out."""
    headers = {"authorization": api_key}
    url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    poll_interval = 3
    elapsed = 0.0
    while elapsed < timeout_seconds:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        status = data["status"]
        if status == "completed":
            return data
        if status == "error":
            raise AssemblyAIError(data.get("error", "Unknown AssemblyAI error"))
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise TranscriptionTimeoutError(
        f"AssemblyAI transcription did not complete within {timeout_seconds:.0f} seconds"
    )


def diarize_with_assemblyai(audio_path: str, api_key: str, video_duration: float) -> list[dict]:
    """Upload, submit, and poll AssemblyAI for a diarized transcript; return its utterances."""
    upload_url = upload_audio_to_assemblyai(audio_path, api_key)
    transcript_id = submit_transcript_request(upload_url, api_key)
    timeout_seconds = min(2 * video_duration, 30 * 60) if video_duration else 30 * 60
    data = poll_transcript(transcript_id, api_key, timeout_seconds)
    return data["utterances"]
```

- [ ] **Step 3: Verify the file still imports cleanly**

Run:
```bash
python3 -c "
import sys
sys.path.insert(0, '/Users/spencerduran/vaults/claude_memory/transcripts')
import transcribe
print(transcribe.diarize_with_assemblyai, transcribe.AssemblyAIError, transcribe.TranscriptionTimeoutError)
"
```
Expected: no `ImportError`/`SyntaxError`; prints the three function/class references.

Full network verification of these three functions happens in Task 6's end-to-end run. They require a real AssemblyAI account and cost a small amount per call, so they aren't exercised standalone here.

---

### Task 4: Extend `build_markdown()` with the `diarized` flag

**Files:**
- Modify: `/Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py`

**Interfaces:**
- Produces: `build_markdown(meta: dict, transcript_text: str, url: str, diarized: bool = False) -> str`. Default `diarized=False` must produce output identical to the current (pre-change) function. Task 5's non-diarize path relies on this.

- [ ] **Step 1: Update the function**

Change:
```python
def build_markdown(meta: dict, transcript_text: str, url: str) -> str:
    title = meta.get("title", "Untitled")
    channel = meta.get("channel", meta.get("uploader", "Unknown"))
    upload_date = meta.get("upload_date", "")
    if upload_date:
        date_str = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""---
title: "{title}"
source: "{url}"
date: {date_str}
channel: "{channel}"
---

# {title}

{transcript_text}
"""
```
to:
```python
def build_markdown(meta: dict, transcript_text: str, url: str, diarized: bool = False) -> str:
    title = meta.get("title", "Untitled")
    channel = meta.get("channel", meta.get("uploader", "Unknown"))
    upload_date = meta.get("upload_date", "")
    if upload_date:
        date_str = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    diarized_line = "\ndiarized: true" if diarized else ""

    return f"""---
title: "{title}"
source: "{url}"
date: {date_str}
channel: "{channel}"{diarized_line}
---

# {title}

{transcript_text}
"""
```

- [ ] **Step 2: Verify identical output when `diarized=False`**

Run:
```bash
python3 -c "
import sys
sys.path.insert(0, '/Users/spencerduran/vaults/claude_memory/transcripts')
from transcribe import build_markdown

meta = {'title': 'Test Video', 'channel': 'Test Channel', 'upload_date': '20260101'}
print(repr(build_markdown(meta, 'body text', 'https://example.com')))
"
```
Expected: the returned string's frontmatter has exactly four lines (`title`, `source`, `date`, `channel`) between the `---` markers, with no `diarized` line, matching today's format exactly.

- [ ] **Step 3: Verify the `diarized: true` line appears when requested**

Run:
```bash
python3 -c "
import sys
sys.path.insert(0, '/Users/spencerduran/vaults/claude_memory/transcripts')
from transcribe import build_markdown

meta = {'title': 'Test Video', 'channel': 'Test Channel', 'upload_date': '20260101'}
print(build_markdown(meta, 'body text', 'https://example.com', diarized=True))
"
```
Expected: frontmatter includes `diarized: true` as the last line before the closing `---`.

---

### Task 5: Wire the diarize path into `main()`

**Files:**
- Modify: `/Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py`

**Interfaces:**
- Consumes: `args.diarize` and `api_key` (Task 1), `diarize_with_assemblyai()` and its exceptions (Task 3), `utterances_to_markdown()` (Task 2), `build_markdown(..., diarized=...)` (Task 4).

- [ ] **Step 1: Branch on `args.diarize` inside `main()`**

Change:
```python
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Downloading audio from {args.url}...")
        audio_path, meta = download_audio(args.url, tmpdir)

        print(f"Transcribing with whisper ({args.model})...")
        segments = transcribe(audio_path, model=args.model)

    transcript_text = segments_to_markdown(segments)
    markdown = build_markdown(meta, transcript_text, args.url)
```
to:
```python
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Downloading audio from {args.url}...")
        audio_path, meta = download_audio(args.url, tmpdir)

        if args.diarize:
            print("Transcribing with AssemblyAI (diarized)...")
            try:
                utterances = diarize_with_assemblyai(
                    audio_path, api_key, meta.get("duration") or 0
                )
            except (AssemblyAIError, TranscriptionTimeoutError) as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            transcript_text = utterances_to_markdown(utterances)
        else:
            print(f"Transcribing with whisper ({args.model})...")
            segments = transcribe(audio_path, model=args.model)
            transcript_text = segments_to_markdown(segments)

    markdown = build_markdown(meta, transcript_text, args.url, diarized=args.diarize)
```

- [ ] **Step 2: Verify the non-diarize path still works end-to-end**

Run against a short public video (e.g. a video under a minute) to keep this fast:
```bash
python3 /Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py "https://www.youtube.com/watch?v=jNQXAC9IVRw" _plan-verify-task5
```
Expected: script runs to completion exactly as before this plan started (downloads, transcribes with Whisper, prints `Saved: ...`), and the saved file's frontmatter has no `diarized` line. Delete the test output afterward: `rm -rf /Users/spencerduran/vaults/claude_memory/transcripts/_plan-verify-task5`.

---

### Task 6: AssemblyAI account setup and end-to-end diarized verification

**Files:**
- None (manual setup + one real run of the already-modified `transcribe.py`).

**Interfaces:**
- None. This is the spec's required manual verification pass.

- [ ] **Step 1: Create an AssemblyAI account and get an API key**

Sign up at https://www.assemblyai.com/, retrieve the API key from the dashboard.

- [ ] **Step 2: Set the environment variable**

```fish
set -Ux ASSEMBLYAI_API_KEY your-key-here
```

- [ ] **Step 3: Run the full diarized pipeline against the target interview**

```bash
python3 /Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py "https://youtu.be/aCOgfvL6lK8" Interviews --diarize
```
Expected: script downloads audio, uploads to AssemblyAI, polls to completion (may take a few minutes for a 72-minute video), and saves a markdown file under `/Users/spencerduran/vaults/claude_memory/transcripts/Interviews/`.

- [ ] **Step 4: Inspect the output**

Open the saved file and confirm:
- Frontmatter includes `diarized: true`.
- Body lines follow the `[timestamp] Speaker N: text` format.
- Spot-check 3-4 utterances against a few minutes of the actual video (skip to that timestamp on YouTube) to confirm speaker turns are attributed sanely, not wildly mixed up.
- Both `Speaker 1` and `Speaker 2` appear (confirming diarization actually split the two speakers, not collapsed them into one).

- [ ] **Step 5: Remove the backup now that the change is verified**

```bash
rm /Users/spencerduran/vaults/claude_memory/transcripts/transcribe.py.bak-pre-diarize
```
