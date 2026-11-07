# Standing rules and workflows

Rules mono has given during the job search that were not yet written down in this repo.
They carry the same authority as `docs/job-search-criteria.md`; where a rule here and a
default procedure differ, the rule wins.

| Area | Where else it is covered |
|---|---|
| Job-search constraints, labels, ranking | `docs/job-search-criteria.md` |
| Company sources and ranking signals | `docs/company-sources.md` |
| Research procedure, ledger, daily dedup | `.claude/skills/job-research/SKILL.md` |
| Everything below | this file only |

## 1. General

| Rule | Since |
|---|---|
| Never mention the AI assistant in commit messages, PR text or code. | standing |
| Prefer tables and visual layouts over plain prose in reports and replies. | standing |
| No email address, password, token or other secret is ever committed to this repo. | standing |

## 2. Job discovery

| Rule | Since |
|---|---|
| Job search is AI research only: web search plus opening and reading each page. Never write or run Python, scrapers, feed parsers or search scripts for discovery. (A scraper was built once and removed in PR #1.) | 2026-10-19 |
| Exclude Iranian companies (also recorded in the criteria addendum). | 2026-10-20 |
| **LinkedIn leads are read only through mono's signed-in Chrome browser extension**, one listing at a time, in a new tab. Never scrape, bulk-export, message anyone, apply or change anything on LinkedIn. When the extension tools are not available in a session, do not fetch LinkedIn any other way: record the lead as `unverified (LinkedIn: check in Chrome)` and say so in the summary. | 2026-11-07 |
| Always confirm an HN "Who is hiring?" claim on the employer's own page (a post once offered a UK visa while the employer page required UK residence). | 2026-11-03 |

### Sources that worked

- The monthly HN "Who is hiring?" thread (posted on the first weekday of the month by
  user `whoishiring`) was the best source in early November. Read it through the
  hn.algolia.com search API, for example `tags=comment,story_<id>&query=visa`.

## 3. Daily scheduled search

A scheduled task runs every day at 08:43 Asia/Tehran and posts into the
"Daily job opportunity search" thread. Its steps, in order:

| Step | What it does |
|---|---|
| 0 | Pull `main`; re-read the job-research skill, `docs/job-search-criteria.md` (with addendum), `docs/company-sources.md`, `data/master.yaml`, and this file. Run date = today, 7-day freshness cut-off. |
| 1 | Read the seen-jobs ledger first; never re-propose a key or URL in it (see the skill's "Daily run and de-duplication"). |
| 2 | Run tracks A (remote), B (sponsored relocation), C (outreach) in parallel. **Each track gets at most 30 page fetches** (the fetch budget is about 100 pages/hour shared by the whole session) and starts by resolving the previous day's `unverified` rows for its track. |
| 2b | LinkedIn leads through the Chrome extension only (section 2). |
| 3 | Profile every proposed company (size, hiring activity, headcount growth, growth status, funding and budget, leadership changes, HQ and entity, reputation, comments). Each figure has a link and date, otherwise "not found". |
| 4 | Write the report to the project files (`job-scan/reports/<date>.md`) and append to the ledger. Reports are **never committed to this repo** (mono reverted one, PR #2). |
| 4b | Update the Google Sheet, or stage rows for import (section 4). |
| 5 | Draft applications for new A/B vacancies (section 5). |
| 6 | Post one short, table-first summary: top results per group, short company table, excluded count by reason, applications drafted and what each needs from mono, whether the Sheet was updated or rows staged, whether LinkedIn was checked, open questions. One line if nothing new qualifies. |

## 4. Google Sheet job tracker

**Rule (mono, 2026-11-04): "from now on please update all datas on google sheet".**
The Google Sheet "Job Search Tracker" in mono's Drive is the source of truth for every
job lead, company profile and application status. The markdown ledgers and
`job-tracker.xlsx` in the project files are backups and the dedup source only.

### Tabs

| Tab | Columns |
|---|---|
| Jobs | Job ID (`J0001`…), Company ID, Company *(formula)*, Role, Track (A Remote / B Relocation / C Outreach), Status (proposed / excluded / unverified), Label, Fit, First seen, Last seen, Posted, Location, Type, Pay, Visa sponsorship, Iran work, Payment route, Hiring entity, Language, Outreach angle, Listing URL, Ledger note, Daily reports, Application IDs, Ledger key: **25 columns** |
| Companies | Company ID (= website domain, same as the ledger key domain), Company, Website, three count columns *(formula)*, then Size, Hiring activity, Headcount growth, Growth status, Funding and budget, Leadership changes, HQ and entity, Reputation, Comments, First profiled, Last profiled |
| Applications | Application ID (`APP001`…), Company ID, Company *(formula)*, Job ID, Role, ledger #, Status, Notes |
| About | Legend |

### Writing rules

| Rule | Why |
|---|---|
| Leave the formula columns empty when appending: `Jobs!C`, `Applications!C`, `Companies!D:F`. | Each is one ARRAYFORMULA in the header cell; a value breaks it with `#REF`. |
| Add a new company to Companies before any job that references it; reuse an existing Company ID (domain). | Lookups key on Company ID. |
| Append below the last row; IDs continue the sequence. | Stable IDs across tabs. |
| Prefix date-like or range-like text (`10-23`, `11-50`, `+16%`) with an apostrophe. | Sheets parses typed values. |
| Match updates to existing rows on Ledger key (column Y). | Row positions shift. |
| Verify a bulk import with a temporary COUNTIF / SUMPRODUCT(ROW) checksum in a spare About cell, then clear it. | A hand-copy slip once shifted rows by one; the checksum caught it. |

### Staging route

The daily search session has no Sheets access. It writes the same rows, in the Sheet's
column order, to `job-scan/sheet-staging/<date>.md` in the project files, and a session
that has the Sheets connector imports them.

| Staging section | Contents |
|---|---|
| Companies to add | **Every** new Company ID in the day's jobs (name + domain stub is enough), not only the profiled ones |
| Companies to update | Profile fields by Company ID |
| Jobs to append | Next Job IDs; **every row has all 25 cells** |
| Jobs to update | Last seen / Status changes, keyed by Ledger key |
| Applications to append | Next Application IDs |

## 5. Applications

| Rule | Since |
|---|---|
| Applying is on for every qualifying lead ("start to apply to all", 2026-10-25; "apply after you find the job", 2026-10-28). The daily search drafts an application for each new proposed A or B vacancy. Not for track C outreach, internships, fellowships, or management roles the career file cannot support. | 2026-10-28 |
| **Nothing is submitted until mono approves that application's answers.** A submission cannot be undone. | 2026-10-25 |
| No cold outreach to companies unless mono asks for it. | 2026-10-25 |
| The name is always **Mono Ruzi**; the GitHub link is always **github.com/monoruz**. | 2026-10-25 |
| Never state the job-search criteria in application text: no pay minimums, payment routes (crypto, Estonian invoicing), sanctions, entity or eligibility conditions in answers, cover letters or summaries. | 2026-10-25 |
| Location is answered truthfully ("Tehran, Iran") with no commentary; never conceal residence. | 2026-10-25 |
| Answer only what a field asks; leave optional fields and remarks blank. | 2026-10-25 |
| Answers come only from `data/master.yaml`; use the existing track resumes (backend, platform/SRE, AI/LLM infrastructure) in the project files. | 2026-10-25 |
| Never solve a captcha. Forms behind a captcha, a sign-in, a video answer, or a cloud block go to mono to send. | 2026-10-25 |

### Who sends which form

| Platform | Sent by | Reason |
|---|---|---|
| Teamtailor, Breezy | assistant, after approval | no captcha |
| Ashby | mono | reCAPTCHA Enterprise |
| Recruitee | mono | hCaptcha image challenge |
| BambooHR (some) | mono | reCAPTCHA v2; may need a street address and postal code |
| Workable | mono | Cloudflare blocks the cloud server (error 1015) |
| Himalayas, LinkedIn | mono | sign-in |
| Forms with video answers | mono | video |

### Files (project files, not this repo)

| File | Purpose |
|---|---|
| `applications/index.md` | Ledger: one row per lead, status `awaiting approval`, `mono to send`, submitted, dropped |
| `applications/drafts.md` | Draft answers per application |
| `applications/send-yourself.md` | Packs for the forms mono sends |
| `resumes/` | General track resumes and PDFs |

Re-read `index.md` and `drafts.md` just before each write; other sessions edit them.

## 6. Employer emails

| Rule |
|---|
| Employer emails (replies, interviews, rejections, offers) update the Applications tab: Status, Notes, date and next step; and Jobs or Companies when the email adds facts. |
| Each email gets a drafted reply, written as Mono Ruzi, never mentioning the job-search criteria. **mono sends it; never send without mono's OK.** |
| Most employer mail comes from Ashby (`no-reply@ashbyhq.com`) and Teamtailor (`*.teamtailor-mail.com`) senders. |

## 7. Rendering in the cloud container

`build/render.sh` produces no output in either headless mode inside the cloud container.
There, render with Playwright `page.pdf()` and `preferCSSPageSize: true`, then check the
page count as usual. On mono's Mac, `render.sh` remains the tool.
