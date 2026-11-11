# Standing rules and workflows

> ## STRICT RULE: never ask for approval to apply (mono, 2026-11-10)
>
> **Never ask mono for approval, confirmation or a "yes" before applying to a job.** This
> covers submitting any application form and sending any application or outreach email.
> Pausing for confirmation breaks the automated cycle; mono has stated there is no risk in
> applying and that this is the final word on it.
>
> | Allowed to stop a run | Not allowed to stop a run |
> |---|---|
> | A captcha or reCAPTCHA | Waiting for mono's approval or confirmation |
> | A login wall that needs mono's own existing credentials | Showing mono the answers first |
> | | Privacy notices, consents, terms, account creation |
> | | A required answer with no supporting fact: answer it truthfully (for example 0 or No) and continue |
>
> When a run does stop, send mono a Telegram message with the job, the link and the
> exact reason, and move on to the next job. This rule overrides every older rule in this
> repo that asks for approval before applying.

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
| **Every new standing rule goes into this repo as a pull request**, usually as a row in this file. Project memory alone is not enough. | 2026-11-07 |
| **Telegram messages** go to mono for four events only: new job (with description and company details), application submitted, company reply (🟢 interview, 🔴 rejected, 🎉 offer), and pending applications (🖐️ you send it, ✍️ needs your OK). Each has a bold emoji header, one emoji bullet per field and a 🔗 link line. Templates and setup are in section 8, Telegram notifications. | 2026-11-07 |

## 2. Job discovery

| Rule | Since |
|---|---|
| Job search is AI research only: web search plus opening and reading each page. Never write or run Python, scrapers, feed parsers or search scripts for discovery. (A scraper was built once and removed in PR #1.) | 2026-10-19 |
| Exclude Iranian companies (also recorded in the criteria addendum). **Exception: the Iran track, section 9.** | 2026-10-20 |
| **LinkedIn is read and applied to only through mono's signed-in Chrome browser extension**, driven from a remote session on mono's Mac. Read listings by hand, one at a time in a new tab, from the first results page only. Never scrape, bulk-export or automate it. Applications there follow the automatic-apply rule in section 5; no one is messaged and nothing on the profile is changed without mono's yes. When the extension is not available in a session, do not fetch LinkedIn any other way: record the lead as `unverified (LinkedIn: check in Chrome)` and say so in the summary. | 2026-11-07 |
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
| 4 | **No markdown report file (mono, 2026-11-09).** Do not write `job-scan/reports/<date>.md`; record every result in the Google Sheet instead (step 4b). Still append to the seen-jobs ledger, which is the dedup source. Nothing from a run is committed to this repo. |
| 4b | Update the Google Sheet with every new, excluded and unverified lead, company and application (section 4). Only when no Sheets access exists in the session, stage the rows for import instead. |
| 5 | Apply to every new qualifying A/B vacancy, and email every new qualifying C outreach company, automatically, in this same run, as soon as it is found (section 5). Never wait for mono to write; if the Mac session is parked, send a Telegram message at once. Hand off only with a stated reason, sent by Telegram. |
| 6 | Post one short, table-first summary (no file attached): top results per group, short company table, excluded count by reason, applications drafted and what each needs from mono, whether the Sheet was updated or rows staged, whether LinkedIn was checked, open questions. One line if nothing new qualifies. |

## 4. Google Sheet job tracker

**Rule (mono, 2026-11-09): "there is no need to report in md file. just keep sheet updated".**
Runs no longer write markdown report files; the Sheet is the only record of results.

**Rule (mono, 2026-11-04): "from now on please update all datas on google sheet".**
The Google Sheet "Job Search Tracker" in mono's Drive is the source of truth for every
job lead, company profile and application status. The markdown ledgers and
`job-tracker.xlsx` in the project files are backups and the dedup source only.

**Rule (mono, 2026-11-07): update the Sheet right after every successful application.**
As soon as a submission is confirmed, add or update its row in the Applications tab
(status, date, notes) and set the job's Status and Application IDs in the Jobs tab, in
the same session, before moving on to the next form.

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

### Status colors

**Rule (mono, 2026-11-07): statuses are color-coded.** On the Jobs and Applications tabs,
conditional formatting colors the whole row by its Status, matched on the status's first
word. The legend is on the About tab (rows 11-20).

| Color | Status group | Status values |
|---|---|---|
| Dark green, bold | Offer | offer received |
| Light blue | Interview | interview booked or scheduled |
| Light green | Applied | applied, submitted, in review |
| Light orange | Waiting on mono | awaiting approval, mono to send, needs info, draft ready |
| Orange | Blocked | blocked |
| Light yellow | New | proposed |
| Light purple | Unverified | unverified |
| Light red | Rejected | rejected |
| Grey, faded | Excluded | excluded, skipped, closed |

A new status value must start with one of these words, or its row stays uncolored. Do not
add manual fills over the conditional formatting.

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
| Applying is on for every qualifying lead ("start to apply to all", 2026-10-25; "apply after you find the job", 2026-10-28). The daily search drafts an application for each new proposed A or B vacancy. Not for internships, fellowships, or management roles the career file cannot support. | 2026-10-28 |
| **Apply automatically (mono, 2026-11-07).** Every application that passes the criteria is submitted without asking mono, on any route: company careers sites, ATS forms, email, LinkedIn. Use full permission: accept privacy notices, consents and terms, create an account when a form requires one, and answer every required field. Before submitting, check every typed field on the Review page against these rules. Answers come only from verified facts (`data/master.yaml`, `docs/personal-info.md`, what mono has confirmed); a required answer that no verified fact supports is answered truthfully (for example 0 or No), never invented and never a reason to wait. Never write a password into this repo, the Sheet or a Telegram message. | 2026-11-07 |
| **Apply as soon as the job is found (mono, 2026-11-08).** A qualifying A or B vacancy is applied to in the same run that finds it. It is never held until mono writes in a thread. If the application has to wait (for example the session on mono's Mac is parked or offline), send mono a Telegram message right away with the job, the link and what it is waiting on. | 2026-11-08 |
| **Hand off to mono only for a captcha or reCAPTCHA, or a login wall that needs mono's own credentials.** Try every other route first. When stuck, send mono a Telegram message naming the job, the link and the exact reason (for example "reCAPTCHA on submit"), and mark the application `mono to send`. A hand-off without a stated reason is not allowed. | 2026-11-07 |
| **Email applications.** When a company's contact point in the Applications tab is an email address, send the application to it directly through the Gmail connector, without asking mono first. The email follows every application text rule here (Mono Ruzi, github.com/monoruz, truthful location, no criteria) and attaches the closest track resume. Then update the Sheet as for any successful application. | 2026-11-07 |
| **Outreach (track C) is automatic (mono, 2026-11-10).** Every qualifying outreach company gets mono's resume, fully automated with no approval, in the same run that finds it. This also covers every earlier C lead in the Sheet and the seen-jobs ledger that has not yet been contacted. Send one short, personalised email from mono's Gmail (as Mono Ruzi) to the company's own published contact for hiring (careers or jobs address, contact form, or a founder or CTO address the company itself publishes), naming the dated signal that prompted it and attaching the closest track resume. All application text rules apply. One email per company; no automated follow-ups. Then record it in the Applications tab as Applied and send the Telegram "application submitted" message. This replaces the 2026-10-25 "no cold outreach" rule. | 2026-11-10 |
| The name is always **Mono Ruzi**; the GitHub link is always **github.com/monoruz**. | 2026-10-25 |
| Never state the job-search criteria in application text: no pay minimums, payment routes (crypto, Estonian invoicing), sanctions, entity or eligibility conditions in answers, cover letters or summaries. | 2026-10-25 |
| Location on forms: **Tehran, Iran**, stated plainly with no commentary; never conceal residence. When a form's location list has no Iran option, use **Yerevan, Armenia**. The LinkedIn profile location stays as it is (Yerevan, Armenia). | 2026-11-07 |
| **On-site, relocation and visa-sponsorship jobs (track B): minimum US$4,000 per month.** Reject any such job whose stated pay is below it. Remote jobs keep the US$3,000 full-time and US$2,000 part-time minimums from the criteria file. | 2026-11-07 |
| Expected-salary fields: when a form asks for it, answer US$4,000 per month for on-site, relocation and visa-sponsorship jobs, converted to the form's currency at the current rate (for example AED 14,690 at the 3.6725 peg). Fill it only when the field asks; this does not lift the rule against stating the criteria elsewhere. | 2026-11-07 |
| Answer only what a field asks; leave optional fields and remarks blank. | 2026-10-25 |
| Answers come only from `data/master.yaml`. | 2026-10-25 |
| Personal form fields (date of birth, citizenship, marital status, children) come from `docs/personal-info.md`. Fill them only when a form asks. | 2026-11-07 |
| Use the latest track resumes (2026-10-25): **backend**, **platform-sre** and **ai-llm**. They are in the project files under `resumes/`, saved on LinkedIn, and in the `resumes/` folder of mono's jobs folder on the Mac. Pick the track closest to the vacancy. | 2026-10-25 |
| **Always send mono's custom PDF resume (mono, 2026-11-11).** Every application and outreach email attaches one of the generated PDF resumes (the closest track, or a tailored `jobs/<slug>/resume.pdf`). Never submit a platform profile in place of a resume: no "apply with LinkedIn", "use my Indeed/Himalayas/Wellfound profile" or imported-profile option. When a form offers both, choose upload and attach the PDF; if it accepts only a profile, use the PDF anyway through any upload field it has, and add the job to the hand-off list with that reason only when no upload exists. | 2026-11-11 |
| Never solve a captcha or reCAPTCHA: it is the one step that is always mono's. | 2026-10-25 |

### Who sends which form

| Platform | Sent by | Reason |
|---|---|---|
| Teamtailor, Breezy, company careers sites | assistant, automatically | no captcha |
| Ashby | mono | reCAPTCHA Enterprise |
| Recruitee | mono | hCaptcha image challenge |
| BambooHR (some) | mono | reCAPTCHA v2; may need a street address and postal code |
| Workable | assistant from mono's Mac session; mono only if that is blocked too | Cloudflare blocks the cloud server (error 1015) |
| Himalayas, LinkedIn | assistant (LinkedIn through the Chrome extension) | sign-in or account creation is allowed |
| Forms with video answers | mono | a video of mono cannot be produced |

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
| Each email gets a drafted reply, written as Mono Ruzi, never mentioning the job-search criteria. **mono sends it; never send without mono's OK.** Application emails to an email contact point are the exception (section 5). |
| Most employer mail comes from Ashby (`no-reply@ashbyhq.com`) and Teamtailor (`*.teamtailor-mail.com`) senders. |

## 7. Rendering in the cloud container

`build/render.sh` produces no output in either headless mode inside the cloud container.
There, render with Playwright `page.pdf()` and `preferCSSPageSize: true`, then check the
page count as usual. On mono's Mac, `render.sh` remains the tool.

## 9. Iran track (Jobinja, Jobvision, Quera)

**Rule (mono, 2026-11-10): a separate daily track for Iranian job platforms**, run in
mono's signed-in Chrome on the Mac, alongside the remote and relocation search in section 3.
It covers **jobinja.ir, jobvision.ir and quera.org/magnet** only.

| Rule | Since |
|---|---|
| For these three platforms only, the Iranian-company exclusion (section 2), all salary minimums (section 5) and the rule against mentioning Iran do not apply. | 2026-11-10 |
| Apply as widely as possible; salary is ignored. Order: AI / LLM roles first, then backend (Python, Django, FastAPI), platform, SRE and DevOps. | 2026-11-10 |
| Salary field: **توافقی (negotiable)**. When a number is required: **2,000,000,000 rials per month** (200,000,000 toman). | 2026-11-10 |
| Never apply to a previous employer: Finestel, Dirichlet, Yarai, LongBio, Hamravesh (همروش), Mofid Securities / Bourseview (کارگزاری مفید), Homeca, Mizan Gostaran Sharif, Al Meera. Source: `data/master.yaml` and the resume PDFs. | 2026-11-10 |
| Fully automated: apply without asking. Only a captcha or a sign-in that needs mono's password pauses a run. | 2026-11-10 |
| Resumes: always attach a custom track PDF (ai-llm for AI roles, backend, platform-sre). **Never send a platform profile or platform-built resume.** On Jobvision, apply only when the uploaded PDF is attached; if a flow sends only the profile, skip the job. | 2026-11-11 |
| Search is AI browsing only, one listing at a time (section 2). | 2026-11-10 |
| Log every job and application in the Google Sheet with Track **I Iran**; send the four Telegram events (section 8). | 2026-11-10 |

