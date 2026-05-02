# Secrets

This file holds credentials used by Skills. Keep it private.

---

## GitHub Personal Access Token

Replace the line below with your token, keeping the `GITHUB_PAT=` prefix.
The token starts with either `ghp_` (classic) or `github_pat_` (fine-grained).

GITHUB_PAT=PASTE_YOUR_TOKEN_HERE

---

## How to get a token

1. Go to https://github.com/settings/tokens?type=beta
2. "Generate new token" (fine-grained)
3. Token name: `Claude Welcome Skill`
4. Expiration: 90 days
5. Repository access: Only select repositories → choose `therealerikap/welcome`
6. Permissions:
   - Contents: Read and write
   - Pages: Read and write
   - Metadata: Read (auto)
7. Generate, copy the token, paste above replacing `PASTE_YOUR_TOKEN_HERE`

When the token expires, repeat steps 1-7 and update the line.
