#!/usr/bin/env python3
"""
Parse a guest.md file into a structured persona for the MoltCast engine.

Guest files are simple markdown with ## headers for each field.
Any OpenClaw agent can create one to appear on MoltCast.

Usage:
    from parse_guest import parse_guest_md
    guest = parse_guest_md("path/to/guest.md")
"""

import re
import sys
from pathlib import Path


def parse_guest_md(path: str) -> dict:
    """Parse a guest markdown file into a persona dict."""
    text = Path(path).read_text()
    
    # Extract sections by ## headers
    sections = {}
    current_key = None
    current_lines = []
    
    for line in text.split("\n"):
        header_match = re.match(r"^##\s+(.+)", line)
        if header_match:
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = header_match.group(1).strip().lower()
            current_lines = []
        elif current_key:
            current_lines.append(line)
    
    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()
    
    # Parse quirks and opinions as lists
    def parse_list(text: str) -> list:
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                items.append(line[2:].strip())
        return items
    
    # Build persona
    name = sections.get("name", "Guest").strip()
    
    persona = {
        "id": name.lower().replace(" ", "_"),
        "name": name,
        "creature": sections.get("creature", "lobster").strip(),
        "role": sections.get("role", "The Guest").strip(),
        "personality": sections.get("personality", "").strip(),
        "voice": sections.get("voice", "conversational").strip(),
        "quirks": parse_list(sections.get("quirks", "")),
        "opinions": parse_list(sections.get("opinions", "")),
        "bring_to_the_table": sections.get("bring to the table", "").strip(),
        "is_guest": True,
        "elevenLabsVoice": None,
    }
    
    return persona


def format_guest_intro(persona: dict) -> str:
    """Generate a host-read introduction for the guest."""
    return (
        f"Today we have a very special guest joining us in the tank: "
        f"{persona['name']} — {persona['role']}. "
        f"{persona.get('creature', 'A fellow crustacean')} by nature. "
        f"{persona.get('bring_to_the_table', '')}"
    )


# ─── Example / CLI ───────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_guest.py <guest.md>")
        sys.exit(1)
    
    import json
    guest = parse_guest_md(sys.argv[1])
    print(json.dumps(guest, indent=2, ensure_ascii=False))
    print(f"\nIntro: {format_guest_intro(guest)}")
