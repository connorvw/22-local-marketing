---
name: bpt-client-onboarding
description: Full client onboarding with Google Drive folder creation, onboarding email draft, project/sprint/deliverables, and follow-up reminders.
---

# Client Onboarding

Complete client onboarding workflow: creates Google Drive folder, drafts onboarding email, sets up project/sprint/deliverables, and schedules follow-up reminders.

## When to Use

- Immediately after lead status changes to `closed_won`
- When starting work with a new client
- After a signed proposal/contract

## Prerequisites

- Lead record with `closed_won` status (or client info from user)
- **Google Integration (optional but recommended):**
  - **Claude Desktop:** Enable Google Drive and Gmail in Settings → Integrations
  - **Claude Code:** Add the Google Drive and Gmail MCP servers to your project's `.mcp.json` or global config

  Without Google integration, the skill will still create the local client record, project, sprint, and follow-ups - just without Drive folders or email drafts.

## Workflow

This is an **interactive workflow** with 9 steps. Guide the user through each step, confirming progress.

### Step 1: Get Client Info

**From lead:**
```
leads_get { "id": "{lead-uuid}" }
```

**Or ask user for:**
- Company name
- Contact name
- Email
- Website

### Step 2: Check & Configure Google Integration

Get agency profile and check for required config:

```
agency_get {}
```

**If `google_config.client_work_folder_id` is missing:**

> "I notice Google Drive isn't configured yet. To create a Drive folder for this client, I need your parent folder ID.
>
> Go to your client folders location in Google Drive - the folder ID is in the URL after `/folders/`
>
> Paste the folder ID, or type 'skip' to continue without Google Drive:"

If they provide a folder ID, attempt to save it:
```
agency_update { "google_config": { "client_work_folder_id": "{folder_id}" } }
```

**If `calendar_link` is missing:**

> "What's your scheduling link for kickoff calls? (e.g., https://calendly.com/you/kickoff)
>
> This will be included in onboarding emails. Type 'skip' to leave it out:"

If they provide a link, save it:
```
agency_update { "calendar_link": "{link}" }
```

**If `google_config.access_checklist_id` is missing:**

Create an agency copy of the master template:

```
mcp__claude_ai_Google_Drive__copy_file
- fileId: "1uhcYuJ7i3V0R1-jA-u0y1xRGMeVFTXwixjWNX3zcTYk"  (master template)
- title: "Access Checklist Template"
- parentId: "{client_work_folder_id}"
```

Save the new document ID:
```
agency_update { "google_config": { "access_checklist_id": "{new_doc_id}" } }
```

Then tell the user:

> "I've created your Access Checklist template: [link]
>
> **Important:** Please open this document and replace `[ENTER EMAIL]` with your agency email (e.g., access@youragency.com). This is the email clients will grant access to.
>
> Once you've updated it, we can continue."

Wait for confirmation before proceeding.

**If config exists, confirm:**

> "I'll use your existing settings:
> - Drive folder: [folder_id]
> - Scheduling link: [calendar_link]
>
> Continue with these, or would you like to update them?"

### Step 3: Create Local Client Record

Use the `clients_create` MCP tool:

```json
{
  "lead_id": "{lead-uuid}",
  "company_name": "Acme Corp",
  "contact_name": "John Smith",
  "email": "john@acme.com",
  "website": "https://acme.com",
  "service_type": "seo_sprint",
  "monthly_retainer": 4500,
  "contract_start_date": "2024-04-01"
}
```

This will:
- Create the client with `onboarding` status
- Set `onboarded_at` timestamp
- Link to the original lead
- Create local client folder in `clients/{client-slug}/`

### Step 4: Create Google Drive Folder Structure

**Skip this step if user chose to skip Google Drive in Step 2.**

Use Claude's native Google Drive MCP tool:

**Create client folder:**
```
mcp__claude_ai_Google_Drive__create_file
- name: "{Company Name}"
- mimeType: "application/vnd.google-apps.folder"
- parent: "{client_work_folder_id}"
```

Capture the returned folder ID.

**Create Client Assets subfolder:**
```
mcp__claude_ai_Google_Drive__create_file
- name: "Client Assets"
- mimeType: "application/vnd.google-apps.folder"
- parent: "{new_client_folder_id}"
```

**Copy templates (if configured):**

If `google_config.onboarding_questionnaire_id` exists:
```
mcp__claude_ai_Google_Drive__copy_file
- fileId: "{onboarding_questionnaire_id}"
- name: "{Company Name} - Onboarding Questionnaire"
- parent: "{new_client_folder_id}"
```

If `google_config.access_checklist_id` exists:

**First, validate the template has been customized:**
```
mcp__claude_ai_Google_Drive__read_file_content
- fileId: "{access_checklist_id}"
```

Check if the content still contains `[ENTER EMAIL]`:

If placeholder still exists, STOP and warn:
> "Your Access Checklist template still has the placeholder `[ENTER EMAIL]` in it.
>
> Please open the template and replace it with your agency email before we send this to a client: [template_link]
>
> Let me know when you've updated it."

Wait for confirmation, then re-validate.

If template is customized (no placeholder), copy it:
```
mcp__claude_ai_Google_Drive__copy_file
- fileId: "{access_checklist_id}"
- name: "{Company Name} - Access Checklist"
- parent: "{new_client_folder_id}"
```

Confirm to user:

> "Created Google Drive folder for {Company Name}:
> - Client folder: [link]
> - Assets subfolder: [link]
> - Onboarding Questionnaire: [link] (if copied)
> - Access Checklist: [link] (if copied)
>
> **Action needed:** Please share the client folder with {client_email}:
> 1. Click the folder link above
> 2. Click 'Share' → Add {client_email} as Editor
>
> This lets the client access their folder and upload assets."

### Step 5: Update Client Record with Drive Folder

**Skip if no Drive folder was created.**

Update the client with Drive folder URLs:

```
clients_update {
  "id": "{client-uuid}",
  "drive_folder": "https://drive.google.com/drive/folders/{folder_id}",
  "custom_fields": {
    "assets_folder": "https://drive.google.com/drive/folders/{assets_folder_id}",
    "access_checklist_doc": "https://docs.google.com/document/d/{checklist_doc_id}/edit"
  }
}
```

### Step 6: Generate Onboarding Email Draft

Read the email template:
```
Read templates/emails/onboarding-email-template.md
```

Get agency profile for merge fields:
```
agency_get {}
```

Get owner info:
```
team_list { "role": "owner" }
```

**Resolve branding colors (with fallback):**

If `agency.branding` is missing or incomplete, use defaults:

- `primary_color` → `agency.branding.primary_color` OR `#2563eb`
- `secondary_color` → `agency.branding.secondary_color` OR `#1e40af`

Do not throw or block on missing branding — fall back silently.

**Fill in merge fields:**

- `{{agency.name}}` → Agency name
- `{{agency.email}}` → Agency email
- `{{agency.website}}` → Agency website URL
- `{{client.company_name}}` → Client company
- `{{client.contact_name}}` → Contact first name
- `{{owner.name}}` → Owner's name
- `{{owner.title}}` → Owner's title (e.g., "Managing Partner")
- `{{drive_folder_link}}` → Link to client folder (or remove section if skipped)
- `{{assets_folder_link}}` → Link to assets subfolder (or remove if skipped)
- `{{access_checklist_link}}` → Link to access checklist (or remove if missing)
- `{{scheduling_link}}` → `agency.calendar_link` (or remove section if missing)
- `{{primary_color}}` → Resolved per branding fallback above
- `{{secondary_color}}` → Resolved per branding fallback above

**Formatting requirements (do not deviate):**

- All body text MUST render at a uniform 16px font size.
- No h1/h2 visual hierarchy. Section headers are bolded inline only — do not increase their font size.
- No "Welcome to {{agency.name}}!" salutation. Open with `Hi {{client.contact_name}},` then dive into the body.
- Opening line MUST read exactly: "We're excited to kick off your campaign." (Do NOT substitute service-specific phrasing like "SEO Sprint engagement".)
- Use inline links with `{{primary_color}}` — no CTA buttons with background fills.

**Create Gmail draft (HTML formatted):**

Use Claude's native Gmail MCP tool with `htmlBody`:

```
mcp__claude_ai_Gmail__create_draft
- to: ["{client_email}"]
- subject: "{Agency Name} — Let's Get Started!"
- htmlBody: "{styled_html_email}"
```

Confirm to user:

> "Created email draft in Gmail. Please review before sending:
> - To: {client_email}
> - Subject: {Agency Name} — Let's Get Started!
>
> The draft includes:
> - Drive folder link (if configured)
> - Access checklist
> - Scheduling link for kickoff call (if configured)"

### Step 7: Create Project + Onboarding Sprint

**Create project:**

```json
{
  "client_id": "{client-uuid}",
  "name": "SEO Sprint 2024",
  "project_type": "seo_sprint",
  "primary_goal": "Increase organic traffic and local visibility",
  "start_date": "2024-04-01",
  "target_end_date": "2024-09-30"
}
```

**Create onboarding sprint (3 days):**

```json
{
  "project_id": "{project-uuid}",
  "sprint_number": 1,
  "sprint_type": "onboarding",
  "scheduled_start": "2024-04-01",
  "scheduled_end": "2024-04-03",
  "status": "active"
}
```

### Step 8: Create Onboarding Deliverables

Create 3 deliverables for the onboarding sprint:

**1. Access Collection (Day 1):**
```json
{
  "sprint_id": "{sprint-uuid}",
  "name": "Access Collection",
  "description": "Collect GA4, GSC, CMS, and other platform access from client",
  "deliverable_type": "setup",
  "due_date": "{start_date + 1 day}"
}
```

**2. Kickoff Call (Day 2):**
```json
{
  "sprint_id": "{sprint-uuid}",
  "name": "Kickoff Strategy Call",
  "description": "Initial strategy discussion - review goals, timeline, and priorities",
  "deliverable_type": "meeting",
  "due_date": "{start_date + 2 days}"
}
```

**3. Project Timeline Document (Day 3):**
```json
{
  "sprint_id": "{sprint-uuid}",
  "name": "Project Timeline Document",
  "description": "Create project timeline with sprint breakdown and key milestones",
  "deliverable_type": "document",
  "due_date": "{start_date + 3 days}"
}
```

### Step 9: Create Follow-up Reminders

Use `followups_create` for key touchpoints. If the client has a `lead_id`, use that; otherwise use `client_id`:

**Day 1: Access checklist follow-up**
```json
{
  "lead_id": "{lead-uuid}",  // or "client_id": "{client-uuid}" if no lead
  "due_date": "{start_date + 1 day}",
  "follow_up_type": "email",
  "note": "Follow up on access checklist - GA4, GSC, CMS"
}
```

**Day 3: Kickoff call (urgent)**
```json
{
  "lead_id": "{lead-uuid}",  // or "client_id": "{client-uuid}" if no lead
  "due_date": "{start_date + 3 days}",
  "follow_up_type": "meeting",
  "note": "Kickoff call with {contact_name}"
}
```

**Day 7: Week 1 check-in**
```json
{
  "lead_id": "{lead-uuid}",  // or "client_id": "{client-uuid}" if no lead
  "due_date": "{start_date + 7 days}",
  "follow_up_type": "call",
  "note": "Week 1 check-in - confirm access, answer questions"
}
```

## Summary Output

After completing all steps, summarize:

> "Client onboarding complete for {Company Name}!
>
> **Google Drive:** (if configured)
> - Client folder: [link]
> - Assets folder: [link]
> - Questionnaire: [link]
>
> **Email:**
> - Draft ready in Gmail - review and send
>
> **Project:**
> - {Project Name} created
> - Onboarding sprint active ({start_date} - {end_date})
> - 3 deliverables scheduled
>
> **Follow-ups scheduled:**
> - Day 1: Access checklist follow-up
> - Day 3: Kickoff call
> - Day 7: Week 1 check-in
>
> **Next steps:**
> 1. Review and send the onboarding email
> 2. Wait for client to complete access checklist
> 3. Run `/bpt-website-quality-audit` after receiving access
> 4. Complete kickoff call
> 5. Run `/bpt-project-plan` to create work sprints based on WQA findings"

## MCP Tools Used

| Tool | Purpose |
|------|---------|
| `leads_get` | Retrieve lead information |
| `agency_get` | Get agency profile and Google config |
| `agency_update` | Save Google config (google_config parameter) |
| `clients_create` | Create client record |
| `clients_update` | Update client with Drive folder URL |
| `projects_create` | Create first project |
| `sprints_create` | Create onboarding sprint |
| `deliverables_create` | Create deliverables |
| `followups_create` | Create follow-up tasks (accepts lead_id or client_id) |
| `team_list` | Get owner info for email |
| `mcp__claude_ai_Google_Drive__create_file` | Create Drive folders |
| `mcp__claude_ai_Google_Drive__copy_file` | Copy template documents |
| `mcp__claude_ai_Google_Drive__read_file_content` | Validate template is customized |
| `mcp__claude_ai_Gmail__create_draft` | Create HTML email draft |

## Error Handling

### Google MCP Tools Not Available
If Google Drive or Gmail MCP tools aren't connected:
> "I can't access Google Drive/Gmail. To enable this:
>
> **Claude Desktop:** Go to Settings → Integrations and enable Google Drive and Gmail
>
> **Claude Code:** Add the Google Drive and Gmail MCP servers to your `.mcp.json` config
>
> I can still create the local client record, project, and follow-ups without Google integration. Want to continue without Drive/Gmail, or set those up first?"

### Template Not Found
If `templates/emails/onboarding-email-template.md` is somehow missing, fall back to composing the email inline using the same merge fields and formatting requirements specified in Step 6.

### Manual Step Required: Share Folder with Client
The Google Drive MCP cannot share folders (no set_permissions tool). After creating the folder:

> "**Manual step:** Please share the client folder with {client_email}:
> 1. Open the folder: [link]
> 2. Click 'Share' button
> 3. Add {client_email} as Editor
>
> This gives the client access to upload assets and view documents."

## Decision Points

**Lead already has client record:**
- Check `data/clients.json` for existing client linked to lead
- If exists, offer to update rather than create new

**Different service type:**
- Adjust project type and sprint templates based on service
- SEO Sprint → onboarding, foundational, content, link, reporting
- Meta Ads → onboarding, account_setup, audience_building, creative_production, campaign_launch

**Client provides access during call:**
- Mark Access Collection deliverable as complete
- Skip Day 1 follow-up
