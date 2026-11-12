# Iran track rules (Jobinja, Jobvision, Quera)

Standing rules for the Iran track only. The remote, relocation and outreach tracks
(A, B, C) live in `docs/rules.md`, `docs/job-search-criteria.md` and
`docs/company-sources.md`; those files hold no Iran-track rules.

| Shared with the other tracks | Where |
|---|---|
| Never ask for approval to apply (strict rule) | top of `docs/rules.md` |
| AI browsing only, no scrapers | `docs/rules.md` section 2 |
| Google Sheet tracker (general writing rules, status colors) | `docs/rules.md` section 4 |
| Name, GitHub, PDF resumes, captcha hand-off | `docs/rules.md` section 5 |
| Telegram events | `docs/rules.md` section 8 |

**Rule (mono, 2026-11-10): a separate daily track for Iranian job platforms**, run in
mono's signed-in Chrome on the Mac, alongside the remote and relocation search (`docs/rules.md` section 3).
It covers **jobinja.ir, jobvision.ir and quera.org/magnet** only.

| Rule | Since |
|---|---|
| For these three platforms only, the Iranian-company exclusion (`docs/rules.md` section 2, `docs/job-search-criteria.md` addendum), all salary minimums (`docs/rules.md` section 5, `docs/job-search-criteria.md`) and the rule against mentioning Iran do not apply. | 2026-11-10 |
| Apply as widely as possible; salary is ignored. Order: AI / LLM roles first, then backend (Python, Django, FastAPI), platform, SRE and DevOps. | 2026-11-10 |
| Salary field: **توافقی (negotiable)**. When a number is required: **2,000,000,000 rials per month** (200,000,000 toman). | 2026-11-10 |
| Never apply to a previous employer: Finestel, Dirichlet, Yarai, LongBio, Hamravesh (همروش), Mofid Securities / Bourseview (کارگزاری مفید), Homeca, Mizan Gostaran Sharif, Al Meera. Source: `data/master.yaml` and the resume PDFs. | 2026-11-10 |
| Fully automated: apply without asking. Only a captcha or a sign-in that needs mono's password pauses a run. | 2026-11-10 |
| Resumes: always attach a custom track PDF (ai-llm for AI roles, backend, platform-sre). **Never send a platform profile or platform-built resume.** On Jobvision, apply only when the uploaded PDF is attached; if a flow sends only the profile, skip the job. | 2026-11-11 |
| Search is AI browsing only, one listing at a time (`docs/rules.md` section 2). | 2026-11-10 |
| Send the four Telegram events (`docs/rules.md` section 8). | 2026-11-10 |


## Google Sheet: Iran tabs

**Rule (mono, 2026-11-12): "please seperate also iran jobs in seperated sheet in the same doc".**
Iran-track rows live in their own three tabs of the same "Job Search Tracker" Google Sheet.
They are never written to the Jobs, Companies or Applications tabs, which hold tracks A, B
and C only.

| Tab | Holds | IDs |
|---|---|---|
| Iran Jobs | Every Jobinja / Jobvision / Quera vacancy, Track `I Iran`. Same 25 columns as Jobs. | `IJ001`, `IJ002`, ... |
| Iran Companies | One row per Iranian employer. Same columns as Companies. | `ir:<platform company slug>` |
| Iran Applications | Every Iran-track application. Same columns as Applications. | `IA001`, `IA002`, ... |

| Rule | Why |
|---|---|
| Log each new job in Iran Jobs and each application in Iran Applications right after it is confirmed; set the job's Status and Application IDs in the same session. | Same as the general rule in `docs/rules.md` section 4, applied to the Iran tabs. |
| Iran IDs have their own sequences: next Job ID = last `IJ` + 1, next Application ID = last `IA` + 1. Never take a `J` or `APP` number. | The two tracks ran in parallel on one sequence and the remote run overwrote 25 Iran rows (J0931-J0955) on 2026-11-12. |
| Add the employer to Iran Companies before the job row. | `Iran Jobs!C` and `Iran Applications!C` look the name up in Iran Companies. |
| Leave the formula columns empty: `Iran Jobs!C`, `Iran Applications!C`, `Iran Companies!D:F`. | Each is one ARRAYFORMULA in the header cell. |
| Start every Status with one of the color keywords in `docs/rules.md` section 4 (`applied`, `submitted`, `interview ...`, `rejected ...`). | The Iran tabs carry the same conditional-format colors; other first words stay uncolored. |
| Ledger key is `<platform>:<listing code>` (e.g. `jobinja:tMXH`, `jobvision:1600354`, `quera:xmqgw`); check it before adding a row. | Dedup across runs. |

Rows logged before the split used `J0931`-`J0995` and `APP070`-`APP134`. Their old IDs
are kept in the Iran Jobs "Ledger note" column and the Iran Applications "Ledger #" column.
