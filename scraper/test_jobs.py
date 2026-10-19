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
        self.assertEqual((j['company'], j['salary'], j['posted']), ('Acme', '$90000 - $130000 per year', '2026-10-18'))
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


TODAY = jobs.datetime(2026, 10, 20).date()


class Criteria(unittest.TestCase):
    def test_values_come_from_the_brief(self):
        c = jobs.load_criteria()
        self.assertEqual((c['min_full_time'], c['min_part_time'], c['fresh_days']), (3000, 2000, 7))
        self.assertEqual(c['labels'][-1], 'Excluded')

    def test_editing_the_brief_changes_the_rule(self):
        import tempfile
        text = jobs.CRITERIA_PATH.read_text().replace('preceding seven days', 'preceding ten days')
        with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False) as f:
            f.write(text)
        self.assertEqual(jobs.load_criteria(f.name)['fresh_days'], 10)
        Path(f.name).unlink()


class Compensation(unittest.TestCase):
    def test_units(self):
        self.assertEqual(jobs.parse_comp('$120k - $150k')[0], 12500)
        self.assertEqual(jobs.parse_comp('$50/hr')[0], 8000)
        self.assertEqual(jobs.parse_comp('$4,000 per month')[0], 4000)

    def test_funding_amounts_are_not_salary(self):
        self.assertEqual(jobs.parse_comp('We raised $20M from investors'), (None, ''))

    def test_part_time_fte_is_not_monthly_pay(self):
        self.assertIsNone(jobs.parse_comp('$120k', part_time=True)[0])
        self.assertEqual(jobs.parse_comp('$2,500/month', part_time=True)[0], 2500)


class Evaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = jobs.load_profile()
        cls.crit = jobs.load_criteria()

    def e(self, title='Senior Python Backend Engineer', location='Worldwide',
          description='Django PostgreSQL Redis Celery Kubernetes', posted='2026-10-18',
          salary='', source='test'):
        job = jobs._job(source, title, 'X', 'u', location, description=description,
                        posted=posted, salary=salary)
        return jobs.evaluate(job, self.profile, self.crit, TODAY)

    def test_unknowns_stay_low_priority_not_excluded(self):
        r = self.e()
        self.assertEqual(r['label'], 'Low-priority/unverified')
        self.assertEqual((r['comp_meets_min'], r['iran_eligibility'], r['payment_route']),
                         ('unverified', 'unknown', 'unknown'))

    def test_stale_and_undated_excluded(self):
        self.assertIn('published 12 days', self.e(posted='2026-10-08')['excluded_reason'])
        self.assertIn('no verifiable', self.e(posted='')['excluded_reason'])

    def test_low_pay_excluded(self):
        r = self.e(salary='$30,000 per year')
        self.assertEqual(r['label'], 'Excluded')
        self.assertIn('below $3,000', r['excluded_reason'])

    def test_us_and_israel_roles_excluded(self):
        self.assertIn('United States or Israel', self.e(location='USA only')['excluded_reason'])
        self.assertIn('United States or Israel', self.e(location='Tel Aviv')['excluded_reason'])

    def test_other_country_restriction_is_iran_incompatible(self):
        r = self.e(location='Europe only')
        self.assertEqual((r['iran_eligibility'], r['label']), ('incompatible', 'Excluded'))

    def test_emea_is_not_excluded(self):
        self.assertNotEqual(self.e(location='EMEA')['label'], 'Excluded')

    def test_sanctions_clause_excludes(self):
        r = self.e(description='Remote anywhere except Cuba, Iran, North Korea and Syria.')
        self.assertEqual(r['iran_eligibility'], 'incompatible')

    def test_crypto_alone_is_only_conditional(self):
        r = self.e(description='Python. Salary paid in USDC monthly.', salary='$5,000/month')
        self.assertEqual((r['crypto_pay'], r['b2b_invoice']), ('advertised option', 'unknown'))
        self.assertEqual(r['label'], 'Conditional')

    def test_confirmed_needs_iran_payment_and_pay(self):
        r = self.e(location='Worldwide incl. Iran', salary='$5,000/month',
                   description='Python. B2B contract, invoice monthly.')
        self.assertEqual(r['label'], 'Confirmed-compatible')

    def test_onsite_without_visa_excluded_with_visa_group_b(self):
        on = self.e(source='hn', location='Berlin | Onsite', description='Python')
        self.assertIn('without explicit visa', on['excluded_reason'])
        visa = self.e(source='hn', location='Berlin | Onsite', description='We offer visa sponsorship.')
        self.assertEqual((visa['group'], visa['label']), ('B', 'Low-priority/unverified'))

    def test_no_visa_sponsorship_phrase(self):
        r = self.e(source='hn', location='Berlin | Onsite',
                   description='Unfortunately we cannot offer visa sponsorship.')
        self.assertEqual(r['visa_sponsorship'], 'no')

    def test_fit_orders_within_label(self):
        good = self.e()
        bad = self.e(title='iOS Engineer', description='Swift UIKit')
        self.assertGreater(good['fit'], bad['fit'] + 30)
        self.assertNotEqual(bad['label'], 'Excluded')   # no exact-stack exclusions

    def test_non_engineering_excluded(self):
        self.assertIn('not an engineering', self.e(title='Account Executive')['excluded_reason'])

    def test_short_terms_need_word_boundary(self):
        r = self.e(title='Engineer', description='We like to go fast and use Scala')
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
            jobs.main(['--cache', str(cache), '--out', d, '--top', '0', '--today', '2026-10-20'])
            with open(Path(d) / 'ranked.csv') as f:
                rows = {r['company']: r for r in csv.DictReader(f)}
            report = (Path(d) / 'report.md').read_text()
        self.assertEqual(rows['Ops Co']['label'], 'Excluded')        # USA only
        self.assertEqual(rows['Quantly']['label'], 'Excluded')       # HN post is 19 days old
        self.assertEqual(rows['Acme']['comp_meets_min'], 'yes')      # $130k/yr
        self.assertIn('## A. Remote vacancies', report)
        self.assertIn('Ledger Labs', report)


if __name__ == '__main__':
    unittest.main()
