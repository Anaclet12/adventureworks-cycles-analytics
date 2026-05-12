# Migration Guide — Moving Your Existing Work Into the Monorepo

This guide walks you through migrating your existing repositories and local work into the `adventureworks-cycles-analytics` monorepo structure.

## What You'll Do

1. Extract this scaffold into a new folder on your machine.
2. Migrate your existing SQL repo (`adventureworks-dwh`) into `01_data_engineering/`.
3. Copy your Power BI artifacts into `02_business_intelligence/`.
4. Drop the ML scaffolding (from earlier in this conversation) into `03_machine_learning/`.
5. Initialize git, commit, and push to GitHub.

## Prerequisites

- Git installed locally
- GitHub account
- Your existing `adventureworks-dwh` repo cloned locally (or accessible)
- The 3 gold-layer CSV extracts you used for Power BI
- The Power BI `.pbix` file

---

## Step 1 — Extract the Scaffold

1. Download `adventureworks-cycles-analytics-scaffold.tar.gz` (provided alongside this guide).
2. Extract it where you keep your projects:

```bash
cd ~/projects     # or wherever you keep code
tar -xzf adventureworks-cycles-analytics-scaffold.tar.gz
cd adventureworks-cycles-analytics
```

Verify the structure:

```bash
ls -la
# You should see: README.md, LICENSE, .gitignore, 4 phase folders, docs/, .github/
```

---

## Step 2 — Migrate the SQL Repo Into `01_data_engineering/`

You have two options.

### Option A — Copy the contents (recommended if your SQL repo isn't pushed to GitHub yet)

Locate your existing `adventureworks-dwh` folder. Copy its contents (NOT the folder itself) into `01_data_engineering/`:

```bash
# Linux / macOS / WSL
cp -r /path/to/adventureworks-dwh/* 01_data_engineering/
cp -r /path/to/adventureworks-dwh/.git* 01_data_engineering/ 2>/dev/null || true

# Windows PowerShell
Copy-Item -Path "C:\path\to\adventureworks-dwh\*" -Destination "01_data_engineering\" -Recurse
```

After copying, verify:

```bash
ls 01_data_engineering/
# Should show: README.md, docs/, scripts/, sql/, data/, etc.
```

The scaffold already includes a README.md for this folder. Decide which one to keep:
- **If your existing repo had a thorough README** that fits the phase folder, keep yours and replace the scaffold's.
- **If your existing README was repo-level (not phase-level)**, keep the scaffold's and migrate any extra content from yours into the appropriate top-level `docs/`.

### Option B — git subtree merge (if your SQL repo is on GitHub and you want to preserve commit history)

```bash
# From the monorepo root
git remote add dwh-repo https://github.com/<your-username>/adventureworks-dwh.git
git fetch dwh-repo
git read-tree --prefix=01_data_engineering/ -u dwh-repo/main
git commit -m "Migrate adventureworks-dwh into 01_data_engineering/"
```

This preserves the file history. Note this is a Git subtree merge — the commits aren't preserved on the new branch, but `git log --follow` will show file history.

---

## Step 3 — Set Up `02_business_intelligence/`

1. Copy your Power BI `.pbix` file:

```bash
cp /path/to/AdventureWorks_Analytics.pbix 02_business_intelligence/pbix/
```

2. Copy the gold-layer CSV extracts to `extracts/` (these will be gitignored, so they're just local working copies):

```bash
cp /path/to/fact_sales.csv 02_business_intelligence/extracts/
cp /path/to/dim_customers.csv 02_business_intelligence/extracts/
cp /path/to/dim_products.csv 02_business_intelligence/extracts/
```

3. Take screenshots of each dashboard in Power BI Desktop and save them:

```
02_business_intelligence/screenshots/
├── d1_sales_margin.png
├── d2_customer_intelligence.png
└── d3_operations_fulfillment.png
```

Open the .pbix → File → Export → Export to PDF, or just screenshot each page.

4. Fill in the documentation placeholders in `02_business_intelligence/docs/`. These will be created in a future step when we work on Phase 2 documentation:
   - `BLUEPRINT.md` — the dashboard blueprint we built earlier in our conversation
   - `DAX_MEASURES.md` — list every measure with its DAX formula
   - `DATA_MODEL.md` — a screenshot of the Model view + explanation

---

## Step 4 — Set Up `03_machine_learning/` (Placeholder Only)

The ML phase is still being built. For now:

1. Place the gold-layer CSV extracts in `03_machine_learning/data/processed/`:

```bash
cp /path/to/fact_sales.csv 03_machine_learning/data/processed/
cp /path/to/dim_customers.csv 03_machine_learning/data/processed/
cp /path/to/dim_products.csv 03_machine_learning/data/processed/
```

2. If you exported your `Customer_RFM` table from Power BI:

```bash
cp /path/to/customer_rfm.csv 03_machine_learning/data/processed/
```

The actual Python code (notebooks + src modules) will be added in the next conversation step.

---

## Step 5 — Set Up `04_production_deployment/` (Empty Placeholder)

Nothing to do here yet. The Docker, FastAPI, and monitoring files will be built during Phase 4.

---

## Step 6 — Initialize Git and Push to GitHub

### 6.1 Initialize the monorepo

```bash
cd adventureworks-cycles-analytics

# If you used Option A in Step 2 (copy), the .git folder from the old repo may
# have been copied — remove it and start fresh:
rm -rf 01_data_engineering/.git
rm -rf 01_data_engineering/.github

# Initialize the monorepo's own git
git init
git add .
git status              # Review what's about to be committed
git commit -m "Initial monorepo scaffold with Phase 1 (Data Engineering) migrated"
```

### 6.2 Create the GitHub repo

1. Go to https://github.com/new
2. Repository name: **`adventureworks-cycles-analytics`**
3. Description: *"End-to-end analytics platform: PostgreSQL data warehouse, Power BI dashboards, Python ML/DL, and production deployment."*
4. Visibility: **Public** (this is your portfolio piece)
5. Do NOT initialize with README, .gitignore, or license — we already have these.
6. Click **Create repository**.

### 6.3 Push to GitHub

GitHub will show you the commands. They'll look like:

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/adventureworks-cycles-analytics.git
git push -u origin main
```

### 6.4 Archive the Old Repo

Once the monorepo is up and verified:

1. Go to your old `adventureworks-dwh` repo on GitHub.
2. **Settings → Archive this repository** (scroll to the danger zone).
3. Add a note to its README: *"This repository has been merged into [adventureworks-cycles-analytics](https://github.com/<your-username>/adventureworks-cycles-analytics). See `01_data_engineering/` in the monorepo for the current version of this code."*

Don't delete the old repo — archiving preserves it as read-only while pointing visitors to the new home.

---

## Step 7 — Verify the Repo Looks Good on GitHub

After pushing, visit your new repo on GitHub. The README will render automatically. Check:

- ✅ The top-level README displays the project overview clearly
- ✅ Each phase folder has its own README that renders when clicked
- ✅ The `docs/` folder is visible and its files render
- ✅ No raw data files are accidentally committed (run `git ls-files | grep csv` to verify)
- ✅ The badges at the top of the README render correctly

If the ecosystem image doesn't appear in the README:
- Save the image you generated for LinkedIn into `docs/images/analytics_ecosystem.png`.
- Commit and push.

---

## Step 8 — Tag the Phase 1 Release

Mark the milestone so visitors can find it cleanly:

```bash
git tag -a v0.1-data-engineering -m "Phase 1 complete: PostgreSQL medallion warehouse"
git push origin v0.1-data-engineering
```

Future tags as you complete each phase:
- `v0.2-business-intelligence` — when Power BI is done
- `v0.3-machine-learning` — when notebooks + segmentation + forecasting are done
- `v1.0` — when the FastAPI + Docker deployment is up and demonstrable

---

## Troubleshooting

### "My SQL repo had files I don't want in the monorepo"

Common candidates to exclude:
- Local PostgreSQL config files
- Editor settings (.vscode/, .idea/) — already in .gitignore
- Test/scratch SQL files

Move them out of `01_data_engineering/` before committing.

### "I get permission denied when pushing to GitHub"

You need either an SSH key configured or a Personal Access Token. For HTTPS:
- GitHub → Settings → Developer settings → Personal access tokens → Generate new token (classic)
- Scope: `repo`
- Use the token as your password when prompted by `git push`.

### "The .pbix file is too large for GitHub"

GitHub has a 100MB file size limit. If your .pbix exceeds it:
- Try Power BI's "Reduce file size" option (File → Options → Reduce file size).
- Consider Git LFS (Large File Storage): https://git-lfs.com/
- Or host the .pbix elsewhere (Google Drive, OneDrive) and link to it from the README.

### "I want to test before pushing"

Set up the remote but don't push yet:

```bash
git remote add origin https://github.com/<your-username>/adventureworks-cycles-analytics.git
git remote -v    # Verify
# When ready:
git push -u origin main
```

---

## What's Next

After the monorepo is on GitHub:

1. Continue building Phase 3 (Machine Learning). The next conversation step picks up from `03_machine_learning/`.
2. Once Phase 3 is complete, move to Phase 4 (Production Deployment).
3. Polish the screenshots, fill in documentation gaps, and tighten the README.

Your portfolio piece is then complete and shareable.
