---
name: welcome-package
description: Build, deploy, and send a personalized client welcome package as a live web page on therealerikap.github.io/welcome/{lastname}. Use when Erika mentions sending a pre-appointment package, a client onboarding package, or an off-market seller package. Three scenarios supported (pre-appointment, onboarding, off-market) and three client types (seller, buyer, both). The skill renders the right template, deploys to GitHub Pages, and drafts a Gmail email with the URL ready to send.
license: Internal use only — Erika Poindexter / Visible
---

# Welcome Package Skill

This skill generates personalized pre-appointment, onboarding, or off-market welcome pages for Erika's real estate clients. It outputs:
1. A live web page deployed to `https://therealerikap.github.io/welcome/{lastname-slug}/`
2. A Gmail draft email with the URL ready to send to the client

## When to use this skill

Use when Erika says anything like:
- "Send a welcome package to the Garcia family"
- "I have a listing appointment with the Smiths Tuesday — send the package"
- "Build a pre-appointment page for [name]"
- "Create an onboarding package for [name]"
- "Off-market package for [name]"
- "Run the welcome skill"

## Required inputs (gather these from Erika before building)

If Erika hasn't given all of these, use `ask_user_input_v0` to collect them with single-tap buttons:

1. **Client name(s)** — full names of the clients (e.g., "Kerry and Carrie Baxter", "Kevin Williams", "Maria Garcia")
2. **Scenario** — single_select between three options:
   - `Pre-Appointment` (still earning the business — has appointment scheduled)
   - `Onboarding` (already won — sending agreements/getting started)
   - `Off-Market` (full commission, off-MLS investor distribution)
3. **Client type** — single_select:
   - `Seller`
   - `Buyer`
   - `Both`
4. **Appointment date** (only if scenario is Pre-Appointment) — text like "Tuesday, April 28" or "Friday, May 3 at 2pm"
5. **Appointment location** (only if scenario is Pre-Appointment) — text like "Your home in Granite Bay" or "My Loomis office" or "Zoom"
6. **Property address** (optional, but ASK FOR IT if scenario is Pre-Appointment-Seller, Onboarding-Seller, or Off-Market) — short address like "1234 Main St" or "8946 Eureka Grove Cir." Used in the email subject line so the client immediately sees which property the package is about. Skip if it's a buyer or if Erika doesn't know yet.

Do NOT ask all six at once. Ask only what's missing. If Erika provided most info upfront, just confirm the missing pieces.

## Deriving first names from full names (CRITICAL — do this correctly)

The Skill needs TWO name variables:
- `--client-names`: HTML-formatted full names (e.g., `"Kerry &amp; Carrie Baxter"`)
- `--first-names`: Just first names joined with "and" (e.g., `"Kerry and Carrie"`)

You must derive first-names from the input. Examples:

| Input | --client-names | --first-names |
|-------|---------------|---------------|
| `Kevin Williams` | `Kevin Williams` | `Kevin` |
| `Maria Garcia` | `Maria Garcia` | `Maria` |
| `Kerry and Carrie Baxter` | `Kerry &amp; Carrie Baxter` | `Kerry and Carrie` |
| `Bob & Jane Smith` | `Bob &amp; Jane Smith` | `Bob and Jane` |
| `The Williams Family` | `The Williams Family` | `The Williams family` |
| `Dr. Lee` | `Dr. Lee` | `Dr. Lee` |

Rule of thumb: extract just the first names (the words before the surname). For couples, join with "and" (not "&"). For single people, use just their first name. If unclear (formal titles, family names without obvious first names), use the whole input gracefully.

Always convert `&` to `&amp;` in `--client-names` since it goes into HTML.

## Scenario-to-template mapping

| Scenario | Template file |
|----------|---------------|
| Pre-Appointment | `templates/template-preappointment.html` |
| Onboarding | `templates/template-onboarding.html` |
| Off-Market | `templates/template-offmarket.html` |

## Token replacement

After loading the template, replace these placeholders with the inputs:

| Token | Source | Example |
|-------|--------|---------|
| `{{CLIENT_NAMES}}` | Full names with `&amp;` for ampersand | "Kerry &amp; Carrie Baxter" |
| `{{CLIENT_FIRST_NAMES}}` | First names joined with "and" | "Kerry and Carrie" |
| `{{APPOINTMENT_DATE}}` | Full date | "Tuesday, April 28" |
| `{{APPOINTMENT_DAY}}` | Day name only | "Tuesday" |
| `{{APPOINTMENT_LOCATION}}` | Full location | "Your home in Granite Bay" |
| `{{LOCATION_SHORT}}` | Short version of location | "Granite Bay" or "Loomis Office" |

For Onboarding and Off-Market scenarios, only `{{CLIENT_NAMES}}` and `{{CLIENT_FIRST_NAMES}}` need filling.

For client type "Buyer" or "Both" in any scenario: TBD — initial version of the skill builds seller-version pages only. Buyer-specific template variations are a future enhancement. If Erika selects Buyer, build the page anyway but inform her: "I'm building a seller-format page for now. Buyer-specific copy is coming in v2 of the skill."

## Slug generation

From the client name, generate a URL slug:
- Take the LAST name only (e.g., "Baxter" from "Kerry & Carrie Baxter")
- Lowercase, alphanumeric only, hyphens for spaces
- Examples: "Baxter" → `baxter`, "Van Der Berg" → `van-der-berg`, "O'Brien" → `obrien`

If a slug already exists in the repo, append a numeric suffix (`baxter-2`).

## How to actually run the deployment (the working pattern)

The single command you should run for end-to-end build+deploy:

```bash
python3 SKILL_DIR/scripts/build_and_deploy.py \
  --secrets-file SKILL_DIR/_secrets.md \
  --scenario pre-appointment \
  --client-type seller \
  --client-names "Kerry &amp; Carrie Baxter" \
  --first-names "Kerry and Carrie" \
  --appointment-date "Tuesday, April 28" \
  --appointment-day "Tuesday" \
  --location-full "Your home in Granite Bay" \
  --location-short "Granite Bay" \
  --property-address "1234 Main St"
```

Where `SKILL_DIR` is the path to the welcome-package skill folder (typically `/mnt/skills/user/welcome-package/` or wherever the Skill is installed).

The scripts will auto-locate templates, snippets, and assets relative to their own location, so you don't need to pre-shuffle files. If the scripts can't find what they need, you'll get a clear error pointing to where they looked.

For Onboarding and Off-Market scenarios, omit the appointment-* and location-* flags:

```bash
python3 SKILL_DIR/scripts/build_and_deploy.py \
  --secrets-file SKILL_DIR/_secrets.md \
  --scenario off-market \
  --client-type seller \
  --client-names "Kevin Williams" \
  --first-names "Kevin" \
  --property-address "5678 Oak Ave"
```

Note: for off-market, the `--property-address` is used in the email subject ONLY. The page itself does NOT show the address, for discretion.

## GitHub deployment workflow

### Step 1: Read the GitHub PAT

Read the file `_secrets.md` from Project Knowledge. The PAT is on a line formatted as:
```
GITHUB_PAT=ghp_xxxxxxxx
```

If the file doesn't exist or the PAT is missing, tell Erika:
> The Skill needs a GitHub Personal Access Token to deploy. Add a file called `_secrets.md` to your Project Knowledge with one line: `GITHUB_PAT=ghp_yourtoken`. Then re-run the Skill.

If the PAT exists but the deployment fails with a 401, tell Erika:
> Your GitHub PAT may have expired. Generate a new one at github.com/settings/tokens, update `_secrets.md` in Project Knowledge, then re-run the Skill.

NEVER display the PAT value in any output to Erika or in any error message. Treat it as sensitive credential material.

### Step 2: Render the personalized HTML

Load the appropriate template, run all token replacements, save to a temporary file.

### Step 3: Push to GitHub

The repo is `therealerikap/welcome` with GitHub Pages enabled.

The file path in the repo for a deployed page should be:
```
{slug}/index.html
```

So Baxter's page lives at `welcome/baxter/index.html` and is publicly accessible at `https://therealerikap.github.io/welcome/baxter/`.

Use the GitHub Contents API to push. The script `scripts/deploy.py` handles this — call it with these arguments:
- `--token` (the PAT, read from _secrets.md)
- `--slug` (the URL slug)
- `--html-file` (path to the rendered HTML)
- `--scenario` (pre-appointment, onboarding, or off-market) — used in commit message
- `--force-assets` (optional — re-uploads assets even if they exist in repo, useful when assets have been updated)

The script handles:
- Checking if the slug already exists (and incrementing if so)
- Creating or updating the file via PUT to /repos/therealerikap/welcome/contents/{slug}/index.html
- Committing with a clear message like "Add welcome page for Baxter (pre-appointment)"
- Returning the live URL

### When to use --force-assets

Use `--force-assets` when:
- This is the first deploy after Erika updates her headshot, hero photo, or logo files
- A previous deploy uploaded the wrong asset version (e.g., chalk logo where cobalt should be)
- Erika asks "redeploy with the latest assets"

Otherwise, omit it. Assets only need to be uploaded once, and re-uploading them on every deploy is wasteful.

If the assets folder (logo-cobalt.png, logo-chalk.png, erika-avatar.jpg, erika-hero.jpg) doesn't exist in the repo yet, the script will upload those first as a one-time setup.

### Step 4: Wait for GitHub Pages to deploy

GitHub Pages typically takes 30-90 seconds to build after a commit. The script waits for the page to return HTTP 200 before reporting success (max wait: 2 minutes, then reports the URL with a note that it may take a moment to appear).

## Email drafting

After successful deployment, draft a Gmail email per Erika's existing email rules (see her `my-rules.md`):

**Recipient handling:**
- For NEW clients (Erika hasn't emailed them recently): draft to herself (`erika@poindexterteam.com`) so she can manually add the recipient as a safety check
- For ongoing threads or known recipients: ask Erika "Do you want me to draft this directly to the client, or to you?"
- Default to drafting to Erika herself if uncertain

**Subject line composition:**

The subject line should include the property address when provided, separated by " — ". This helps the client immediately see which property the package is about.

For ALL scenarios (including off-market): if a property address was provided, append " — [address]" to the subject. The address goes in the email subject regardless of scenario, because the client needs to know which property they're being contacted about.

The discretion rule applies only to the PUBLIC PAGE: off-market does NOT show the address on the page itself. The email is private 1:1 communication, so the address is safe there.

Pre-Appointment subjects:
- With property: `Before our {{APPOINTMENT_DAY}} appointment — {{PROPERTY_ADDRESS}}`
- Without property: `Before our {{APPOINTMENT_DAY}} appointment`

Onboarding subjects:
- With property (seller): `Welcome aboard + what happens next — {{PROPERTY_ADDRESS}}`
- Without property: `Welcome aboard + what happens next`

Off-Market subjects:
- With property: `Welcome + how I sell off-market — {{PROPERTY_ADDRESS}}`
- Without property: `Welcome + how I sell off-market`

**Email content varies by scenario AND client type:**

The emails below should be drafted in Erika's voice using the actual content provided. Replace tokens, then create the Gmail draft using the create_draft tool.

### Pre-Appointment seller email
```
Subject: Before our {{APPOINTMENT_DAY}} appointment[{{ — PROPERTY_ADDRESS}}]

Hi {{CLIENT_FIRST_NAMES}},

Looking forward to {{APPOINTMENT_DAY}} at {{APPOINTMENT_LOCATION}}. Before we sit down, I put together a page that walks through everything I want you to know going in: how I work, what your money pays for, the post-NAR compensation landscape, and what to expect at our appointment.

It's about a 12-minute read: https://therealerikap.github.io/welcome/{slug}/

A few things to know before {{APPOINTMENT_DAY}}:
- I won't bring a price recommendation. I have to see your home first.
- I will bring marketing samples from recent listings, my listing agreement, and a walkthrough checklist.
- Within 48 hours after our appointment, you'll have a custom CMA, net sheet, and marketing plan from me.

I also added a section near the bottom of the page with a few things I'd love to know before we meet — trust/entity ownership, liens, tenants, unpermitted work, solar, and your timing. If you can reply with what you know, that's great. If not, just bring the answers when we sit down.

See you {{APPOINTMENT_DAY}}.

Erika

[full signature block]
```

### Pre-Appointment buyer email
```
Subject: Before our {{APPOINTMENT_DAY}} consultation

Hi {{CLIENT_FIRST_NAMES}},

Looking forward to {{APPOINTMENT_DAY}}. Buying a home in 2026 is more involved than it used to be, especially after the NAR changes last year, so I put together a page that walks through how I work, what to expect, and what your representation actually covers.

It's about a 12-minute read: https://therealerikap.github.io/welcome/{slug}/

A few things to know before {{APPOINTMENT_DAY}}:
- Bring whoever is making the decision with you (spouse, partner, parent, anyone on the loan).
- If you've already talked to a lender, bring your pre-approval letter. If not, that's fine — we'll figure it out together.
- We'll sign a buyer representation agreement before I show you any homes. The page covers what's in it.

I also added a section near the bottom with a few things I'd love to know before we meet — pre-approval status, down payment situation, loan type, and timing. If you can reply with what you know, that's great. If not, just bring the answers.

See you {{APPOINTMENT_DAY}}.

Erika

[full signature block]
```

### Onboarding seller email
```
Subject: Welcome aboard + what happens next[{{ — PROPERTY_ADDRESS}}]

Hi {{CLIENT_FIRST_NAMES}},

So glad we're working together. I put together a page that walks through how I work, what your money pays for, and exactly what happens over the next few weeks.

Read it here: https://therealerikap.github.io/welcome/{slug}/

The shortest version of what's coming:
- DocuSign with your listing agreement is hitting your inbox in the next day or two
- I'll reach out within 48 hours of your signature to schedule the photographer walkthrough
- We'll be live on the market in 1 to 2 weeks
- You'll get a real written update from me weekly once we're live

There's also a section near the bottom of the page with a few things I need to confirm this week — trust/entity ownership, liens, tenants, unpermitted work, solar, and your timing. Reply when you have a chance, or text me, whatever's easier.

If anything raises a question, text me. That's what I'm here for.

Let's go.

Erika

[full signature block]
```

### Onboarding buyer email
```
Subject: Welcome aboard + what happens next

Hi {{CLIENT_FIRST_NAMES}},

So glad we're working together. I put together a page that walks through how I work, what your representation covers, and exactly what happens between now and your keys.

Read it here: https://therealerikap.github.io/welcome/{slug}/

The shortest version of what's coming:
- DocuSign with your buyer representation agreement is hitting your inbox in the next day or two
- If you haven't talked to a lender yet, I'd love to introduce you to Kristin at Borrow Smart or Lindsay at CARE Finance Group. Both are excellent.
- Once you're pre-approved, we'll set up your custom MLS search and start touring homes together
- You'll see homes the second they hit the market, and we'll go see them in person

There's a section near the bottom of the page with a few things I need to confirm this week — pre-approval status, down payment situation, loan type, and timing. Reply when you have a chance.

If anything raises a question, text me.

Let's go.

Erika

[full signature block]
```

### Off-Market seller email
```
Subject: Welcome + how I sell off-market

Hi {{CLIENT_FIRST_NAMES}},

Thanks for trusting me with this one. Off-market sales are some of my favorite work, and I want you to walk in knowing exactly how the next few weeks are going to roll out.

Read the full page here: https://therealerikap.github.io/welcome/{slug}/

The shortest version:
- DocuSign with your listing agreement is hitting your inbox in the next day or two
- The investor outreach starts the moment we have your signature. I have 200+ active investor buyers and 30+ regular Placer County flippers in my direct database.
- We'll know in 2 to 3 weeks whether the off-market approach is bringing the right offer. If not, we pivot to full MLS without losing momentum or paying anything extra.

There's also a section near the bottom of the page with a few things I need to confirm this week — trust/entity ownership, liens, tenants, unpermitted work, solar, and your timing. Off-market sales move fast, so the sooner I have these answers, the better I can brief the network. Reply when you have a chance.

If anything raises a question, text me.

Let's go.

Erika

[full signature block]
```

Use the Gmail `create_draft` tool. After creating the draft, report:

```
✓ Welcome page is live: https://therealerikap.github.io/welcome/{slug}/
✓ Email drafted in Gmail (subject: "[subject]", recipient: [you/client])

Open Gmail Drafts to review and send. The page may take 30-60 seconds to fully appear after first deploy.

Want me to do anything else with this client?
```

## File structure in the GitHub repo

```
therealerikap/welcome/
├── README.md                    (one-time: "Welcome packages by Erika Poindexter")
├── assets/
│   ├── logo-cobalt.png         (Real wordmark, cobalt color, for use on light backgrounds)
│   ├── logo-chalk.png          (Real wordmark, white, for use on dark backgrounds)
│   ├── erika-avatar.jpg        (small head crop for sticky header)
│   └── erika-hero.jpg          (full editorial portrait for hero section)
└── {slug}/
    └── index.html              (one folder per client, page lives at /index.html)
```

## Things to never do

- Never display the GitHub PAT in any output, even in error messages
- Never auto-send the email. Always create as draft only.
- Never use a slug that contains punctuation, spaces, or special characters
- Never overwrite an existing client's page without confirming with Erika first
- Never include private financial details (net sheet figures, exact pricing) on the public web page
- Never mention specific addresses on the public web page (use neighborhood names like "Granite Bay" instead)

## Things to always do

- Always confirm the inputs back to Erika before deploying ("Building Pre-Appointment seller package for Kerry & Carrie Baxter, appointment Tuesday April 28 at their home in Granite Bay. Deploying to /welcome/baxter/. Sound right?")
- Always use the existing assets in /assets/ folder, never re-embed images as base64 (keeps files small and updates centralized)
- Always follow Erika's voice rules from `my-rules.md` and `my-voice.md` in any custom copy you generate
- Always report the live URL and the email draft location after a successful run
