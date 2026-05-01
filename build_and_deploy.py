#!/usr/bin/env python3
"""
build_and_deploy.py — End-to-end: render the template, deploy to GitHub Pages.

Usage:
  python build_and_deploy.py \\
    --secrets-file /path/to/_secrets.md \\
    --scenario pre-appointment \\
    --client-names "Kerry &amp; Carrie Baxter" \\
    --first-names "Kerry and Carrie" \\
    --appointment-date "Tuesday, April 28" \\
    --appointment-day "Tuesday" \\
    --location-full "Your home in Granite Bay" \\
    --location-short "Granite Bay"

Reads the GitHub PAT from the secrets file (looking for GITHUB_PAT=...).
Renders the template to a temp file.
Deploys to GitHub Pages.
Prints the live URL.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Add scripts dir to path for slugify import
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from slugify import slugify


def read_pat(secrets_file):
    """Extract GITHUB_PAT from the secrets file."""
    if not Path(secrets_file).exists():
        return None
    with open(secrets_file, "r") as f:
        content = f.read()
    # Look for GITHUB_PAT=... outside of code blocks (the actual setting line)
    # Match a line that starts with GITHUB_PAT= and has a real-looking token
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("GITHUB_PAT="):
            value = line.split("=", 1)[1].strip()
            # Skip placeholder values
            if value and value != "PASTE_TOKEN_HERE" and not value.startswith("PASTE"):
                return value
    return None


def main():
    parser = argparse.ArgumentParser(description="Build and deploy a welcome page end-to-end")
    parser.add_argument("--secrets-file", required=True,
                        help="Path to _secrets.md containing GITHUB_PAT=...")
    parser.add_argument("--scenario", required=True,
                        choices=["pre-appointment", "preappointment", "onboarding",
                                 "off-market", "offmarket"])
    parser.add_argument("--client-names", required=True,
                        help='Full names with HTML ampersand, e.g., "Kerry &amp; Carrie Baxter"')
    parser.add_argument("--first-names", required=True,
                        help='First names joined with "and"')
    parser.add_argument("--appointment-date", default="")
    parser.add_argument("--appointment-day", default="")
    parser.add_argument("--location-full", default="")
    parser.add_argument("--location-short", default="")
    parser.add_argument("--slug-override", default=None,
                        help="Force a specific slug instead of generating from name")
    parser.add_argument("--no-wait", action="store_true",
                        help="Skip waiting for GitHub Pages to deploy")
    args = parser.parse_args()

    # Step 1: Read PAT
    pat = read_pat(args.secrets_file)
    if not pat:
        print("ERROR: GitHub PAT not found in secrets file. Edit "
              f"{args.secrets_file} and set GITHUB_PAT=ghp_...", file=sys.stderr)
        sys.exit(1)

    # Step 2: Generate slug
    if args.slug_override:
        slug = args.slug_override
    else:
        # Strip HTML entities for slug generation
        clean_names = args.client_names.replace("&amp;", "&").replace("&", "and")
        slug = slugify(clean_names)
    print(f"Slug: {slug}")

    # Step 3: Render to temp file
    render_script = SCRIPT_DIR / "render.py"
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as tmp:
        tmp_path = tmp.name

    render_cmd = [
        sys.executable, str(render_script),
        "--scenario", args.scenario,
        "--client-names", args.client_names,
        "--first-names", args.first_names,
        "--output", tmp_path,
    ]
    if args.appointment_date:
        render_cmd.extend(["--appointment-date", args.appointment_date])
    if args.appointment_day:
        render_cmd.extend(["--appointment-day", args.appointment_day])
    if args.location_full:
        render_cmd.extend(["--location-full", args.location_full])
    if args.location_short:
        render_cmd.extend(["--location-short", args.location_short])

    print("Rendering template...")
    result = subprocess.run(render_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR rendering: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"  {result.stdout.strip()}")
    if result.stderr:
        print(f"  warnings: {result.stderr.strip()}")

    # Step 4: Deploy
    deploy_script = SCRIPT_DIR / "deploy.py"
    deploy_cmd = [
        sys.executable, str(deploy_script),
        "--token", pat,
        "--slug", slug,
        "--html-file", tmp_path,
        "--scenario", args.scenario,
    ]
    if args.no_wait:
        deploy_cmd.append("--no-wait")

    print("Deploying to GitHub Pages...")
    result = subprocess.run(deploy_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR deploying: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Parse the FINAL_URL line from deploy output
    final_url = None
    final_slug = None
    for line in result.stdout.splitlines():
        print(f"  {line}")
        if line.startswith("FINAL_URL="):
            final_url = line.split("=", 1)[1]
        elif line.startswith("FINAL_SLUG="):
            final_slug = line.split("=", 1)[1]

    # Cleanup temp file
    try:
        os.unlink(tmp_path)
    except OSError:
        pass

    # Final report
    print()
    if final_url:
        print(f"✓ Deployed: {final_url}")
        print(f"✓ Slug used: {final_slug or slug}")
    else:
        print("Deploy completed but URL not captured. Check therealerikap/welcome on GitHub.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
