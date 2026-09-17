# بودجه‌بندی هزینه‌ها و دارایی‌های بانک با استفاده از هوش مصنوعی

Persian (RTL), Jalali dates, 2 pages. Rendered 2026-09-17.

## Positioning

"مهندس هوش مصنوعی و سامانه‌های مالی" — an engineer who builds AI systems over
financial data, on-premise, with auditable output. Three threads carry the whole
document:

1. **On-premise inference.** Yarai leads with five production models up to 27B
   parameters on internal GPUs, "وابستگی به سرویس‌های بیرونی را حذف کرد". For an
   Iranian bank this is not a nice-to-have — financial data cannot leave the
   institution, and sanctions foreclose the hosted APIs. Few local candidates can
   show they have already done it.
2. **Auditable AI.** Dirichlet's schema-constrained output contract and the ~22-rule
   deterministic engine "که نهاد ناظر بتواند آن را به چالش بکشد" answer the question
   a bank's audit function asks first: when the model produces a number, can you
   defend it? This is the single most transferable thing in the file.
3. **Financial systems credibility.** Finestel ($250M monthly, reconciliation,
   near-zero duplicate orders) and Mofid (Iran's largest capital-market data
   platform, ~1 TB) establish that the AI work sits on top of real financial
   engineering, not demos.

Sharif MSc/BSc is kept prominent; it carries disproportionate weight with Iranian
banks.

## THE RISK — read this before sending

**«بودجه‌بندی با هوش مصنوعی» may mean forecasting, not LLMs.** If the bank wants
time-series forecasting, cost prediction, or portfolio/asset optimisation — ARIMA,
Prophet, gradient boosting, optimisation under constraints — then the master
database has almost nothing: the only classical ML on record is the BigQuery
recommendation work at Al Meera in 2017-18, which is old and thin. Everything
strong in this resume is LLM and AI-platform engineering.

Two readings, two different resumes:
- **"AI" = LLM/automation applied to budgeting workflows** → this resume is a strong fit.
- **"AI" = predictive modelling of costs and assets** → this resume is a near-miss,
  and you should say plainly in the cover note that your strength is building and
  operating the systems rather than the modelling.

Find out which before applying if you possibly can. It changes the answer.

## Selection

Included: Finestel (5), Dirichlet (4), Yarai (2), Mofid (3), Hamravesh (1), Loader (1).

Cut, and why:
- **LongBio, Homeca, Mizan, Al Meera** — nothing on them serves an AI/finance role, and
  Persian costs roughly 30% more space than Latin at the same point size.
- **Dirichlet's image-analysis security review** — strong work, wrong subject.
- **Yarai's multi-tenant branded assistants** — consumer-product framing; tested at
  render time and it pushed the document to 3 pages.
- **Hamravesh's async replication** — kept the role for on-premise infrastructure
  credibility, one bullet only.
- **Frontend, DevOps consulting, web-crawling, MN Service** — off-topic here.

Kept deliberately: **Loader's CDC over bank card transactions**. One line, and the only
item in the database touching banking payments directly.

Fit is exact: adding any single further bullet spills to 3 pages.

## Numbers deliberately omitted

Per the truth policy, the five Yarai bullets rendered **without** their sample figures —
no "70% cost reduction", no "six teams". The claims stand unquantified. Supply the real
numbers and they go in, and these bullets become considerably stronger.

## Verify before sending

1. **Clearance on the Finestel figures.** $250M monthly volume, 40,000 accounts, the
   60M-row table and the 75% reduction are the backbone of page 1, and `q-finestel-visibility`
   is still unanswered. Some employers treat volume and account counts as confidential.
   A bank is exactly the sort of reader who might mention it to someone.
2. **The Persian name** — محمد نوروزی was inferred, then confirmed by you. Worth one
   more look on a document you submit.
3. **Jalali conversions** — computed and checked against four Nowruz anchors, but the
   month boundaries are approximate for periods given only as a year. خرداد ۱۴۰۳ for
   "Jun 2024" assumes mid-month.
4. **Persian prose** — written to a formal register (کتابی). A native read-through before
   submission is cheap insurance; I would not stake an application on my Persian
   without it.

## Quantification prompts

- **Mofid**: no team size, no user count for Bourseview. "Iran's largest capital-market
  data platform" would land harder with a user or institution count.
- **Hamravesh**: the SeaweedFS-vs-MinIO performance claim is still an assertion; a
  benchmark figure would make it evidence.
- **Loader**: transaction volume through the CDC payment pipeline — a banking number,
  on a resume going to a bank.

## Interview preparation

Likely questions, and where the answers live:
- *"How do you stop the model inventing a budget number?"* → the Dirichlet output contract:
  strict schema plus deterministic post-processor, so output outside the approved set is
  structurally impossible, with the rules engine as reproducible baseline.
- *"Can this run inside our network?"* → Yarai: KServe/vLLM on internal GPUs, five models
  to 27B, no external dependency.
- *"Have you worked with financial data at scale?"* → Mofid ~1 TB and Finestel's 60M-row
  trade table with online DDL and no write downtime.
- *"What happens when it breaks at 2am?"* → Finestel reconciliation and the gevent/Celery
  watchdog work (not on this resume for space; keep it as a spoken answer).
