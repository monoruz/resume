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
     policy, confirmed Iran-based engineers) but no qualifying recent vacancy.
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
     contract language, job-board entity field. A foreign office address alone is not
     an entity;
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
- an "Excluded" table listing what was cut and the failing requirement, so the same
  leads are not re-researched next run.

Commit the report on the working branch. In chat, report the group tables (top results
only), the count of excluded leads by reason, and the open questions mono must answer
or ask the company. Keep the long detail in the file.

## Never

- Submit applications, contact companies, or disclose candidate information.
- Invent or estimate dates, pay, policies, applicant counts, growth or eligibility.
- Treat "remote", "global team", crypto activity or an Estonian invoice option as
  confirmation of Iran-based eligibility.
- Suggest concealing residence, nationality, or who performs the work.
