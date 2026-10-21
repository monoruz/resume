# Company sources and ranking

How to find companies worth approaching and how to rank them. This is the reference for
track C (outreach companies) in `docs/job-search-criteria.md`, and for the growth and
hiring evidence on tracks A and B. The criteria file remains the authority on every
constraint. Where this file and the criteria differ, the criteria win.

Based on mono's Target Account Intelligence outline of 2026-10-20.

## How the sources are used

Every source below is read by AI research: a web search to find the page, then opening
and reading the page itself. Nothing here is scraped, polled by a script or queried in
bulk, and no claim enters a report without a link to the page it came from (standing
rule in `.claude/skills/job-research/SKILL.md`).

**Company identity is the website domain.** One company can appear as "Acme Inc" in a
funding database, "Acme" on Product Hunt and "Acme Labs" on a job board. Records from
different sources are matched on the company's own domain (`acme.com`), and the report
lists each company once under that domain.

## Exclusions, applied before any ranking

| Exclude | Rule | Source |
|---|---|---|
| Iranian companies | The hiring or contracting entity is registered or headquartered in Iran, or the business's main operations are in Iran, including an Iranian company working through a foreign shell. Decide from the company's legal pages, registry entries and own statements. Never decide from founders' or staff names, language or nationality. | mono, 2026-10-20 |
| US- or Israel-based entities | The actual hiring entity and the role are based in the United States or Israel. A US or Israeli parent, investor or customer alone does not exclude. | `job-search-criteria.md`, Geographic company rules |
| Unclear entity | Not excluded, but ranked lower and marked unverified. | `job-search-criteria.md` |

Excluding Iranian *companies* is separate from the Iran-based *team* signal. A non-Iranian
company that already engages engineers working from Iran is still a strong positive
signal.

## Sources

### Company, funding and registry data

| Source | Best for | What to read |
|---|---|---|
| [Crunchbase](https://www.crunchbase.com) | Global startups | Funding rounds and dates, headcount band, HQ, investors, leadership |
| [Dealroom](https://dealroom.co) | Europe | Funding, HQ, growth indicators; stronger European coverage than Crunchbase |
| [PitchBook](https://pitchbook.com) | Europe and Asia | Funding and deal history (mostly paywalled; use public profile pages) |
| [Tracxn](https://tracxn.com) | South-East Asia, emerging markets | Sector lists, funding, HQ |
| [LatamList](https://latamlist.com) | Latin America | Funding news and new startups |
| [Product Hunt](https://www.producthunt.com) | Early-stage, product-led startups | Recent launches, makers, launch date |
| [Y Combinator directory](https://www.ycombinator.com/companies), [Techstars](https://www.techstars.com/portfolio), [Seedstars](https://www.seedstars.com) | Accelerator graduates | Batch, HQ, "hiring" flag, founder names |
| National company registries (e.g. UK Companies House, Estonian e-Business Register, EU registers) | Hiring entity and country | Registered entity, address, status; settles "actual hiring entity" questions |

### Hiring signals

| Source | Best for | What to read |
|---|---|---|
| Company careers page (`/careers`, `/jobs`) | The original vacancy | Open roles, publication dates, location rules, contractor wording |
| ATS boards (Ashby, Greenhouse, Lever, Workable, Personio, Recruitee) | Original listing with a date | Published date, location, compensation, visa wording |
| [LinkedIn](https://www.linkedin.com) company pages and jobs | Headcount trend, open roles | Employee count over time, number of open roles, new leadership hires |
| [Wellfound](https://wellfound.com) | Startups actively hiring | Open roles, salary bands, remote policy |
| [RemoteOK](https://remoteok.com), [We Work Remotely](https://weworkremotely.com), [Exactly](https://exactly.ai) | Remote-hiring companies | Discovery only; confirm on the company's own listing |
| [Welcome to the Jungle (Otta)](https://www.welcometothejungle.com) | Europe and UK startups | Roles, company profile, team size |

### Growth and technology signals

| Source | Best for | What to read |
|---|---|---|
| [BuiltWith](https://builtwith.com), [Wappalyzer](https://www.wappalyzer.com) | Tech stack | Whether the stack matches master.yaml (Python/Django/FastAPI, Kubernetes, PostgreSQL, LLM tooling) |
| [Similarweb](https://www.similarweb.com) | Traffic trend | Direction of web traffic over recent months |
| [GitHub](https://github.com) | Engineering activity | Public repos, commit recency, open issues that match a documented technical need |
| Google Play / App Store | Product activity | Release recency, update cadence |
| Company blog, press, founder posts | Expansion and needs | New teams, new markets, technical problems they describe in public |

## Ranking

The criteria's ranking order comes first: compatibility with Iran-based work and a
feasible payment route, then confirmed pay, then technical fit. The signals below rank
companies **within** that order. They decide which of two otherwise comparable
companies to approach first, and they supply the sourced reason that track C requires.

| # | Signal | Strong evidence | Weight |
|---|---|---|---|
| 1 | New funding | A round announced in the last 6 months (company or investor announcement, Crunchbase/Dealroom entry) | High |
| 2 | Open key roles | Active Senior, Lead, Staff or founding engineering vacancies on the company's own careers page or ATS | High |
| 3 | Headcount growth | 10-20% or more growth in LinkedIn headcount over the last 3-6 months | Medium |
| 4 | Leadership changes | A new VP of Engineering, CTO, Head of Engineering or Head of People/Talent in the last 6 months | Medium |
| 5 | Stack match | BuiltWith/Wappalyzer, GitHub or job text shows tools that master.yaml covers | Medium |
| 6 | Traffic or product momentum | Rising Similarweb trend, recent launches or app releases | Low |

Rules for using them:

- Every signal needs a link and a date. One without either is not counted.
- Signals 1-4 are what the criteria call "evidence of engineering expansion". Open roles
  alone mean "actively hiring", not "growing".
- Headcount figures come from the page as read on the run date; write that date next to
  the figure.
- Funding and growth raise priority but never override an exclusion or a hard
  requirement.

## Decision-makers and outreach

Research may name the role to approach (CTO, VP of Engineering, founder, Head of Talent)
and link the company's own team or contact page, so mono can write a personalised
message. A good hook is a dated, sourced signal, such as "raised a Series A in
September and opened three senior backend roles".

Out of scope, per `job-search-criteria.md` ("Do not submit applications, send outreach,
or disclose candidate information" and "Do not collect unnecessary personal information
about individual employees"):

- sending, queuing or automating any message (cold-email tools such as Instantly or Lemlist);
- harvesting personal email addresses or profiles (Apollo, Hunter, Dropcontact, PhantomBuster);
- proxies or session tricks to get around a site's access controls.

mono sends every message personally.
