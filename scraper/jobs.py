#!/usr/bin/env python3
"""Collect remote job listings and rank them against data/master.yaml.

Sources (all public, no API key):
  remoteok   https://remoteok.com/api                     JSON
  remotive   https://remotive.com/api/remote-jobs         JSON
  wwr        https://weworkremotely.com/categories/*.rss  RSS
  hn         Hacker News "Who is hiring?" via the Algolia API

Scoring is mechanical and explainable; every row carries the terms that matched.
  title    0-40  best-matching target family (backend, platform/SRE, AI infra, fintech)
  skills   0-45  weighted coverage of resume skills found in title + tags + description
  location -20..+15  worldwide / EMEA-friendly vs. country-restricted
  penalty  title words for roles outside the target (mobile, sales, junior, ...)

Usage:
  python3 scraper/jobs.py                       # all sources -> out/jobs/ranked.csv
  python3 scraper/jobs.py --sources hn,wwr --top 30 --min-score 40
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
    'ai-infra': (r'\b(llm|ai|ml|machine learning|mlops|genai|inference|applied ai)\b', 30),
    'fintech': (r'\b(trading|fintech|exchange|crypto|payments?|quant|defi|brokerage)\b', 20),
}
SENIORITY = (r'\b(senior|sr\.?|staff|lead|principal)\b', 10)
ENGINEER = r'\b(engineer|developer|sre|architect|programmer)\b'
NEGATIVE = (r'\b(ios|android|mobile|swift|kotlin|java(?!script)|\.net|c#|php|ruby|rails|'
            r'salesforce|sap|designer|sales|marketing|recruiter|account executive|'
            r'customer success|support specialist|intern|junior|jr\.?|writer|'
            r'data entry|qa tester|manual qa)\b')

# Location: mono is in Tehran. Worldwide roles are the realistic pool; EMEA and
# timezone-band roles are worth a look; country-restricted roles are pushed down.
LOC_GOOD = r'\b(worldwide|anywhere|global|any location|remote \(global\)|all countries)\b'
LOC_OK = r'\b(emea|europe|middle east|asia|utc[+-]?[0-4]\b|gmt[+-]?[0-4]\b|cet|eet|turkey|uae|dubai)\b'
LOC_BAD = (r'\b(us only|usa only|u\.s\. only|united states|us-based|us based|canada only|'
           r'uk only|must be located in|must reside in|north america|americas|latam|'
           r'us citizens?|security clearance|est|pst|cst)\b')

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
            sal = f"{j['salary_min']}-{j.get('salary_max') or ''}"
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
    loc_re = re.compile(r'remote|onsite|on-site|hybrid|' + LOC_GOOD, re.I)
    location = ' | '.join(p for p in parts[1:] if loc_re.search(p))
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
    """Latest 'Ask HN: Who is hiring?' thread; only comments that mention remote."""
    hits = json.loads(_get('https://hn.algolia.com/api/v1/search_by_date'
                           '?tags=story,author_whoishiring&hitsPerPage=10'))['hits']
    story = next(h for h in hits if 'who is hiring' in h['title'].lower())
    thread = json.loads(_get(f"https://hn.algolia.com/api/v1/items/{story['objectID']}",
                             timeout=90))
    return [parse_hn_comment(c) for c in thread.get('children', [])
            if c.get('text') and re.search(r'\bremote\b', c['text'], re.I)]


FETCHERS = {'remoteok': fetch_remoteok, 'remotive': fetch_remotive,
            'wwr': fetch_wwr, 'hn': fetch_hn}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def score(job, profile):
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

    loc = (job['location'] + ' ' + hay[:600]).lower()
    if re.search(LOC_GOOD, loc):
        loc_pts, loc_tag = 15, 'worldwide'
    elif re.search(LOC_BAD, job['location'].lower() or loc):
        loc_pts, loc_tag = -20, 'restricted'
    elif re.search(LOC_OK, loc):
        loc_pts, loc_tag = 8, 'emea/tz'
    else:
        loc_pts, loc_tag = 0, 'unclear'

    penalty = -30 if re.search(NEGATIVE, title) else 0
    total = round(title_pts + skill_pts + loc_pts + penalty, 1)
    top_skills = [s for _, s in sorted(matched, reverse=True)[:10]]
    return {**job, 'score': total, 'title_pts': title_pts, 'skill_pts': skill_pts,
            'loc_pts': loc_pts, 'location_fit': loc_tag,
            'family': '+'.join(f for f, _ in fam_hits) or '-',
            'matched_skills': ', '.join(top_skills)}


def dedupe(jobs):
    seen, out = set(), []
    for j in jobs:
        key = (re.sub(r'\W+', '', j['company'].lower()), re.sub(r'\W+', '', j['title'].lower()))
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out


COLUMNS = ['score', 'title', 'company', 'family', 'location_fit', 'location', 'salary',
           'matched_skills', 'source', 'posted', 'url',
           'title_pts', 'skill_pts', 'loc_pts']


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sources', default=','.join(FETCHERS))
    ap.add_argument('--out', default=str(ROOT / 'out/jobs'))
    ap.add_argument('--top', type=int, default=25, help='rows printed to stdout')
    ap.add_argument('--min-score', type=float, default=0, help='drop rows below this from the CSV')
    ap.add_argument('--cache', help='score a raw.json from a previous run instead of fetching')
    a = ap.parse_args(argv)

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
    ranked = sorted((score(j, profile) for j in dedupe(raw)), key=lambda r: -r['score'])
    ranked = [r for r in ranked if r['score'] >= a.min_score]

    with open(out / 'ranked.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
        w.writeheader()
        w.writerows(ranked)

    print(f'\n{len(ranked)} ranked -> {out / "ranked.csv"}\n')
    print(f'{"score":>5}  {"location":10}  {"title":45}  {"company":22}  source')
    for r in ranked[:a.top]:
        print(f'{r["score"]:5.0f}  {r["location_fit"]:10}  {r["title"][:45]:45}  '
              f'{r["company"][:22]:22}  {r["source"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
