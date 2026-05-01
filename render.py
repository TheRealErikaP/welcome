#!/usr/bin/env python3
"""
render.py — Fill a welcome package template with personalization tokens.

Usage:
  python render.py --scenario pre-appointment \\
                   --client-names "Kerry &amp; Carrie Baxter" \\
                   --first-names "Kerry and Carrie" \\
                   --appointment-date "Tuesday, April 28" \\
                   --appointment-day "Tuesday" \\
                   --location-full "Your home in Granite Bay" \\
                   --location-short "Granite Bay" \\
                   --output rendered.html
"""

import argparse
import sys
from pathlib import Path

TEMPLATE_MAP = {
    "pre-appointment": "template-preappointment.html",
    "preappointment": "template-preappointment.html",
    "onboarding": "template-onboarding.html",
    "off-market": "template-offmarket.html",
    "offmarket": "template-offmarket.html",
}


def main():
    parser = argparse.ArgumentParser(description="Render a welcome package template")
    parser.add_argument("--scenario", required=True,
                        choices=list(TEMPLATE_MAP.keys()),
                        help="Which scenario template to use")
    parser.add_argument("--client-names", required=True,
                        help='Full names with HTML ampersand, e.g., "Kerry &amp; Carrie Baxter"')
    parser.add_argument("--first-names", required=True,
                        help='First names joined with "and", e.g., "Kerry and Carrie"')
    parser.add_argument("--appointment-date", default="",
                        help='For pre-appointment scenario, e.g., "Tuesday, April 28"')
    parser.add_argument("--appointment-day", default="",
                        help='Day name only, e.g., "Tuesday"')
    parser.add_argument("--location-full", default="",
                        help='Full location, e.g., "Your home in Granite Bay"')
    parser.add_argument("--location-short", default="",
                        help='Short location, e.g., "Granite Bay"')
    parser.add_argument("--templates-dir", default=None,
                        help="Path to templates folder (defaults to ../templates)")
    parser.add_argument("--output", required=True,
                        help="Output path for rendered HTML")
    args = parser.parse_args()

    # Resolve templates directory
    if args.templates_dir:
        templates_dir = Path(args.templates_dir)
    else:
        templates_dir = Path(__file__).parent.parent / "templates"

    template_file = templates_dir / TEMPLATE_MAP[args.scenario]
    if not template_file.exists():
        print(f"ERROR: Template not found: {template_file}", file=sys.stderr)
        sys.exit(1)

    with open(template_file, "r", encoding="utf-8") as f:
        html = f.read()

    # Token replacements
    replacements = {
        "{{CLIENT_NAMES}}": args.client_names,
        "{{CLIENT_FIRST_NAMES}}": args.first_names,
        "{{APPOINTMENT_DATE}}": args.appointment_date,
        "{{APPOINTMENT_DAY}}": args.appointment_day,
        "{{APPOINTMENT_LOCATION}}": args.location_full,
        "{{LOCATION_SHORT}}": args.location_short,
    }

    for token, value in replacements.items():
        html = html.replace(token, value)

    # Sanity check: warn if any unfilled tokens remain
    import re
    unfilled = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if unfilled:
        print(f"WARN: Unfilled tokens in output: {set(unfilled)}", file=sys.stderr)

    # Adjust asset paths from relative (../assets/) to absolute (/welcome/assets/)
    # so the page works when deployed at /welcome/{slug}/index.html
    html = html.replace("../assets/", "/welcome/assets/")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Rendered: {output_path} ({len(html)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
