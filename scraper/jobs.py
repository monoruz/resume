#!/usr/bin/env python3
"""Collect remote job listings and rank them against data/master.yaml.

Sources (all public, no API key):
  remoteok   https://remoteok.com/api                     JSON
  remotive   https://remotive.com/api/remote-jobs         JSON
  wwr        https://weworkremotely.com/categories/*.rss  RSS
  hn         Hacker News "Who is hiring?" via the Algolia API

Filtering and labels follow docs/job-search-criteria.md. The compensation minimums,
the freshness window and the label names are read from that file at run time.

  1. Hard exclusions (label "Excluded", with the reason):
     - publication date missing or older than the freshness window
     - confirmed maximum cash compensation below the full-/part-time minimum
     - role based in the United States or Israel
     - posting restricts the work location to somewhere Iran is not, or lists Iran
       among excluded/sanctioned countries
     - on-site role without explicit visa sponsorship
     - not an engineering role at all (sales, recruiting, design, ...)
  2. Evidence columns, each kept separate as the criteria require:
     iran_eligibility  confirmed / unknown / incompatible
     crypto_pay, b2b_invoice  advertised option / unknown
     comp_meets_min    yes / no / unverified
  3. Label: Confirmed-compatible needs Iran confirmed + a payment route + comp met;
     Conditional needs at least one of Iran confirmed or a payment route;
     everything else that survives is Low-priority/unverified.
  4. Group: A = remote, B = sponsored relocation. Group C (outreach) needs research
     a feed cannot supply, so it is not produced here.
  5. Within a label, rows sort by the criteria's ranking order, using technical fit
     (title family + weighted resume-skill overlap, 0-85) as the main tie-breaker.

Outputs: out/jobs/ranked.csv (every row, excluded included, with reasons) and
out/jobs/report.md (group A and B tables, plus exclusion counts).

Usage:
  python3 scraper/jobs.py                       # all sources
  python3 scraper/jobs.py --sources hn,wwr --top 30
  python3 scraper/jobs.py --cache out/jobs/raw.json   # re-score a saved fetch offline

Stdlib + PyYAML only (PyYAML is already required by build/check.py).
"""
import argparse, csv, html, json, re, sys, time, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
UA = 'Mozilla/5.0 (resume job scraper; +https://github.com/monoruz/resume)'

# ---------------------------------------------------------------------------
# Targets. Titles come from the role families in master.yaml (profile.slants).
# ---------------------------------------------------------------------------
FAMILIES = {
    'backend': (r'\b(backend|back-end|back end|python|django|fastapi|api)\b', 30),
    'platform-sre': (r'\b(sre|site reliability|platform|devops|infrastructure|infra|'
                     r'kubernetes|cloud engineer|reliability|production engineer)\b', 30),
    'ai-infra': (r'\b(llm|ai|ml|machine learning|mlops|genai|inference|applied ai|agents?)\b', 30),
    'fullstack': (r'\b(full[- ]?stack)\b', 25),
    'fintech': (r'\b(trading|fintech|exchange|crypto|payments?|quant|defi|brokerage)\b', 20),
    'founding-lead': (r'\b(founding|tech lead|technical lead|cto|head of engineering)\b', 20),
    'consulting': (r'\b(consultant|consulting|contractor|freelance)\b', 15),
    'frontend': (r'\b(frontend|front-end|front end|react|next\.?js)\b', 15),
    'seo': (r'\b(seo|technical seo)\b', 15),
}
SENIORITY = (r'\b(senior|sr\.?|staff|lead|principal)\b', 10)
ENGINEER = r'\b(engineer|developer|sre|architect|programmer|consultant|cto)\b'
# Criteria: "avoid unnecessary exact-stack exclusions", so only roles that are not
# engineering at all are cut. Native mobile is kept but simply scores low on fit.
NOT_ENGINEERING = (r'\b(sales|marketing manager|recruiter|account executive|account manager|'
                   r'customer success|support specialist|designer|copywriter|writer|'
                   r'data entry|intern|internship)\b')

# --- Geography (criteria: GEOGRAPHIC COMPANY RULES, CANDIDATE PROFILE) -----------
US_IL = (r'\b(united states|usa|u\.s\.a?\.?|us[- ]based|us only|us citizens?|'
         r'us residents?|israel|tel aviv|herzliya|haifa|jerusalem|'
         r'san francisco|sf bay|bay area|new york|nyc|seattle|boston|austin|chicago|'
         r'los angeles|denver|atlanta|miami|washington,? dc|security clearance)\b')
# A location field naming only somewhere Iran is not, e.g. "Europe only", "UK", "LATAM".
NOT_IRAN_REGION = (r'\b(canada|north america|americas|latam|latin america|south america|'
                   r'mexico|brazil|argentina|colombia|uk|united kingdom|ireland|europe|eu|'
                   r'eea|germany|france|spain|portugal|netherlands|poland|italy|sweden|'
                   r'norway|denmark|finland|switzerland|austria|belgium|czech|romania|'
                   r'australia|new zealand|india|philippines|japan|singapore|apac|africa)\b')
OPEN_REGION = (r'\b(worldwide|anywhere|global|any location|all countries|emea|'
               r'middle east|mena|asia|iran|utc[+-]?[0-4]\b|gmt[+-]?[0-4]\b)\b')
IRAN_EXCLUDED = (r'(sanctioned countr|ofac|embargoed|(except|excluding|exclude|not|outside of)'
                 r'[^.]{0,60}\biran\b|\biran\b[^.]{0,40}\b(cuba|north korea|syria|crimea)|'
                 r'\b(cuba|north korea|syria|crimea)\b[^.]{0,40}\biran\b)')
REMOTE = r'\bremote\b'
NOT_REMOTE = r'\b(no remote|not remote|onsite only|on-site only|in[- ]office only)\b'

# --- Payment routes (criteria: REMOTE CONTRACTING AND PAYMENT) -------------------
# Kept as separate columns because evidence for one does not confirm another.
CRYPTO_PAY = (r'\b(paid in (crypto|usdc|usdt|stablecoins?)|pay(ment|s)? in (crypto|usdc|usdt|'
              r'stablecoins?)|salary in (crypto|usdc|usdt)|(usdc|usdt|stablecoin) (salary|'
              r'payments?|compensation)|crypto (salary|payroll|compensation|payments? option))')
B2B_INVOICE = (r'\b(b2b contract|b2b agreement|invoice us|invoic(e|ing) (monthly|through|via)|'
               r'contract(or)? via your (own )?company|through your (own )?(company|agency)|'
               r'subcontract(ing|or)?|independent contractor|contractor agreement|'
               r'agency or individual)\b')

# --- Relocation track ------------------------------------------------------------
VISA = (r'\b(visa sponsorship|sponsor(s|ing)? (a |your |work )?visas?|will sponsor|'
        r'h-?1b sponsorship|blue card sponsorship|skilled worker visa sponsorship)\b')
NO_VISA = (r'\b(no|not|unable to|cannot|can\'t|do not|don\'t|without)\b[^.]{0,30}'
           r'\b(visa|sponsor)')

# --- Other priority signals ------------------------------------------------------
PREFERRED_INDUSTRY = (r'\b(fintech|trading|exchange|brokerage|payments|financial|crypto|defi|'
                      r'seo|search engine optimi[sz]ation|llm|generative ai|ai[- ]native|'
                      r'machine learning|inference)\b')
LOW_COMPETITION = (r'\b(contract|contractor|freelance|paid trial|paid project|trial project|'
                   r'founding|first engineer|sole engineer|email (the )?(founder|cto))\b')
PART_TIME = r'\bpart[- ]time\b'

# Resume tags are slugs; these are the words a JD uses for them.
SYNONYMS = {
    'kubernetes': ['kubernetes', 'k8s'], 'postgresql': ['postgres', 'postgresql'],
    'ci-cd': ['ci/cd', 'ci-cd', 'continuous integration', 'continuous delivery'],
    'llm': ['llm', 'llms', 'large language model'], 'ai': ['ai', 'genai', 'generative ai'],
    'api-design': ['api design', 'rest api', 'apis', 'graphql'], 'rest': ['rest', 'restful'],
    'distributed-systems': ['distributed systems', 'distributed system'],
    'nodejs': ['node.js', 'nodejs', 'node'], 'nextjs': ['next.js', 'nextjs'],
    'observability': ['observability', 'opentelemetry', 'tracing'],
    'reliability': ['reliability', 'sre', 'slo', 'slos', 'incident response', 'on-call'],
    'data-engineering': ['data engineering', 'etl', 'data pipeline', 'data pipelines'],
    'multi-tenancy': ['multi-tenant', 'multi-tenancy', 'multitenant'],
    'drf': ['django rest framework', 'drf'], 'aws': ['aws', 'amazon web services'],
    'gitops': ['gitops'], 'rag': ['rag', 'retrieval augmented', 'retrieval-augmented'],
    'trading': ['trading', 'exchange', 'order execution', 'market data'],
    'fintech': ['fintech', 'financial', 'payments', 'banking'],
    'infrastructure': ['infrastructure', 'infrastructure as code', 'iac'],
    'agents': ['ai agents', 'agentic', 'llm agents'], 'inference': ['inference', 'model serving'],
    'async': ['async', 'asyncio'], 'microservices': ['microservices', 'microservice'],
}
# Tags too generic to discriminate between postings.
SKIP_TAGS = {'ownership', 'process', 'collaboration', 'quality', 'standards', 'safety',
             'correctness', 'maintainability', 'clean-code', 'documentation', 'leadership',
             'mentoring', 'scale', 'operations', 'api', 'tooling', 'resilience',
             'product-engineering', 'developer-experience', 'architecture', 'debugging'}
# Common JD words that say little on their own: counted, but at weight 1.
GENERIC = {'frontend', 'automation', 'performance', 'testing', 'security', 'monitoring',
           'deployment', 'databases', 'networking', 'algorithms', 'concurrency', 'cloud',
           'integrations', 'storage', 'scheduling', 'fullstack', 'javascript'}
# Skills-section names that are ordinary English words or noise in a JD.
SKIP_NAMES = {'go', 'regex', 'latex', 'markdown', 'linux', 'oop', 'agile', 'scrum', 'figma',
              'concurrency', 'algorithms', 'design patterns', 'clean code', 'web crawling',
              'responsive design', 'responsive ui', 'tls', 'dns', 'smtp', 'tcp', 'ip', 'http'}


# ---------------------------------------------------------------------------
# Resume profile
# ---------------------------------------------------------------------------
def load_profile(path=ROOT / 'data/master.yaml'):
    """Return {canonical_skill: (weight, [regex patterns])} from master.yaml."""
    d = yaml.safe_load(Path(path).read_text())
    counts = {}

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get('tags'), list):
                for t in x['tags']:
                    counts[t] = counts.get(t, 0) + 1
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(d.get('experience', []) + d.get('projects', []))
    skills = {}
    for tag, n in counts.items():
        if tag in SKIP_TAGS:
            continue
        terms = SYNONYMS.get(tag, [tag.replace('-', ' ')])
        skills[tag] = [1 if tag in GENERIC else 1 + min(n, 20) / 5, terms]
    # Named tools from the skills section count too, at a flat weight.
    for items in (d.get('skills') or {}).values():
        for item in items:
            for part in re.split(r'[/,+]', re.sub(r'\(.*?\)', '', item)):
                name = part.strip()
                key = name.lower()
                if len(key) < 2 or key in SKIP_NAMES or key in skills or any(key in t for _, t in skills.values()):
                    continue
                skills[key] = [1.5, [key]]
    return {k: (w, [_term_re(t) for t in terms]) for k, (w, terms) in skills.items()}


def _term_re(term):
    return re.compile(r'(?<![\w.])' + re.escape(term.lower()) + r'(?![\w])')


# ---------------------------------------------------------------------------
# Fetchers. Each returns a list of normalised dicts.
# ---------------------------------------------------------------------------
def _get(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')


def _job(source, title, company, url, location='', tags=(), description='', posted='',
         salary=''):
    return {'source': source, 'title': _clean(title), 'company': _clean(company),
            'url': url, 'location': _clean(location), 'tags': [str(t) for t in tags],
            'description': _clean(description), 'posted': posted, 'salary': salary}


def _clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', str(s or '')))
    return re.sub(r'\s+', ' ', s).strip()


def parse_remoteok(text):
    out = []
    for j in json.loads(text):
        if not isinstance(j, dict) or 'position' not in j:
            continue  # first element is the legal notice
        sal = ''
        if j.get('salary_min'):
            hi = j.get('salary_max') or j['salary_min']
            sal = f"${j['salary_min']} - ${hi} per year"
        out.append(_job('remoteok', j.get('position'), j.get('company'),
                        j.get('url') or f"https://remoteok.com/remote-jobs/{j.get('id')}",
                        j.get('location'), j.get('tags') or [], j.get('description'),
                        (j.get('date') or '')[:10], sal))
    return out


def parse_remotive(text):
    return [_job('remotive', j.get('title'), j.get('company_name'), j.get('url'),
                 j.get('candidate_required_location'), j.get('tags') or [],
                 j.get('description'), (j.get('publication_date') or '')[:10],
                 j.get('salary') or '')
            for j in json.loads(text).get('jobs', [])]


def parse_wwr(text):
    out = []
    for item in ET.fromstring(text).iter('item'):
        g = lambda k: (item.findtext(k) or '').strip()
        company, _, title = g('title').partition(': ')
        if not title:
            company, title = '', company
        posted = ''
        try:
            posted = datetime.strptime(g('pubDate')[:25], '%a, %d %b %Y %H:%M:%S').date().isoformat()
        except ValueError:
            pass
        out.append(_job('wwr', title, company, g('link'), g('region'),
                        [g('category')] if g('category') else [], g('description'), posted))
    return out


def parse_hn_comment(c, thread_id=None):
    """A top-level 'Who is hiring' comment. Convention: 'Company | Role | Location | ...'."""
    raw = c.get('text') or ''
    first = _clean(re.split(r'<p>', raw, maxsplit=1)[0])
    body = _clean(raw)
    parts = [p.strip() for p in first.split('|')]
    company = parts[0] if parts else ''
    role_re = re.compile(ENGINEER + r'|' + SENIORITY[0], re.I)
    title = next((p for p in parts[1:] if role_re.search(p)), ' | '.join(parts[1:3]))
    # Every other header field except links and pay is treated as location text.
    skip = re.compile(r'https?://|www\.|\$|€|£|\bsalary\b', re.I)
    location = ' | '.join(p for p in parts[1:] if p != title and not skip.search(p))
    posted = (c.get('created_at') or '')[:10]
    return _job('hn', title or first[:80], company,
                f"https://news.ycombinator.com/item?id={c.get('id')}",
                location, [], body, posted)


def fetch_remoteok():
    return parse_remoteok(_get('https://remoteok.com/api'))


def fetch_remotive():
    out = []
    for cat in ('software-dev', 'devops', 'data'):
        out += parse_remotive(_get(f'https://remotive.com/api/remote-jobs?category={cat}'))
    return out


WWR_FEEDS = ('remote-back-end-programming-jobs', 'remote-devops-sysadmin-jobs',
             'remote-full-stack-programming-jobs')


def fetch_wwr():
    out = []
    for feed in WWR_FEEDS:
        out += parse_wwr(_get(f'https://weworkremotely.com/categories/{feed}.rss'))
    return out


def fetch_hn():
    """Latest 'Ask HN: Who is hiring?' thread; comments mentioning remote work or visas."""
    hits = json.loads(_get('https://hn.algolia.com/api/v1/search_by_date'
                           '?tags=story,author_whoishiring&hitsPerPage=10'))['hits']
    story = next(h for h in hits if 'who is hiring' in h['title'].lower())
    thread = json.loads(_get(f"https://hn.algolia.com/api/v1/items/{story['objectID']}",
                             timeout=90))
    return [parse_hn_comment(c) for c in thread.get('children', [])
            if c.get('text') and re.search(r'\bremote\b|\bvisa', c['text'], re.I)]


FETCHERS = {'remoteok': fetch_remoteok, 'remotive': fetch_remotive,
            'wwr': fetch_wwr, 'hn': fetch_hn}


# ---------------------------------------------------------------------------
# Criteria file: the numbers and labels come from docs/job-search-criteria.md
# ---------------------------------------------------------------------------
CRITERIA_PATH = ROOT / 'docs/job-search-criteria.md'
_WORDS = {w: i for i, w in enumerate(
    'zero one two three four five six seven eight nine ten eleven twelve thirteen '
    'fourteen'.split())}


def load_criteria(path=CRITERIA_PATH):
    """Pull the machine-checkable values out of the prose brief; fail loudly if absent."""
    text = re.sub(r'\s+', ' ', Path(path).read_text())

    def need(rx, what):
        m = re.search(rx, text, re.I)
        if not m:
            raise SystemExit(f'{path}: could not find {what} (pattern {rx!r})')
        return m

    money = lambda m: int(m.group(1).replace(',', ''))
    days = need(r'publication date within the preceding (\w+) days', 'freshness window').group(1)
    labels = re.findall(r'- (Confirmed-compatible|Conditional|Low-priority/unverified|Excluded):',
                        text)
    if len(labels) != 4:
        raise SystemExit(f'{path}: expected the four priority labels, found {labels}')
    return {
        'min_full_time': money(need(r'Full-time: minimum USD ([\d,]+) gross per month',
                                    'full-time minimum')),
        'min_part_time': money(need(r'Part-time: minimum USD ([\d,]+) gross per month',
                                    'part-time minimum')),
        'fresh_days': int(days) if days.isdigit() else _WORDS[days.lower()],
        'labels': labels,
    }


# ---------------------------------------------------------------------------
# Compensation
# ---------------------------------------------------------------------------
_MONEY = re.compile(
    r'(?<![A-Za-z])(?:usd\s?|us\$|\$)\s?(\d[\d,]*(?:\.\d+)?)\s?(k)?(?![\d.]*\s?(?:m|mm|b|bn|'
    r'million|billion)\b)'
    r'(?:\s?(?:-|–|to)\s?(?:usd\s?|us\$|\$)?\s?(\d[\d,]*(?:\.\d+)?)\s?(k)?)?'
    r'\s*(/\s?(?:hr|hour|h|mo|month|yr|year|annum)|per (?:hour|month|year|annum)|an hour|a year|'
    r'monthly|annually|hourly)?', re.I)


def parse_comp(text, part_time=False):
    """Return (max monthly USD or None, readable basis). None means unverified.

    Only USD amounts are read; other currencies stay unverified rather than being
    converted at a guessed rate. Part-time annual or hourly figures are not converted,
    because the criteria forbid treating a full-time-equivalent as the monthly amount.
    """
    best = None
    for m in _MONEY.finditer(text or ''):
        lo, lo_k, hi, hi_k, unit = m.groups()
        val = float((hi or lo).replace(',', '')) * (1000 if (hi_k or (lo_k and not hi)) else 1)
        unit = (unit or '').lower()
        if 'h' in unit and 'month' not in unit or unit == 'hourly':
            if part_time:
                continue
            monthly, basis = val * 160, f'${val:,.0f}/h x 160h'
        elif 'mo' in unit:
            monthly, basis = val, f'${val:,.0f}/month'
        elif 'y' in unit or 'ann' in unit or val >= 20000:
            if part_time:
                continue
            monthly, basis = val / 12, f'${val:,.0f}/year'
        else:
            continue                      # bare small number: unit unknown
        if monthly < 300:
            continue                      # too small to be a salary: likely a price or fee
        if best is None or monthly > best[0]:
            best = (round(monthly), basis)
    return best or (None, '')


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def tech_fit(job, profile):
    title = job['title'].lower()
    hay = ' '.join([title, ' '.join(job['tags']).lower(), job['description'].lower()])
    fam_hits = [(f, w) for f, (rx, w) in FAMILIES.items() if re.search(rx, title)]
    title_pts = max((w for _, w in fam_hits), default=0)
    if len(fam_hits) > 1:
        title_pts += 5                       # e.g. "Senior Python Platform Engineer"
    if re.search(SENIORITY[0], title):
        title_pts += SENIORITY[1]
    if not re.search(ENGINEER, title) and job['source'] != 'hn':
        title_pts = title_pts // 2
    title_pts = min(title_pts, 40)

    matched, got = [], 0.0
    for skill, (w, pats) in profile.items():
        if any(p.search(hay) for p in pats):
            matched.append((w, skill))
            got += w
    # Saturating: ~25 weight-points of overlap is a full-marks match.
    skill_pts = round(45 * min(got / 25, 1), 1)
    return {'fit': round(title_pts + skill_pts, 1), 'title_pts': title_pts,
            'skill_pts': skill_pts, 'family': '+'.join(f for f, _ in fam_hits) or '-',
            'matched_skills': ', '.join(s for _, s in sorted(matched, reverse=True)[:10])}


def _days_old(posted, today):
    try:
        return (today - datetime.strptime(posted[:10], '%Y-%m-%d').date()).days
    except ValueError:
        return None


def evaluate(job, profile, crit, today):
    fit = tech_fit(job, profile)
    title = job['title'].lower()
    body = ' '.join([title, ' '.join(job['tags']).lower(), job['description'].lower()])
    loc = job['location'].lower()
    excluded, questions = [], []

    # Freshness
    age = _days_old(job['posted'], today)
    if age is None:
        excluded.append('no verifiable publication date')
    elif age > crit['fresh_days']:
        excluded.append(f'published {age} days ago (limit {crit["fresh_days"]})')

    # Work arrangement and relocation track
    remote = job['source'] != 'hn' or bool(re.search(REMOTE, loc or body[:300]))
    if re.search(NOT_REMOTE, body):
        remote = False
    visa = bool(re.search(VISA, body)) and not re.search(NO_VISA, body)
    group = 'A' if remote else 'B'
    if not remote and not visa:
        excluded.append('on-site without explicit visa sponsorship')
    if group == 'B':
        questions.append('visa sponsorship for an Iranian applicant not confirmed')

    # Geography: US/Israel-based roles, and location restrictions that leave Iran out
    open_region = bool(re.search(OPEN_REGION, loc))
    if re.search(US_IL, loc) and not open_region:
        excluded.append('role based in the United States or Israel')
        entity = 'US/Israel (from location)'
    else:
        entity = 'unknown'
        questions.append('actual hiring entity and country unknown')

    if re.search(IRAN_EXCLUDED, body):
        iran = 'incompatible'
        excluded.append('posting excludes Iran or sanctioned countries')
    elif re.search(r'\biran\b', loc):
        iran = 'confirmed'
    elif group == 'A' and loc and not open_region and re.search(NOT_IRAN_REGION, loc):
        iran = 'incompatible'
        excluded.append(f'location restricted to: {job["location"][:40]}')
    else:
        iran = 'unknown'
        if group == 'A':
            questions.append('Iran-based work not confirmed')

    # Payment routes, kept separate
    crypto = 'advertised option' if re.search(CRYPTO_PAY, body) else 'unknown'
    b2b = 'advertised option' if re.search(B2B_INVOICE, body) else 'unknown'
    if crypto == b2b == 'unknown' and group == 'A':
        questions.append('payment route unknown')

    # Compensation
    part_time = bool(re.search(PART_TIME, body))
    contract = bool(re.search(r'\b(contract|contractor|freelance)\b', title + ' ' + loc))
    monthly, basis = parse_comp(job['salary'] or '', part_time)
    if monthly is None:
        monthly, basis = parse_comp(job['title'] + ' ' + job['description'][:1500], part_time)
    minimum = crit['min_part_time'] if part_time else crit['min_full_time']
    if monthly is None:
        comp_ok = 'unverified'
        questions.append('compensation undisclosed')
    elif monthly >= minimum:
        comp_ok = 'yes'
    else:
        comp_ok = 'no'
        excluded.append(f'max pay ${monthly:,}/month below ${minimum:,} minimum')

    if re.search(NOT_ENGINEERING, title):
        excluded.append('not an engineering role')

    labels = dict(zip(['confirmed', 'conditional', 'low', 'excluded'], crit['labels']))
    route = 'advertised option' in (crypto, b2b)
    if excluded:
        label = labels['excluded']
    elif iran == 'confirmed' and route and comp_ok == 'yes':
        label = labels['confirmed']
    elif iran == 'confirmed' or route:
        label = labels['conditional']
    else:
        label = labels['low']

    industry = bool(re.search(PREFERRED_INDUSTRY, body))
    low_comp = bool(re.search(LOW_COMPETITION, body))
    why = [f'fit {fit["fit"]:.0f}/85']
    why += [w for w, ok in [('Iran confirmed', iran == 'confirmed'),
                            ('crypto pay', crypto != 'unknown'),
                            ('B2B/invoice', b2b != 'unknown'),
                            ('pay meets minimum', comp_ok == 'yes'),
                            ('preferred industry', industry),
                            ('contract/founding/trial', low_comp)] if ok]
    return {**job, **fit, 'group': group, 'label': label,
            'excluded_reason': '; '.join(excluded),
            'rationale': ', '.join(why),
            'employment': 'part-time' if part_time else ('contract' if contract else 'full-time'),
            'comp_monthly_usd_max': monthly or '', 'comp_basis': basis,
            'comp_meets_min': comp_ok, 'iran_eligibility': iran,
            'crypto_pay': crypto, 'b2b_invoice': b2b,
            'payment_route': 'advertised option' if route else 'unknown',
            'visa_sponsorship': 'advertised' if visa else 'no',
            'hiring_entity': entity, 'days_old': '' if age is None else age,
            'preferred_industry': 'yes' if industry else '',
            'low_competition_signal': 'yes' if low_comp else '',
            'open_questions': '; '.join(questions)}


def rank_key(r, crit):
    """Label first, then the criteria's RANKING order as far as a feed can show it."""
    return (crit['labels'].index(r['label']), r['group'],
            -(r['iran_eligibility'] == 'confirmed') - (r['payment_route'] != 'unknown'),
            -(r['comp_meets_min'] == 'yes'), -r['fit'],
            -(r['preferred_industry'] == 'yes'), -(r['low_competition_signal'] == 'yes'))


def dedupe(jobs):
    seen, out = set(), []
    for j in jobs:
        key = (re.sub(r'\W+', '', j['company'].lower()), re.sub(r'\W+', '', j['title'].lower()))
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out


COLUMNS = ['group', 'label', 'rationale', 'excluded_reason', 'title', 'company', 'url',
           'posted', 'days_old', 'employment', 'comp_monthly_usd_max', 'comp_basis',
           'comp_meets_min', 'iran_eligibility', 'payment_route', 'crypto_pay', 'b2b_invoice',
           'visa_sponsorship', 'hiring_entity', 'location', 'fit', 'family', 'matched_skills',
           'preferred_industry', 'low_competition_signal', 'open_questions', 'source',
           'title_pts', 'skill_pts']


def _md(v):
    return str(v).replace('|', '/').replace('\n', ' ')


def write_report(path, rows, crit, today):
    keep = [r for r in rows if r['label'] != crit['labels'][-1]]
    gone = [r for r in rows if r['label'] == crit['labels'][-1]]
    out = [f'# Job scan {today.isoformat()}', '',
           f'Criteria: `docs/job-search-criteria.md` (full-time minimum ${crit["min_full_time"]:,}'
           f'/month, part-time ${crit["min_part_time"]:,}/month, published within '
           f'{crit["fresh_days"]} days). {len(keep)} kept, {len(gone)} excluded.', '',
           'Everything below is read from the posting text only. "unknown" means the posting '
           'is silent, not that the answer is no; each item still needs confirmation from the '
           'company before applying.', '']
    head = ['Label', 'Role', 'Company', 'Posted', 'Type', 'Pay/month (max)', 'Meets min',
            'Iran work', 'Payment route', 'Fit', 'Open questions']
    for group, name in [('A', 'A. Remote vacancies'), ('B', 'B. Sponsored-relocation vacancies')]:
        g = [r for r in keep if r['group'] == group]
        out += [f'## {name} ({len(g)})', '']
        if not g:
            out += ['None this run.', '']
            continue
        out += ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
        for r in g:
            pay = f'${r["comp_monthly_usd_max"]:,}' if r['comp_monthly_usd_max'] else '-'
            route = ', '.join(k for k, c in [('crypto', 'crypto_pay'), ('B2B', 'b2b_invoice')]
                              if r[c] != 'unknown') or 'unknown'
            out.append('| ' + ' | '.join(_md(x) for x in [
                r['label'], f'[{r["title"][:60]}]({r["url"]})', r['company'][:30], r['posted'],
                r['employment'], pay, r['comp_meets_min'], r['iran_eligibility'], route,
                f'{r["fit"]:.0f}', r['open_questions']]) + ' |')
        out.append('')
    out += ['## C. Outreach companies', '',
            'Not produced by the scraper: this track needs sourced research on each company.', '',
            '## Excluded', '', '| Reason | Count |', '|---|---|']
    counts = {}
    for r in gone:
        for reason in r['excluded_reason'].split('; '):
            key = re.sub(r'\d+', 'N', reason) if 'published' in reason or 'max pay' in reason \
                else reason
            key = key.split(':')[0]
            counts[key] = counts.get(key, 0) + 1
    out += [f'| {k} | {v} |' for k, v in sorted(counts.items(), key=lambda kv: -kv[1])]
    Path(path).write_text('\n'.join(out) + '\n')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sources', default=','.join(FETCHERS))
    ap.add_argument('--out', default=str(ROOT / 'out/jobs'))
    ap.add_argument('--top', type=int, default=25, help='rows printed to stdout')
    ap.add_argument('--cache', help='score a raw.json from a previous run instead of fetching')
    ap.add_argument('--criteria', default=str(CRITERIA_PATH))
    ap.add_argument('--today', help='run date YYYY-MM-DD for the freshness rule (default: today, UTC)')
    a = ap.parse_args(argv)

    crit = load_criteria(a.criteria)
    today = (datetime.strptime(a.today, '%Y-%m-%d').date() if a.today
             else datetime.now(timezone.utc).date())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.cache:
        raw = json.loads(Path(a.cache).read_text())
    else:
        raw = []
        for name in a.sources.split(','):
            t = time.time()
            try:
                got = FETCHERS[name.strip()]()
                print(f'{name:9} {len(got):4} listings  ({time.time() - t:.1f}s)', file=sys.stderr)
                raw += got
            except Exception as e:           # one dead source should not sink the run
                print(f'{name:9} FAILED: {e}', file=sys.stderr)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')
        (out / f'raw-{stamp}.json').write_text(json.dumps(raw))
        (out / 'raw.json').write_text(json.dumps(raw))

    profile = load_profile()
    rows = sorted((evaluate(j, profile, crit, today) for j in dedupe(raw)),
                  key=lambda r: rank_key(r, crit))

    with open(out / 'ranked.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    write_report(out / 'report.md', rows, crit, today)

    kept = [r for r in rows if r['label'] != crit['labels'][-1]]
    print(f'\n{len(kept)} kept, {len(rows) - len(kept)} excluded -> {out / "report.md"}\n')
    print(f'{"grp":3}  {"label":24}  {"fit":>3}  {"title":40}  {"company":20}  pay')
    for r in kept[:a.top]:
        print(f'{r["group"]:3}  {r["label"]:24}  {r["fit"]:3.0f}  {r["title"][:40]:40}  '
              f'{r["company"][:20]:20}  {r["comp_meets_min"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
