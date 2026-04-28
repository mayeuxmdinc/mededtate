#!/usr/bin/env python3
"""
Generate the /now voice-guide MP3s from voice-scripts.txt via ElevenLabs.

Usage:
  python3 generate_audio.py                  # default voice (Rachel)
  python3 generate_audio.py --voice Bella    # try a different voice
  python3 generate_audio.py --dry-run        # parse + print, don't call API

Reads the API key from ~/.elevenlabs_key. Writes one MP3 per script entry
into the same directory as this script. Skips files that already exist
unless --overwrite is passed.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.elevenlabs.io/v1"

# Voice catalog. "Grace" is from the ElevenLabs Voice Library
# (Starter tier required); the rest are free-tier premade voices,
# kept for fallback if we ever lose Library access.
VOICES = {
    "Grace":   "mZTVERjx1WQkdAWt1Lcm", # Library: warm velvety meditation voice — DEFAULT
    "Jessica": "cgSgspJ2msm6clMCkdW9", # American, Warm, Bright
    "Sarah":   "EXAVITQu4vr4xnSDxMaL", # Mature, Reassuring, Confident
    "Bella":   "hpp4J3VqNfWAUOO0d1Us", # Professional, Bright, Warm
    "Laura":   "FGY2WhTYpPnrIDTdsKH5", # Enthusiast, Quirky Attitude
    "Lily":    "pFZP5JQG7iQjIQuC4Bku", # Velvety Actress (British)
    "Matilda": "XrExE9yKIg1WjnnlVkGX", # Knowledgable, Professional
    "Alice":   "Xb7hH8MSUJpSbSDYk0k2", # Clear, Engaging Educator
    "River":   "SAz9YHcvj6GT2YYXdXww", # Relaxed, Neutral, Informative
    "Brian":   "nPczCjzI2devNBz1zQrb", # Deep, Resonant and Comforting
    "Jason":   "lNJnJjn1OFKWTmtR1fcn", # Library: cinematic documentary narrator
    "Joel":    "45nhFQt9BtnpUzG1E1Cj", # Library: calm conversational thoughtful
}

# Meditation-tuned settings:
#   stability=0.97 — flattens delivery toward monotone (calm)
#   similarity_boost=0.40 — strips performative inflection
#   style=0.0 — no enhancement, calmest baseline
#   speed=0.90 — 10% slower than default cadence
VOICE_SETTINGS = {
    "stability": 0.97,
    "similarity_boost": 0.40,
    "style": 0.0,
    "use_speaker_boost": True,
    "speed": 0.90,
}

# eleven_multilingual_v2 is the current production model.
MODEL_ID = "eleven_multilingual_v2"


def parse_scripts(script_path: Path) -> list[tuple[str, str]]:
    """Extract (filename, text) pairs from voice-scripts.txt."""
    text = script_path.read_text(encoding="utf-8")
    pairs: list[tuple[str, str]] = []
    # The file uses repeating blocks of "Filename: X\nText: Y". Match them
    # with non-greedy text capture, stopping at the next blank line or
    # next "Filename:" marker.
    for m in re.finditer(
        r"Filename:\s*(\S+)\s*\nText:\s*(.+?)(?=\n\s*\n|\nFilename:|$)",
        text,
        flags=re.DOTALL,
    ):
        filename = m.group(1).strip()
        body = m.group(2).strip()
        pairs.append((filename, body))
    return pairs


def synth_one(api_key: str, voice_id: str, text: str, out_path: Path) -> None:
    """Call ElevenLabs TTS and write an MP3 to out_path."""
    url = f"{API_BASE}/text-to-speech/{voice_id}/stream?output_format=mp3_44100_128"
    body = json.dumps(
        {
            "text": text,
            "model_id": MODEL_ID,
            "voice_settings": VOICE_SETTINGS,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            audio = resp.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"  HTTP {e.code} from ElevenLabs for '{out_path.name}': {e.read().decode('utf-8', errors='replace')}")
    out_path.write_bytes(audio)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--voice", default="Grace", choices=list(VOICES.keys()))
    p.add_argument("--dry-run", action="store_true", help="Parse + print, don't call API")
    p.add_argument("--overwrite", action="store_true", help="Re-generate even if file exists")
    args = p.parse_args()

    here = Path(__file__).parent
    script_path = here / "voice-scripts.txt"
    if not script_path.exists():
        print(f"voice-scripts.txt not found at {script_path}", file=sys.stderr)
        return 1

    pairs = parse_scripts(script_path)
    if not pairs:
        print("No filename/text pairs parsed — check the script format.", file=sys.stderr)
        return 1

    print(f"Parsed {len(pairs)} clips. Voice: {args.voice}.")

    if args.dry_run:
        for fname, body in pairs:
            print(f"  {fname:<28} → {body!r}")
        return 0

    key_path = Path.home() / ".elevenlabs_key"
    if not key_path.exists():
        print(f"Missing API key file at {key_path}. Create it with the key alone (no prefix).", file=sys.stderr)
        return 1
    api_key = key_path.read_text().strip()
    voice_id = VOICES[args.voice]

    skipped = generated = 0
    for fname, body in pairs:
        out_path = here / fname
        if out_path.exists() and not args.overwrite:
            print(f"  skip (exists): {fname}")
            skipped += 1
            continue
        print(f"  generating:   {fname}  ←  {body!r}")
        synth_one(api_key, voice_id, body, out_path)
        generated += 1

    print(f"Done. {generated} generated, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
