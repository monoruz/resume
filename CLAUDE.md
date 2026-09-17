# Resume Tailoring System

A single-source-of-truth career database (`data/master.yaml`) that gets selected,
reordered, and rewritten into a **2-page, ATS-safe PDF** tailored to a specific job
description, on demand.

## Core workflow

When the user pastes or links a job description and asks for a resume:

1. **Read the JD carefully.** Extract into a working list:
   - Hard requirements (years, languages, frameworks, domains)
   - Nice-to-haves
   - The *vocabulary* the company uses (e.g. "distributed systems" vs "microservices",
     "growth" vs "acquisition") — mirror their words where they describe the same work
   - Signals about seniority, team size, and what the role actually optimizes for
2. **Select** from `data/master.yaml`: which roles, which bullets, which projects, which
   skills. Ruthlessly cut what does not serve this JD. Two pages is a hard budget.
3. **Rewrite** the selected bullets to lead with the JD's priorities (see Truth policy).
4. **Render** to `jobs/<company>-<role>/` — see Output.
5. **Report back** in chat with: the tailoring rationale (2-4 lines), the gap list, and
   the quantification prompts. Never bury these in a file the user has to go find.

Ask for the JD if the user asks for a resume without providing one. Ask which of several
resumes to iterate on if it is ambiguous.

## Truth policy (non-negotiable)

Everything the resume asserts must be true and traceable to what the user has told me.

**Allowed — this is the tailoring lever, use it aggressively:**
- Reordering, cutting, merging, and splitting bullets
- Rewriting wording, framing, and emphasis to match the JD's language
- Naming skills genuinely *implied* by described work (built and shipped a Django API →
  "REST API design", "relational data modeling" are fair)
- Choosing the job title variant the user actually held that reads closest to the target
  role (if they held both "Software Engineer" and an internal "Tech Lead" designation,
  lead with whichever fits)
- Adjusting scope language to the truthful ceiling, not the truthful average

**Never:**
- Invent or alter employers, titles, dates, locations, degrees, certifications,
  or employment continuity
- Invent metrics, team sizes, user counts, revenue figures, or performance numbers
- Claim tools, languages, or domains the user has not actually worked in
- Silently upgrade an exposure into an expertise

**The metrics gap — handle it this way, never by guessing:**
Strong resumes are quantified, and the master data will often lack numbers. When a bullet
would land far harder with a figure, do **not** insert one. Instead add it to the
**quantification prompts** in the chat report:

> `bullets.finestel.3` — "Cut API response times" would be much stronger with a number.
> From what you've described (Redis caching layer on the hot path) a 40-70% reduction is
> typical. What was the actual figure?

The user answers, the answer goes into `master.yaml` as their claim, and every future
resume reuses it. This is how the database gets stronger over time — treat it as a
standing job, not a one-off.

If the user directly instructs me to insert a specific fabricated fact, say once, briefly,
that I won't, offer the truthful strongest alternative, and move on. Do not lecture.

## Data model

`data/master.yaml` is the only source of career facts. Never write career content directly
into a rendered resume that is not in the master file — add it to the master first, then
render. This keeps every resume consistent with every other one.

Key conventions:
- Every role has **more bullets than any single resume will use** (aim for 6-10). The
  master is a superset; tailoring is selection.
- Each bullet carries `tags:` (skills/domains) so JD matching is mechanical, and
  optionally `impact:` (high/med/low) for tie-breaking when trimming to fit.
- `id:` on roles and projects so the chat report can reference specific items.
- Metrics live inline in the bullet text, already verified by the user.
- `verify: true` marks a claim the user has not yet confirmed. **Never render a
  `verify: true` bullet.** Raise it, get an answer, remove the flag.
- `needs_metric:` records a number the bullet should carry but the user has not supplied.
  The bullet text is stored **without** the figure, so it is safe to render as-is; the
  field describes exactly which number to ask for. Never fill one in by estimation — if
  source material arrives with a placeholder like `[X%]`, strip the claim to what is known
  and record the gap here.
- `open_questions:` at the bottom of the file tracks unresolved gaps. Work through the
  relevant ones before a tailored render rather than dumping all of them at once.

When the user dumps new raw experience, normalize it into `master.yaml` yourself, then
show them a summary of what was added and ask about anything ambiguous. Don't make them
write YAML.

## Output

**Primary deliverable: PDF, rendered from HTML+CSS via headless Chrome.**
No LaTeX or pandoc on this machine; Chrome gives full typographic control and exact
pagination. Do not introduce a new toolchain without asking.

```bash
build/render.sh jobs/<slug>/resume.html
```

Per-job directory layout:

```
jobs/<company>-<role>/
├── jd.md          # the job description, saved verbatim
├── resume.html    # the tailored resume (self-contained, inlines the template CSS)
├── resume.pdf     # rendered output — the thing the user sends
└── notes.md       # tailoring rationale, gaps, quantification prompts, interview prep
```

Slug format: lowercase, hyphenated, `company-role` (e.g. `stripe-senior-backend`).

## Design constraints

**ATS-safe single column.** Non-negotiable structural rules — ATS parsers break on
violations of these:
- One column. No sidebars, no multi-column CSS, no layout tables.
- Real selectable text only. No text baked into images, no icon fonts carrying meaning
  (a ✉ glyph next to an email is fine; an icon *replacing* the word "Email" is not).
- Standard section headings: `Experience`, `Education`, `Skills`, `Projects`. Parsers
  pattern-match on these — don't get clever with "Where I've Been".
- Dates in a consistent `Mon YYYY – Mon YYYY` format, on the same line as the role.
- Contact details as plain text in the document body, never in the PDF header/footer
  (many parsers discard headers).

Polish comes from typography, whitespace, and one accent color — not from layout tricks.

**Exactly 2 pages.** Not 1.5, not 2.1. Page 2 should be at least ~70% full; if the content
only fills 1.3 pages, cut to a tight 1 page instead and tell the user why. `templates/base.html`
exposes density knobs as CSS variables at the top (`--fs-body`, `--lh`, `--gap-section`,
`--gap-item`) — tune those to fit before cutting content, but never below the floors noted
in the template comments (below those it reads as cramped and desperate).

**Always verify the page count after rendering** — `build/render.sh` prints it. A resume
that silently spilled to 3 pages is a failed deliverable.

## Content principles

- Bullets lead with the outcome, not the activity. "Cut p99 latency 60% by…" beats
  "Responsible for optimizing…".
- No first-person pronouns, no "Responsible for", no personal-attribute filler
  ("hard-working team player"). Skills sections list tools and domains, not adjectives.
- Past roles in past tense, current role in present tense.
- The summary/headline at the top is rewritten per JD — it is the highest-leverage
  50 words on the page. Omit it entirely rather than writing a generic one.
- Reverse-chronological. Deviating from this is an ATS and recruiter red flag.
- Skills section is ordered by JD relevance, not alphabetically or by fondness.

## Voice — formal register, written by the person who did the work

**Register: strictly formal throughout.** No contractions, no colloquialisms, no humour,
no rhetorical questions, no conversational asides. Complete grammatical constructions.
Impersonal third person — no `I`, `my`, or `we`. Restrained punctuation: prefer the
semicolon and colon to the em dash, and keep em dashes to one or two per page.

Formality and inflated vocabulary are not the same thing, and this is the distinction that
matters most here. `Spearheaded a comprehensive initiative to leverage robust solutions`
is not formal — it is padded. `Diagnosed intermittent worker termination under sustained
load` is formal, because it is precise and impersonal. Formal register raises precision;
it does not raise word count or abstraction. When in doubt, the more exact word is the
more formal one.

The second goal is that every line reads like it came from the engineer who was actually
there. This is not in tension with formality: specificity survives formal register intact,
and it is what makes a resume land. It is casualness that formality removes, not detail.
Evading AI detectors is not the objective — those are unreliable on short factual bullets
and should not drive decisions — but the AI tells and the quality problems are the same
list, so this section addresses both.

**Banned vocabulary.** These are LLM defaults and recruiters are sick of them:
`leveraged` · `utilized` (use "used") · `spearheaded` · `orchestrated` · `streamlined` ·
`facilitated` · `robust` · `seamless` · `comprehensive` · `cutting-edge` · `state-of-the-art` ·
`delve` · `underscore` · `testament to` · `showcase` · `empower` · `elevate` ·
`demonstrated expertise in` · `proficient in` · `responsible for` · `helped to` ·
`played a key role in` · `successfully` (if it shipped, "successfully" is noise).

**Banned constructions:**
- "Not just X, but Y" and "X isn't just Y — it's Z"
- Tricolons used as flourish ("faster, cleaner, and more maintainable")
- Every bullet opening with a past-tense verb in the same rhythm
- Em-dash-heavy sentence rhythm repeated across bullets (one or two per page, maximum)
- Hedges: "helped improve", "contributed to", "worked to ensure"
- Any sentence that would fit equally well on a different candidate's resume

**Do this instead:**
- **Specificity only the doer would have.** "Gunicorn workers exiting on response timeout"
  is more convincing than "resolved server stability issues" precisely because it is odd
  and narrow. Name the actual tool, the actual failure, the actual number. When the master
  file has a concrete detail, use it rather than summarizing it away.
- **Vary the shape.** Real writing is uneven. Some bullets run two lines, some run one.
  Not every bullet carries a metric — a page where all six bullets end in a percentage
  reads as manufactured. Roughly half should.
- **Vary the opening.** Not every line begins with a past-tense verb. A subject-first
  construction is equally formal and breaks the rhythm: "Four legacy frontend projects
  carried no test coverage; all four were migrated to typed, documented code." Use two or
  three per page at most, or the variation becomes its own pattern.
- **Prefer the exact verb over the impressive one.** `built`, `designed`, `diagnosed`,
  `migrated`, `instrumented`, `reduced`, `eliminated`, `maintained`, `established`. Each
  names a specific action. Reject verbs that name no action: `leveraged`, `spearheaded`,
  `orchestrated`, `streamlined`. Latinate vocabulary is entirely acceptable — required,
  at this register — where it is precise; it is rejected only where it is padding.
- **State results as measured facts, not achievements.** "Reduced query response time by
  50%" rather than "achieved an impressive 50% reduction". No self-congratulation, no
  intensifiers (`significantly`, `dramatically`, `exceptionally`, `highly`).
- **Keep domain register.** Write the way engineers in that domain talk: "N+1", "p99",
  "pre-signed URLs", "circuit breaking", "rolling update". Precision of jargon is a strong
  human signal; vague technical gesturing is the opposite.
- **Let the summary be opinionated.** The highest-risk generic text is the summary. It
  should make a specific claim about what this person is, one another candidate could not
  copy. "Frontend engineer who owns the API behind the UI" is a position. "Experienced
  developer with strong skills" is filler.

**Never** introduce deliberate errors, awkward grammar, or typos to seem more human. That
trades a real signal (competence) for an imaginary one.

**Self-check before rendering.** Read the bullets in sequence and confirm three things:
(1) the register is uniformly formal — no contraction, colloquialism, or casual verb has
slipped in; (2) the bullets do not all share one length, rhythm, and opening shape;
(3) no banned word or empty intensifier survived. Then re-read the source resumes — the
user's own phrasing often carries technical detail worth preserving, though it generally
needs lifting into formal register before use.

**Register exception, to raise rather than decide alone.** Strict formality is correct for
enterprise, financial, governmental, academic, and most non-US employers. A small number
of employers — early-stage startups, and some US consumer-product companies — write job
descriptions in a deliberately informal register, and matching formal prose against them
can read as distant. If a JD is conspicuously informal, say so in the chat report and
recommend a moderated register; do not quietly relax the default.

## Persian resumes (RTL)

Use `templates/base-fa.html` — `lang="fa" dir="rtl"`, Vazirmatn embedded (Arabic + Latin +
Latin-Extended, one variable face per subset). Vazirmatn carries Latin as well as Persian,
so English technical terms sit inside Persian prose in the same typeface instead of
switching mid-sentence.

**Bidirectional text is the thing that breaks.** The Unicode bidi algorithm handles plain
Latin words inside Persian correctly, but reorders strings that mix Latin with digits,
slashes, brackets or operators — `SQLAlchemy 2.0`, `p95`, `2.1s`, `ALGORITHM=INSTANT`,
`select_related`. Wrap each of those in `<span class="ltr">`, which isolates the run. Plain
words such as `Django` or `Kubernetes` need no wrapper. After rendering a Persian resume,
read the PDF and confirm no mixed-script string has been visually reversed; this is not
something the page count or a lint check will catch.

**Layout under `dir="rtl"`:** `padding-inline-start` resolves to the right edge, so list
indentation works without a separate rule; the `.item-head` flex row places dates on the
left, which is correct. Dates are pinned LTR so Gregorian months and years do not reorder.

**Density:** Persian sets wider and needs more leading than Latin at the same point size.
The RTL template's floors are higher (`--fs-body: 10pt`, `--lh: 1.60`) and its default
line-height is 1.75. Expect a Persian resume to hold noticeably less content per page than
the Latin one; cut accordingly rather than dropping below the floors.

**Register:** the formal-voice rules apply in Persian too — کتابی/رسمی throughout, no
colloquial forms, no first person. Keep the same ban on padding and self-assessment.

**Digits:** Latin digits (`40,000`) by default. They are standard in Iranian technical
writing and avoid any font-fallback risk. Do not mix Latin and Persian digits in one
document.

**Calendar:** ask. Iranian employers vary between Gregorian and Jalali (شمسی) dates on
Persian resumes, and the choice must be consistent across the whole document.

## Things to just do, without asking

- Save the JD verbatim to `jd.md` (postings get taken down; you'll want it for interview prep)
- Re-render the PDF after any HTML edit
- Report the page count and any content that got cut to make the budget
- Update `master.yaml` when the user supplies new facts or metrics mid-conversation

## Things to ask about

- Whether to target a different seniority framing than the JD literally states
- Any JD requirement that the master data cannot support at all (there may be a real
  answer that was never written down)
- Whether to spend a second render on a `.docx` mirror for a portal that demands Word

## Files

- `CLAUDE.md` — this file
- `data/master.yaml` — the career database; everything flows from here
- `templates/base.html` — empty single-column template with density knobs in `<style>`
- `templates/example.html` — the same template filled in, as a markup reference
- `build/render.sh` — HTML → PDF via headless Chrome, reports page count
- `templates/_fonts.css` — embedded Source Sans 3 (base64 woff2); inlined into templates
- `templates/base-fa.html` — Persian/RTL template (Vazirmatn, bidi isolation, RTL layout)
- `templates/_fonts-fa.css` — embedded Vazirmatn (Arabic + Latin)
- `.github/workflows/resumes.yml` — CI: validate, render, gate on page count, release
- `build/check.py` — validates `master.yaml`; **run it after every edit to that file**.
  PyYAML silently keeps the last of any duplicate mapping key and will drop a whole role
  without raising, so never trust a bare `safe_load` as proof the edit landed. The checker
  also reports `verify: true` bullets and concurrent "Present" roles.
- `jobs/<slug>/` — one directory per application
- `out/` — scratch renders (gitignored)

### Rendering notes

`render.sh` tries `--headless=old` first and falls back to `--headless=new`. This is not
redundancy for its own sake: old headless hangs on `--print-to-pdf` for `file://` URLs on
this Mac, and recent Linux Chrome builds ship only the new mode. Both paths are exercised
— do not simplify to one. It also discovers Chrome across macOS and Linux paths, honours
`CHROME=/path`, and fails the run on a page count other than 2 when `STRICT_PAGES=1`
(which CI sets).

**Fonts are embedded, and that is load-bearing.** `templates/_fonts.css` holds Source Sans
3 (SIL OFL 1.1) as base64 woff2 — one variable face per subset, covering weights 200-900 —
inlined into every template. Without this, CI on Ubuntu would substitute a different font,
silently changing every line width and therefore the pagination you proofread. Never
replace the font stack with a system font, and keep the embed inlined so each `resume.html`
stays self-contained.

**The embedded font covers Latin and Latin-Extended only.** Non-Latin script (the Persian
product names in the Yarai entry, for instance) will render as missing glyphs on a machine
without a fallback font. Transliterate in rendered resumes — "یار" becomes "Yar" — or the
PDF shows empty boxes on the reviewer's screen and not on yours.

**CI** (`.github/workflows/resumes.yml`) runs on every push to `main`: it validates
`master.yaml`, renders every `jobs/*/resume.html` with `STRICT_PAGES=1`, uploads the PDFs
as build artifacts, and republishes them to a rolling `latest` GitHub release. It renders
only what is committed; it cannot tailor, because tailoring means reading a JD.
