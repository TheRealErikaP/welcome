#!/usr/bin/env python3
"""
deploy.py — Deploy a personalized welcome page to GitHub Pages.

Usage:
  python deploy.py --token <PAT> --slug baxter --html-file rendered.html --scenario pre-appointment

What it does:
  1. Checks if the slug folder already exists in the repo
     (auto-increments if needed: baxter → baxter-2)
  2. Uploads asset files to /assets/ on first run only
  3. Pushes the rendered HTML to /<slug>/index.html
  4. Returns the live URL

Repo: therealerikap/welcome (must exist with GitHub Pages enabled)
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_OWNER = "therealerikap"
REPO_NAME = "welcome"
BRANCH = "main"
PAGES_BASE_URL = f"https://{REPO_OWNER}.github.io/{REPO_NAME}"
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


def gh_request(method, path, token, body=None):
    """Make a request to the GitHub API. Returns parsed JSON or None on 404."""
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "welcome-package-skill"
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 401:
            print("ERROR: GitHub authentication failed. Token may be expired or invalid.", file=sys.stderr)
            sys.exit(2)
        if e.code == 403:
            print("ERROR: GitHub permission denied. Token may not have repo write access.", file=sys.stderr)
            sys.exit(3)
        body_text = e.read().decode()
        print(f"ERROR: GitHub API {e.code}: {body_text}", file=sys.stderr)
        sys.exit(4)


def get_existing_file_sha(path, token):
    """Get the SHA of an existing file (needed to update it). Returns None if file doesn't exist."""
    result = gh_request("GET", f"/contents/{path}?ref={BRANCH}", token)
    if result and isinstance(result, dict):
        return result.get("sha")
    return None


def file_exists(path, token):
    """Check if a path exists in the repo."""
    return get_existing_file_sha(path, token) is not None


def folder_exists(path, token):
    """Check if a folder exists by listing its contents."""
    result = gh_request("GET", f"/contents/{path}?ref={BRANCH}", token)
    return result is not None and isinstance(result, list)


def upload_file(path, content_bytes, message, token):
    """Upload or update a file in the repo."""
    encoded = base64.b64encode(content_bytes).decode()
    body = {
        "message": message,
        "content": encoded,
        "branch": BRANCH
    }
    sha = get_existing_file_sha(path, token)
    if sha:
        body["sha"] = sha
    return gh_request("PUT", f"/contents/{path}", token, body=body)


def find_available_slug(base_slug, token):
    """Return base_slug if available, else base_slug-2, base_slug-3, etc."""
    if not folder_exists(base_slug, token):
        return base_slug
    n = 2
    while folder_exists(f"{base_slug}-{n}", token):
        n += 1
        if n > 50:
            raise RuntimeError(f"Cannot find available slug for {base_slug} after 50 tries")
    return f"{base_slug}-{n}"


def ensure_assets(token, assets_dir):
    """Upload assets to /assets/ folder if they don't exist yet."""
    assets = ["logo-cobalt.png", "logo-chalk.png", "erika-avatar.jpg", "erika-hero.jpg"]
    uploaded = []
    for asset in assets:
        repo_path = f"assets/{asset}"
        if file_exists(repo_path, token):
            continue
        local_path = Path(assets_dir) / asset
        if not local_path.exists():
            print(f"WARN: asset {local_path} not found locally, skipping", file=sys.stderr)
            continue
        with open(local_path, "rb") as f:
            content = f.read()
        upload_file(repo_path, content, f"Add {asset}", token)
        uploaded.append(asset)
    return uploaded


def ensure_readme(token):
    """Create a README on first run if the repo is empty."""
    if file_exists("README.md", token):
        return False
    content = b"""# Welcome Packages

Personalized client welcome pages by Erika Poindexter, Realtor.

Real Broker | CA DRE 01903694
"""
    upload_file("README.md", content, "Initial README", token)
    return True


def wait_for_deploy(url, max_seconds=120):
    """Poll the deployed URL until it returns 200 or timeout."""
    start = time.time()
    while time.time() - start < max_seconds:
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "welcome-package-skill"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            pass
        time.sleep(5)
    return False


def main():
    parser = argparse.ArgumentParser(description="Deploy a welcome page to GitHub Pages")
    parser.add_argument("--token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--slug", required=True, help="URL slug for the client (e.g., 'baxter')")
    parser.add_argument("--html-file", required=True, help="Path to the rendered HTML file")
    parser.add_argument("--scenario", default="pre-appointment",
                        help="Scenario name (for commit message)")
    parser.add_argument("--assets-dir", default=None,
                        help="Path to assets folder (defaults to ../assets relative to this script)")
    parser.add_argument("--no-wait", action="store_true",
                        help="Skip waiting for GitHub Pages to deploy")
    args = parser.parse_args()

    # Resolve assets directory
    if args.assets_dir:
        assets_dir = Path(args.assets_dir)
    else:
        assets_dir = Path(__file__).parent.parent / "assets"

    # Read the rendered HTML
    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}", file=sys.stderr)
        sys.exit(1)
    with open(html_path, "rb") as f:
        html_content = f.read()

    print(f"Deploying welcome page for slug '{args.slug}' (scenario: {args.scenario})")

    # First-run setup
    if ensure_readme(args.token):
        print("  Created README.md (first-time repo setup)")

    uploaded_assets = ensure_assets(args.token, assets_dir)
    if uploaded_assets:
        print(f"  Uploaded assets: {', '.join(uploaded_assets)}")

    # Find available slug
    final_slug = find_available_slug(args.slug, args.token)
    if final_slug != args.slug:
        print(f"  Slug '{args.slug}' already exists, using '{final_slug}' instead")

    # Upload the HTML
    repo_path = f"{final_slug}/index.html"
    commit_msg = f"Add welcome page for {final_slug} ({args.scenario})"
    upload_file(repo_path, html_content, commit_msg, args.token)
    print(f"  Pushed to {repo_path}")

    # Build live URL
    live_url = f"{PAGES_BASE_URL}/{final_slug}/"
    print(f"  Live URL (after Pages build): {live_url}")

    # Wait for deploy
    if not args.no_wait:
        print("  Waiting for GitHub Pages to build...", end="", flush=True)
        if wait_for_deploy(live_url):
            print(" ✓ live")
        else:
            print(" timed out (page should appear within 1-2 min)")

    # Output for parent script to capture
    print(f"\nFINAL_URL={live_url}")
    print(f"FINAL_SLUG={final_slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
