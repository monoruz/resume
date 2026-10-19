"""Parser and scoring tests. Payloads mirror each source's public response shape.

Run: python3 -m unittest discover scraper
"""
import json, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import jobs

REMOTEOK = json.dumps([
    {'legal': 'API terms notice'},
    {'id': '1', 'date': '2026-10-18T10:00:00+00:00', 'company': 'Acme',
     'position': 'Senior Python Backend Engineer', 'tags': ['python', 'django', 'postgres'],
     'description': '<p>Django, Celery, Redis, PostgreSQL, Kubernetes. Remote worldwide.</p>',
     'location': 'Worldwide', 'salary_min': 90000, 'salary_max': 130000,
     'url': 'https://remoteok.com/remote-jobs/1'},
])
REMOTIVE = json.dumps({'jobs': [
    {'id': 7, 'url': 'https://remotive.com/j/7', 'title': 'Site Reliability Engineer',
     'company_name': 'Ops Co', 'tags': ['kubernetes', 'terraform'],
     'publication_date': '2026-10-17T00:00:00', 'candidate_required_location': 'USA only',
     'salary': '', 'description': 'Kubernetes, Terraform, Prometheus, Grafana.'},
]})
WWR = """<?xml version="1.0"?><rss><channel><item>
<title>Ledger Labs: Platform Engineer (LLM Inference)</title>
<region>Anywhere in the World</region><category>DevOps and Sysadmin</category>
<pubDate>Sat, 18 Oct 2026 12:00:00 +0000</pubDate>
<link>https://weworkremotely.com/remote-jobs/ledger-labs-platform</link>
<description>&lt;p&gt;vLLM, KServe, GPU scheduling on Kubernetes, ArgoCD.&lt;/p&gt;</description>
</item></channel></rss>"""
HN = {'id': 42, 'created_at': '2026-10-01T15:00:00Z',
      'text': 'Quantly | Senior Backend Engineer (Python) | REMOTE (EMEA) | $150k'
              '<p>Trading execution engine in FastAPI, Redis locking, ClickHouse.'}


class Parsers(unittest.TestCase):
    def test_remoteok_skips_legal_row(self):
        (j,) = jobs.parse_remoteok(REMOTEOK)
        self.assertEqual((j['company'], j['salary'], j['posted']), ('Acme', '90000-130000', '2026-10-18'))
        self.assertNotIn('<p>', j['description'])

    def test_remotive(self):
        (j,) = jobs.parse_remotive(REMOTIVE)
        self.assertEqual((j['title'], j['location']), ('Site Reliability Engineer', 'USA only'))

    def test_wwr_splits_company(self):
        (j,) = jobs.parse_wwr(WWR)
        self.assertEqual((j['company'], j['title']), ('Ledger Labs', 'Platform Engineer (LLM Inference)'))
        self.assertEqual(j['posted'], '2026-10-18')
        self.assertIn('vLLM', j['description'])

    def test_hn_pipe_header(self):
        j = jobs.parse_hn_comment(HN)
        self.assertEqual((j['company'], j['title']), ('Quantly', 'Senior Backend Engineer (Python)'))
        self.assertIn('REMOTE (EMEA)', j['location'])
        self.assertTrue(j['url'].endswith('id=42'))


class Scoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = jobs.load_profile()

    def s(self, **kw):
        base = jobs._job('test', kw.pop('title'), 'X', 'u', kw.pop('location', ''),
                         description=kw.pop('description', ''))
        return jobs.score(base, self.profile)

    def test_target_beats_offtarget(self):
        good = self.s(title='Senior Python Backend Engineer', location='Worldwide',
                      description='Django PostgreSQL Redis Celery Kubernetes')
        bad = self.s(title='Senior iOS Engineer', location='Worldwide',
                     description='Swift UIKit')
        self.assertGreater(good['score'], bad['score'] + 40)
        self.assertIn('python', good['matched_skills'])

    def test_location_restriction_penalised(self):
        ww = self.s(title='SRE', location='Worldwide', description='Kubernetes')
        us = self.s(title='SRE', location='US only', description='Kubernetes')
        self.assertEqual((ww['location_fit'], us['location_fit']), ('worldwide', 'restricted'))
        self.assertGreater(ww['score'], us['score'])

    def test_family_tagging(self):
        r = self.s(title='Staff Platform Engineer, LLM Inference')
        self.assertIn('platform-sre', r['family'])
        self.assertIn('ai-infra', r['family'])

    def test_short_terms_need_word_boundary(self):
        r = self.s(title='Engineer', description='We like to go fast and use Scala')
        self.assertNotIn('go', r['matched_skills'].split(', '))

    def test_dedupe(self):
        a = jobs._job('a', 'Backend Engineer', 'Acme Inc', 'u1')
        b = jobs._job('b', 'Backend  Engineer', 'ACME inc.', 'u2')
        self.assertEqual(len(jobs.dedupe([a, b])), 1)

    def test_end_to_end_from_cache(self):
        import tempfile, csv
        raw = (jobs.parse_remoteok(REMOTEOK) + jobs.parse_remotive(REMOTIVE)
               + jobs.parse_wwr(WWR) + [jobs.parse_hn_comment(HN)])
        with tempfile.TemporaryDirectory() as d:
            cache = Path(d) / 'raw.json'
            cache.write_text(json.dumps(raw))
            jobs.main(['--cache', str(cache), '--out', d, '--top', '0'])
            with open(Path(d) / 'ranked.csv') as f:
                rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[-1]['company'], 'Ops Co')   # US-only sinks to the bottom


if __name__ == '__main__':
    unittest.main()
