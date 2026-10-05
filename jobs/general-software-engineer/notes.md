# General software engineer resume

Not tailored to a posting. The target is a two-page resume that shows the widest credible surface: trading backend, platform and SRE, and LLM systems, with frontend and consulting kept where they add a skill the later roles do not.

## Why this shape

The summary states the three things a reviewer can check: the Finestel execution path ($2M a month, eight exchanges), the Hamravesh cluster (100+ nodes, 40+ TB), and Dirichlet's constrained model output. Experience stays reverse-chronological. Overlaps are labeled (part-time, contract, concurrent freelance) so the timeline does not look like double full-time employment.

Yarai figures that are still `verify: true` in `data/master.yaml` are not on the page. The inference platform, the LiteLLM gateway, and the GitOps path are rendered without those numbers.

## Cut to make two pages

- Finestel: gevent watchdog, online DDL on the 60M-row trade table, DCA/TWAP engine, Terminal API, Stripe and white-label API.
- Dirichlet: RBAC on Supabase, the traffic-sign catalogue query cut (~15 queries to 2, ~70% latency), CI/CD ownership.
- Yarai: the incident-triage and news-agent products. The white-label platform is on the page without the launch-time claim. Cost, team-count, complete-report, and drafts-per-week figures are unverified and were not used.
- Mofid: T-SQL and the ~1 TB ownership bullet (the ~1 TB figure is in the subtitle only).
- Homeca: SMS OTP, Celery/RabbitMQ, HAProxy, backups. The 0.1% downtime bullet stays unrendered (`verify: true`).
- LongBio: omitted. Bullets are generic and the start month is unknown.
- Mizan and Al Meera: omitted. This drops Express/Node as a primary story, and BigQuery, Spark, and the recommendation system.
- Projects: datasource admin panels, MN Service, Loader, the crawler. Optimalist's GitHub link is omitted because the repository is private. cdk8s-seaweed-s3 is linked; it lives under `mm74noroozi`, not the header account `monoruzi`.

## Quantification prompts

- `bullets.yarai` inference cost — the 70% reduction is a placeholder. What was the actual cut versus the third-party API?
- `bullets.yarai` gateway — how many internal teams were on the LiteLLM gateway?
- `bullets.yarai` white-label — launch time for a new branded assistant before and after the Helm templates? The "three days to four hours" figure is unverified.
- `bullets.yarai` triage — complete-report rate after the clarification loop? 85% is unverified.
- `bullets.yarai` news agent — publish-ready drafts per week? "Around 20" is unverified.
- `bullets.homeca` — start and end months, team size, and any traffic or user figure. Dates are year-only on the page.
- `bullets.finestel` — confirm 40,000+ accounts, ~25K signals/day, 20M+ events/day, the 60M-row table, and ~148K LOC are cleared for external use.
- `profile.years_experience` — the page says eight years, anchored to 2018. Anchoring to Al Meera (2017) makes it nine.
- `dirichlet` — the page ends the contract at Sep 2026. Say if it is still open.
- MN Service (1,000+ clients, ~600 GB/day) is off the page. Confirm whether a censorship-circumvention VPN belongs on a general resume.
