# Welcome Package Skill — Usage Guide

This is your guide to using the welcome-package Skill. It generates personalized client landing pages, deploys them to GitHub Pages, and drafts the email to send. End to end, about 30 seconds per client.

## What the Skill does

You tell Claude:
> "Send a pre-appointment package to Kerry & Carrie Baxter for our Tuesday 2pm appointment at their home in Granite Bay."

The Skill:
1. Renders a personalized HTML page in your Real-branded design system
2. Pushes it to your GitHub repo at `therealerikap/welcome`
3. GitHub Pages publishes it at `https://therealerikap.github.io/welcome/baxter/`
4. Drafts an email in your Gmail with the URL ready to send
5. Tells you what's done

You open Gmail, review the draft, hit send.

## One-time setup (do this once)

You'll need to do these three things one time before the Skill works.

### Step 1 — Create the GitHub repo

1. Go to **github.com**, log in as `therealerikap`
2. Top right corner → "+" → "New repository"
3. Name it: `welcome`
4. Owner: `therealerikap`
5. Visibility: **Public** (required for GitHub Pages on free accounts)
6. Check "Add a README file"
7. Click "Create repository"

### Step 2 — Enable GitHub Pages on the repo

1. In the new `welcome` repo, click "Settings" (top tab)
2. Left sidebar: "Pages"
3. Source: "Deploy from a branch"
4. Branch: `main`, Folder: `/ (root)`
5. Click "Save"
6. Wait about 1 minute. The page will show "Your site is live at https://therealerikap.github.io/welcome/"

### Step 3 — Generate a Personal Access Token (PAT)

1. Go to **github.com/settings/tokens?type=beta** (fine-grained tokens)
2. Click "Generate new token"
3. Token name: `Claude Welcome Skill`
4. Expiration: **90 days** (you'll need to renew quarterly)
5. Repository access: **Only select repositories** → choose `therealerikap/welcome`
6. Permissions:
   - **Contents:** Read and write
   - **Pages:** Read and write
   - **Metadata:** Read (this is auto-selected)
7. Click "Generate token"
8. **Copy the token immediately.** You won't see it again. Looks like `github_pat_xxxxxxx...`

### Step 4 — Install the Skill in your Claude Project

1. In this Claude Project, click the menu → "Knowledge" or "Skills"
2. Upload the `welcome-package` folder (the whole folder, not individual files)
3. Open the file `_secrets.md` inside the uploaded skill
4. Find the line that says `GITHUB_PAT=PASTE_TOKEN_HERE`
5. Replace `PASTE_TOKEN_HERE` with the token you copied from GitHub
6. Save

That's it. Setup done.

## How to actually use it

Open a new chat in this Project. Say something like:

> "Run the welcome package skill for Maria Garcia, pre-appointment, seller, Friday May 9 at 10am at her home in Rocklin."

Or more casually:

> "I need to send a pre-appointment package to the Smiths. Listing appointment is Tuesday at 6pm at their place in Granite Bay."

Or super short:

> "Run the welcome skill"

(In the third case, Claude will ask you the missing details with single-tap buttons — no typing required.)

Claude will:
1. Confirm the inputs back to you
2. Build the page
3. Push to GitHub
4. Wait for GitHub Pages to deploy (~30-60 seconds)
5. Draft the email in Gmail
6. Report the URL

You'll get back something like:
```
✓ Page is live: https://therealerikap.github.io/welcome/garcia/
✓ Email drafted in Gmail (subject: "Quick read before our Friday appointment")

Open Gmail Drafts to review and send.
```

## The three scenarios

When the Skill asks you what scenario, here's how to choose:

### Pre-Appointment
Use when: You have a listing or buyer consultation scheduled. Still earning the business. Need to send the package ahead of time so they walk in informed.

Required: Appointment date, time, and location.

### Onboarding
Use when: They've already chosen you. You're sending the agreements and getting started.

The page reads "Glad we're doing this. Here's the playbook." It mentions the DocuSign coming and lays out what happens over the next few weeks.

Required: Just client names. No appointment details needed.

### Off-Market
Use when: Off-MLS sale. Investor distribution. Same 3% but no public listing, no photography, no open houses.

The page emphasizes your investor network (200+ buyers, 30+ Placer County flippers), broker network distribution, and the "we can pivot to full MLS if needed" upgrade path.

Required: Just client names. No appointment details needed.

## What if something goes wrong

### "GitHub PAT not found" or 401 error
Your token expired or was never set. Open `_secrets.md` in your Project Knowledge, paste a new token from github.com/settings/tokens, save.

### "Slug already exists, using baxter-2"
You have two clients with the same last name. Skill auto-increments. The URL becomes `welcome/baxter-2/`. Edit the URL in your email draft if you want to make sense of which Baxter it is.

### "Page not loading"
GitHub Pages can take 1-2 minutes to build the first time after a commit. Wait a minute and refresh.

### "I want to update an existing client's page"
Tell Claude: "Update the Baxter welcome page" and re-run the Skill with the slug override. The Skill will overwrite the existing page.

### "I want to delete a client's page"
Go to github.com/therealerikap/welcome, navigate to the slug folder, delete the file from the GitHub web interface. Or ask Claude to do it.

## Maintaining the Skill

### When the PAT expires (every 90 days)
1. Generate a new token (same steps as Step 3 above)
2. Update `_secrets.md` in your Project Knowledge with the new token
3. Done. Skill keeps working.

### When you want to update your bio, photos, or copy
The master content lives in `pre-appointment-master-v2.docx`. Edit it. Then ask Claude to rebuild the templates from the updated master. (We can build a "rebuild templates" command later if this happens often.)

### When you want to update your headshot or hero photo
Replace `assets/erika-avatar.jpg` and `assets/erika-hero.jpg` in the Skill folder. Re-upload. Next deployed page will use the new images. Existing pages can be force-refreshed by re-running the Skill on those clients.

### When you want to add a custom domain
You can point `welcome.poindexterteam.com` at the GitHub Pages site. Settings → Pages → Custom domain → enter `welcome.poindexterteam.com` → set up the CNAME at GoDaddy. Ask Claude to walk you through the DNS setup when you're ready.

## Sharing with your Real friends

The Skill is yours. To share with another agent:

1. Zip the whole `welcome-package` folder (with their headshot, logo, content swapped in)
2. They install it in their own Claude Project
3. They follow steps 1-4 of one-time setup with their own GitHub account and PAT
4. They edit the Skill's templates to swap your name/DRE/contact info for theirs

The full package for sharing — including a setup guide written for them — is on the roadmap. Once you've used your version a few times and we've ironed out any rough edges, we'll package the shareable version.

## What's not in v1 (and what could be added)

- **Buyer-specific copy:** The current Skill builds seller-format pages even when type is "Buyer." A v2 will swap the copy to buyer-specific language.
- **Both buyer + seller in one package:** Same — currently routes to seller. v2 will combine both.
- **Calendar invite generation:** A `.ics` calendar file attached to the email so the client can add the appointment in one tap. Easy add-on.
- **Loom video embed:** A spot in the page where you can drop a personal Loom URL ("Hi Kerry & Carrie, here's a quick hello..."). Easy add-on.
- **Click tracking:** Knowing if/when they opened the page. Requires moving off pure GitHub Pages to something with analytics. Future consideration.

## The TL;DR

1. Set up GitHub repo + PAT (one time, ~10 min)
2. Install Skill, paste PAT in `_secrets.md` (one time, ~2 min)
3. Going forward: "Run the welcome skill for [client name], [scenario], [details]"
4. Skill builds, deploys, drafts email
5. Open Gmail, send

That's it. Welcome to the future of you not making one-off Canva pages every time you onboard a client.
