---
name: job-research
description: Deep-research job and company discovery for mono against docs/job-search-criteria.md and data/master.yaml. Use when asked to find jobs, search for roles, research companies to apply to, or refresh the weekly job scan.
---

# Job research

Find paid work mono can realistically take, by researching companies and vacancies on
the live web. This is research, not scraping: every result is opened, read and
checked against the criteria before it is reported.

## Sources of truth

| File | Governs |
|---|---|
| `docs/job-search-criteria.md` | Every constraint, label, ranking rule and output field. Re-read it at the start of each run; it overrides anything in this file. |
| `data/master.yaml` | Technical experience. Fit explanations cite role ids and bullets from it. Never claim a skill that is not in it. |
| `docs/company-sources.md` | Where to find companies (funding, hiring, growth and tech sources), domain-based de-duplication, and the ranking signals used within the criteria's order. |

## Preflight: the web must be readable

Run one page fetch (any official careers page) before starting. Search results alone
cannot verify a publication date, a location restriction, pay or a hiring entity, so
if pages cannot be opened, stop and say so. Do not produce a search-snippet report in
place of verified results.

## Procedure

1. **Set the run date** (today, UTC) and the freshness cut-off from the criteria file.
2. **Candidate discovery, three tracks in parallel** (one subagent each when available):
   - **A. Remote vacancies.** Search direct ATS boards first, since they carry the
     original listing and its date: `site:jobs.ashbyhq.com`, `site:boards.greenhouse.io`,
     `site:jobs.lever.co`, `site:apply.workable.com`, `site:jobs.personio.de`, combined
     with role words (backend, Python, platform, SRE, DevOps, AI/LLM, full-stack, founding
     engineer, technical SEO) and `remote`. Then remote boards (RemoteOK, We Work
     Remotely, Remotive, Himalayas, Working Nomads, web3.career, CryptoJobsList, the
     current HN "Who is hiring?" thread). Also search for the payment-route evidence the
     criteria prioritise: "paid in USDC/USDT", "stablecoin salary", "B2B contract",
     "contractors worldwide", and explicit Iran mentions.
   - **B. Sponsored relocation.** Vacancies that explicitly offer visa sponsorship for
     the vacancy itself (for example EU Blue Card, Dutch highly-skilled migrant, UK
     Skilled Worker, UAE employment visa). Generic "relocation support" does not count.
   - **C. Outreach companies.** Companies with a sourced reason to approach (expansion,
     a documented technical need matching master.yaml, explicit contractor/crypto/B2B
     policy, confirmed Iran-based engineers) but no qualifying recent vacancy. Find them
     through the funding, accelerator and growth sources in `docs/company-sources.md`,
     and rank them with its signals (new funding, open senior roles, headcount growth,
     leadership changes, stack match).
3. **Verify each candidate by opening it.** For every vacancy, open the listing (prefer
   the company's own page over a board repost) and record:
   - publication date as stated on the page, with where it was read; no date means
     excluded from A/B, never estimated;
   - location or residency restrictions and any sanctions/OFAC clause;
   - pay as written, converted to monthly only when the unit is explicit, and checked
     against the full-time or part-time minimum (FTE salary is not part-time pay);
   - employment type (full-time, part-time, contract).
4. **Research each surviving company** (the "deep" part):
   - actual hiring entity and its country: legal notice/imprint, terms of service,
     contract language, job-board entity field, national company registry. A foreign
     office address alone is not an entity. **Exclude Iranian companies** (entity
     registered or headquartered in Iran, or main operations in Iran, including through
     a foreign shell), decided from these sources only, never from people's names or
     nationality;
   - contractor and payment policy: crypto pay, third-party invoicing, B2B; record each
     separately with its source;
   - Iran-based engineers: only explicit public statements (company pages, posts by the
     company). Never infer location or nationality from names, photos or language;
   - hiring urgency and growth: number of open engineering roles, new teams, funding or
     expansion announcements, each with source and date; "actively hiring" is not
     "growing";
   - reputation and payment reliability: Glassdoor, Blind, Reddit, Trustpilot, HN,
     contractor forums. Separate isolated complaints from repeated patterns, and note
     the absence of complaints as unproven, not clean.
5. **Apply the criteria**: remove confirmed hard-requirement failures, label the rest
   (Confirmed-compatible / Conditional / Low-priority/unverified), and rank in the
   criteria's order. Fewer verified results beat a padded list.

## Output

Write `research/<YYYY-MM-DD>/report.md` with:

- one summary table per group (A, B, C): label, company + website, role or outreach
  angle, link, posted date, type, pay vs minimum, Iran eligibility, payment route, fit;
- below the tables, one short section per result with every field the criteria's
  REQUIRED RESULTS list asks for, each claim linked to its source and marked as a
  company statement, recruiter statement or third-party report;
- a **Company profiles** table, one row per proposed company, with the attributes in
  `docs/company-sources.md` § Company profile (rule from mono, 2026-10-21);
- an "Excluded" table listing what was cut and the failing requirement, so the same
  leads are not re-researched next run.

For a daily scheduled run, see the next section for where the report goes. For an ad hoc
run, commit the report on the working branch. In chat, report the group tables (top results
only), the count of excluded leads by reason, and the open questions mono must answer
or ask the company. Keep the long detail in the file.

## Daily run and de-duplication

A scheduled task runs this procedure once a day. mono must never be shown the same job
twice, so every run works against a persistent ledger.

| File | Purpose |
|---|---|
| `/mnt/project-files/job-scan/seen-jobs.md` | Ledger of every lead proposed or excluded, with its key, status and URL. Its header defines the key and the matching rules. |
| `/mnt/project-files/job-scan/reports/<YYYY-MM-DD>.md` | The full report for that run (same structure as Output below). |

1. **Read the ledger first.** Before researching, load every key and URL.
2. **Skip repeats during discovery**, not only at the end: a candidate whose key or URL
   is in the ledger, or that is the same role at the same company re-listed under another
   city or board, is not re-verified or re-reported. Excluded leads stay excluded unless
   a new listing with a new URL and a new publication date appears.
3. **Outreach companies (C)** already proposed may return only as an *update*, when a
   new dated signal exists, and the update names what changed.
4. **Profile every proposed company** while researching it: size, hiring and headcount
   growth, funding and budget signals, and the other attributes listed in
   `docs/company-sources.md` § Company profile. Each daily report carries the
   Company profiles table.
5. **Report only new results.** Fewer results are fine; an empty run says so in one line.
6. **Append to the ledger after the run**: every new proposed, excluded and unverified
   lead, with today's date as first seen. Update `Last seen` on repeats that were
   encountered again. Re-read the file about ten seconds after writing to confirm it
   landed.
7. **Write the report** to `reports/<date>.md` (not to the repo), then post a short
   summary to mono: the top new results as a table, the count of excluded leads by
   reason, and open questions, with the report attached.

The ledger holds facts mono has already seen, so it is safe to read; it is never a
reason to skip verification of a new lead.

## Never

- Search for jobs using Python, or any script that scrapes, downloads or parses job
  feeds. mono's standing rule: discovery and verification are done by AI research,
  meaning web search plus reading each page, so every result gets judgement, not a regex.
- Submit applications, contact companies, or disclose candidate information. This
  includes cold-email tools and contact-harvesting services (see `docs/company-sources.md`).
- Invent or estimate dates, pay, policies, applicant counts, growth or eligibility.
- Treat "remote", "global team", crypto activity or an Estonian invoice option as
  confirmation of Iran-based eligibility.
- Suggest concealing residence, nationality, or who performs the work.
