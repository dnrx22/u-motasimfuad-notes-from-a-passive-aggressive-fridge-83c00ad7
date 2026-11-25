#!/usr/bin/env python3
"""Notes From a Passive-Aggressive Fridge.

Writes the fridge's single door-screen note to entry.txt.

The note is exactly one line: the fridge has been keeping score of the
owner's 2 a.m. raids, and it would like the record to show that it
noticed. Dry, petty, and specific -- the appliance equivalent of
leaving a Post-it on its own door.

Deterministic: no input, no network, no clock, no randomness. The same
bytes come out on every run, so two runs hash identically.
"""

import hashlib
import os
import sys

# The note. One line, plain ASCII, no leading or trailing whitespace.
LINE = "You opened me at 2 a.m., stared into the light, and ate nothing. I am a fridge, not a therapist."

MAX_CHARS = 160
OUTPUT_NAME = "entry.txt"


def validate(line):
    """Enforce every rule the bounty places on the note.

    Returns a list of problems; an empty list means the line is valid.
    """
    problems = []
    if not isinstance(line, str) or not line:
        problems.append("line must be a non-empty string")
        return problems
    if line != line.strip():
        problems.append("line has leading or trailing whitespace")
    if "\n" in line or "\r" in line:
        problems.append("line must be exactly one line")
    # A door screen shows printable text only: reject control characters
    # (tab, bell, ...) even though they are technically ASCII.
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in line):
        problems.append("line must contain printable characters only")
    if len(line) > MAX_CHARS:
        problems.append("line is %d chars, over the %d limit" % (len(line), MAX_CHARS))
    try:
        line.encode("ascii")
    except UnicodeEncodeError:
        problems.append("line must be plain ASCII")
    return problems


def output_dir():
    """Where entry.txt goes: MAKEFUN_OUTPUT_DIR, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    problems = validate(LINE)
    if problems:
        for problem in problems:
            print("INVALID: %s" % problem, file=sys.stderr)
        return 1

    directory = output_dir()
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, OUTPUT_NAME)

    # Exactly the line plus one trailing newline -- nothing else.
    payload = (LINE + "\n").encode("ascii")
    with open(path, "wb") as handle:
        handle.write(payload)

    # Round-trip check: what landed on disk must be exactly what we wrote.
    with open(path, "rb") as handle:
        on_disk = handle.read()
    if on_disk != payload:
        print("INVALID: round-trip mismatch in %s" % path, file=sys.stderr)
        return 1

    print("chars: %d" % len(LINE))
    print("sha256: %s" % hashlib.sha256(payload).hexdigest())
    print("wrote: %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
