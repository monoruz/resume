# Iran track rules (Jobinja, Jobvision, Quera)

Standing rules for the Iran track only. The remote, relocation and outreach tracks
(A, B, C) live in `docs/rules.md`, `docs/job-search-criteria.md` and
`docs/company-sources.md`; those files hold no Iran-track rules.

| Shared with the other tracks | Where |
|---|---|
| Never ask for approval to apply (strict rule) | top of `docs/rules.md` |
| AI browsing only, no scrapers | `docs/rules.md` section 2 |
| Google Sheet tracker | `docs/rules.md` section 4 |
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
| Log every job and application in the Google Sheet with Track **I Iran**; send the four Telegram events (`docs/rules.md` section 8). | 2026-11-10 |

