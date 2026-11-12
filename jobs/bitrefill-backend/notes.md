# Bitrefill: Backend Developer — tailoring notes and application draft

## Why this lead

| Check | Result |
|---|---|
| Fresh | Posted 2026-10-23 (Teamtailor `datePosted`); still live on 2026-10-25 |
| Remote | "Fully remote since day one", "Team across 30+ countries", "Wherever in the world you are, you are welcome" |
| Payment route | "Get paid in crypto if you want" (advertised option) |
| Entity | Airfill Prepaid AB, Sweden (from the 2026-10-24 report); El Salvador and Delaware entities also exist |
| Iran eligibility | **Unknown.** Customer terms carry an EU/US/UK sanctions clause; the JobPosting structured data lists Sweden under `applicantLocationRequirements`, which may be a Teamtailor default |
| Pay | Not stated: unverified against the US$3,000/month minimum |

## Tailoring rationale

The JD centres on crypto payments, supplier and third-party integrations, MongoDB/MySQL,
and search as a bonus. The resume leads with the Finestel exchange-integration layer
(eight exchange SDKs, Stripe, HubSpot, Hyperliquid) and the money-correctness work
(locking, reconciliation, rate limiting), then uses the two TypeScript projects for the
Node.js, MongoDB and OpenSearch evidence the Python-heavy career would otherwise lack.

## Gaps

| JD asks | Evidence | Gap |
|---|---|---|
| Node.js/TypeScript as the main language | Express at Mizan (2018-19) and Al Meera (2017-18); TypeScript in Optimalist and the datasource panels | No recent *employed* Node.js role; Python is the main language since 2019 |
| Typesense | OpenSearch query compilation, MongoDB text search | Typesense itself not used |
| E-commerce | Homeca marketplace; Stripe billing at Finestel | No storefront or gift-card catalogue work |
| Mentoring juniors | Finestel documentation and rule set | No explicit mentoring line in the master file |

## Cut to make two pages

Finestel gevent watchdog, DCA/TWAP, Terminal API and streamer fleet; Yarai cut to one bullet
(verify-flagged figures not used); Hamravesh to one bullet; Mofid frontend, Envoy and PKCE;
Homeca design system and backups; Al Meera, LongBio; projects cdk8s-seaweed-s3 and MN Service;
the panels' test-count bullet. Density: `--lh` 1.34 (floor), other knobs unchanged.

## Register

Bitrefill's posting is conspicuously informal ("No bullshit meetings", "get shit done"). The
resume stays formal. The form answers below use plain first person, which is normal for a form
field, but no slang.

## Draft form answers

**Where are you based? (Country/City)**
> Tehran, Iran

**Please share a link to your Github, Portfolio, LinkedIn or similar**
> LinkedIn: linkedin.com/in/mohammad-noroozi · GitHub: github.com/monoruz

**Why would you like to work at Bitrefill?**
> For the past two years I have built the part of a crypto platform that talks to other people's systems: order routing across eight exchange APIs, reconciliation when their state and ours disagree, rate limiting so we never get banned, and Stripe billing beside it. Bitrefill's backend is the same kind of problem pointed at payments and suppliers instead of exchanges, and it is a product people actually use crypto for, rather than only trade it. I also work best in the setup you describe: fully remote, written communication, and an AI-assisted workflow (I run coding agents against a repository in one of my own projects).

**Please tell us about your experience in modern backend technologies and Node.js specifically**
> My main backend language since 2019 has been Python: Django, DRF, Celery, Redis and MariaDB at Finestel, where I own the execution engine and the exchange-integration layer for 40,000+ connected accounts, and FastAPI with PostgreSQL elsewhere. Node.js is where I started: Express services on PostgreSQL and MongoDB at Mizan (2018-19) and Al Meera (2017-18). Today I write TypeScript in two production projects. Optimalist is a Bun/TypeScript service on MongoDB and OpenSearch with 220 tests, a GitHub-API sync pipeline and a durable job table. The datasource panels are four Next.js/Node consoles for MongoDB, PostgreSQL, OpenSearch and MinIO, including a MongoDB query compiler and an OpenSearch query builder that picks the right query per field type. I have not used Typesense, but I have built search on OpenSearch and MongoDB text indexes. I also run what I build: Kubernetes, AWS, Sentry and Prometheus.

**Tell us about a technical challenge you faced and how you overcame it**
> At Finestel, users occasionally got duplicate or wrongly sized orders. The cause was concurrency: fills arriving at the same time raced each other through trade callbacks, take-profit calculation and balance updates. I added Redis distributed locks around those three paths, with blocking and non-blocking variants depending on whether a second caller should wait or back off. Duplicate orders fell to near zero. That exposed a second problem: our state and the exchange's state could still drift (a fill we missed, an order left open). So I built reconciliation jobs that compare the two and repair the gap, such as cancelling dangling orders and filling take-profit gaps. Stuck positions that needed someone to fix them by hand dropped by about 75%.

## Decided by mono (2026-10-25)

- Name on the form: Mono Ruzi.
- GitHub: github.com/monoruz (resume header and `master.yaml` updated).
- No optional remarks in the answers (the crypto-payment line was removed).
- Never state job-search criteria (pay, payment route, sanctions, eligibility) in application text; now a rule in `CLAUDE.md`.

## Quantification prompts

- `finestel` Stripe billing: subscriber count or monthly billed volume.
- `finestel` rate limiter: how many API bans per month before it, if known.
- `optimalist`: any usage figure (active chats, questions served), per `q-optimalist-metrics`.
