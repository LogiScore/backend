# 🔐 LogiScore Development Safety Prompt for Cursor

**Last updated:** 2025-08-08 09:58 UTC  
**Purpose:** Prevent accidental repo confusion, static content insertion, or unintended code deletion by enforcing strict development rules for Cursor while working on the LogiScore project.

---

## ⚙️ Project Architecture Overview

- LogiScore is a structured platform with two **strictly separated** codebases:
  - **Frontend**: Built with **SvelteKit**, responsible for dynamic user-facing interfaces.
  - **Backend**: Powered by **FastAPI**, hosted on **Render**, and connected to a **PostgreSQL** database.
- **These repos must never be cross-referenced.** No file, function, or logic should be copied between them unless explicitly requested and approved.

---

## 🚨 ABSOLUTE RESTRICTIONS

### ❌ Do Not:

1. Copy code between frontend and backend.
2. Push or auto-commit to **any** repo without:
   - Showing a full summary of changes
   - Declaring target repo(s)
   - Waiting for user approval
3. Insert static content in production components (no hardcoded plans, categories, links, reviews, or scores).
4. Delete or overwrite unrelated components, files, or markup (even within the same file).
5. Refactor, restructure, or remove unused code unless **specifically** instructed.

---

## ✅ Do:

1. Identify which repo you're working in:
   - "Frontend (SvelteKit)" or "Backend (FastAPI)"
2. Modify **only the file** currently being discussed.
3. Create dynamic components that:
   - Pull data from APIs or database
   - Use backend endpoints or store bindings
   - Respect user permissions and states
4. Review and align with:
   - `LogiScore_User_Requirements.md`
   - `LogiScore_Technical_Documentation.md`
   - `LogiScore_Documentation.md`
5. Ask for confirmation before:
   - Making any change outside the scope
   - Applying fixes that touch shared layouts or modules
   - Initiating repo pushes or deployments

---

## 📦 Push Workflow (MANDATORY)

Before pushing to any branch:

- Summarize the proposed changes:
  - File names
  - Nature of changes
  - Repo path (frontend/backend)
- WAIT for user approval before executing.

📌 **If unsure about the destination repo or data source – stop and ask.**

---

## 🛡️ File-Level Safety

Before editing critical files (like `+page.svelte`, `+layout.svelte`, schema definitions, or API routes):

- Create a timestamped backup (e.g., `filename_YYYYMMDD_HHMM_backup.svelte`)
- OR prompt the user to back it up manually

This prevents accidental data or structure loss from AI hallucinations or misunderstood logic.

---

## 📂 Dynamic Data Enforcement

### For all frontend components:
- Must bind to:
  - API results from backend
  - Data stores
  - Props from route params or endpoints

### For all backend logic:
- Must operate with PostgreSQL via valid models
- Must return JSON for frontend consumption
- Must obey user roles and access rules from the documentation

---

## 🧠 Use Documentation Before Code

Reference project logic from:

- `LogiScore_User_Requirements.md`: User roles, permissions, and behavior rules
- `LogiScore_Technical_Documentation.md`: System architecture and APIs
- `LogiScore_Documentation.md`: Implementation details and data structures

If a feature contradicts documentation, do not implement it without clarification.

---

## 🔁 Common Mistakes Cursor Must Avoid

| Mistake | Impact | Prevention |
|--------|--------|------------|
| Editing unrelated sections | Breaks layout, deletes needed code | Touch only the requested file/section |
| Copying frontend code to backend | Corrupts repo logic | Know which repo you're in |
| Inserting static plans or reviews | Breaks dynamic data expectations | Pull from DB/API only |
| Auto-pushing to wrong repo | Can delete real files or deploy wrong logic | Always show plan and wait for user approval |
| Removing CSS classes or selectors silently | Breaks design | Leave CSS untouched unless modifying directly relevant components |

---

## 🧠 If In Doubt…

> **STOP. Ask. Verify.**
>
> Cursor must **never assume** behavior or logic. This project has strict architectural and operational boundaries. If logic is unclear or multiple interpretations exist, ask the user.

---

## ✅ Final Checklist (For Every Action)

- [ ] Are you in the correct repo (frontend or backend)?
- [ ] Are you editing the correct file only?
- [ ] Are you using dynamic data sources?
- [ ] Have you confirmed with documentation?
- [ ] Are you providing a push summary before deploying?
- [ ] Have you created a backup before structural edits?

---

This prompt is designed to **protect LogiScore from accidental damage**, ensure stable builds, and minimize developer frustration.

