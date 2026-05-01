#!/usr/bin/env python3
"""
slugify.py — Generate a URL slug from a client name.

Usage:
  python slugify.py "Kerry & Carrie Baxter"  # → baxter
  python slugify.py "Maria Van Der Berg"     # → van-der-berg
  python slugify.py "John O'Brien"           # → obrien
"""

import re
import sys


def slugify(name):
    """
    Generate a URL slug from a client name.

    Rules:
    - Take only the LAST name (last word in the input)
    - Lowercase
    - Replace spaces with hyphens
    - Remove all non-alphanumeric characters except hyphens
    - Multi-word last names ("Van Der Berg") supported by passing the full last name as input
    """
    name = name.strip()

    # Strip common joining words and "& Partner" patterns
    # e.g., "Kerry & Carrie Baxter" → keep "Baxter"
    # e.g., "Smith and Jones" (two unrelated last names) → keep "Jones"
    # Remove ampersands and "and" with their surrounding context, take what's last
    parts = re.split(r"\s*(?:&|&amp;|\band\b|,)\s*", name)
    last_part = parts[-1].strip()  # Take last "person" in the list

    # From that, take the LAST WORD (that's the family name in most cases)
    # But for compound last names like "Van Der Berg", we need to be smart.
    # Heuristic: if there are 3+ words, assume "First [Middle] LastWord" → take last word
    # If 2 words, take the second word
    # User can pass last name only if they want compound: "Van Der Berg" alone
    words = last_part.split()
    if len(words) == 0:
        return "client"
    elif len(words) <= 2:
        # "Kerry Baxter" → "baxter", or "Van Berg" → "van-berg"
        # Take everything if 2 words and first looks like a particle (van, von, de, di, etc.)
        particles = {"van", "von", "de", "di", "du", "del", "della", "le", "la", "mc", "mac", "o"}
        if words[0].lower().rstrip("'") in particles:
            slug_source = " ".join(words)
        else:
            slug_source = words[-1]
    else:
        # 3+ words: scan for particles. If any word is a particle, include everything from
        # the first particle onward (so "Maria Van Der Berg" → "van der berg").
        particles = {"van", "von", "de", "di", "du", "del", "della", "le", "la", "mc", "mac"}
        first_particle_idx = None
        for i, w in enumerate(words):
            if w.lower() in particles:
                first_particle_idx = i
                break
        if first_particle_idx is not None:
            slug_source = " ".join(words[first_particle_idx:])
        else:
            slug_source = words[-1]

    # Lowercase, replace spaces with hyphens, strip non-alphanumeric
    slug = slug_source.lower()
    slug = slug.replace("'", "").replace("`", "")  # Remove apostrophes
    slug = re.sub(r"\s+", "-", slug)  # Spaces to hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)  # Strip everything else
    slug = re.sub(r"-+", "-", slug)  # Collapse multiple hyphens
    slug = slug.strip("-")

    return slug or "client"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: slugify.py 'Client Name'", file=sys.stderr)
        sys.exit(1)
    print(slugify(sys.argv[1]))
