import sys
import unittest
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from collect_commits import USER, snapshot


class CommitCollectionTests(unittest.TestCase):
    def test_pinned_pagination_identity_visibility_and_elapsed_months(self):
        def repo(name, **change):
            return dict({'name':name,'owner':{'id':1},'default_branch':'trunk',
                         'private':False,'fork':False}, **change)

        def commit(i, date='2026-04-01T00:00:00Z', author=1):
            return {'sha':f'{i:040x}','author':{'id':author},'commit':{'author':{'date':date}}}

        calls = []
        def fetch(url):
            path = urlsplit(url).path
            q = parse_qs(urlsplit(url).query)
            if path == f'/users/{USER}':
                return {'id':1}
            if path.endswith('/repos'):
                return [repo('one'),repo('two'),repo('hidden',private=True),
                        repo('fork',fork=True),repo('foreign',owner={'id':2})]
            name = path.split('/')[3]
            self.assertIn(name, ('one','two'))
            if q['sha']==['trunk']:
                return [{'sha':'f'*40}]
            self.assertEqual(q['sha'], ['f'*40])
            self.assertEqual(q['author'], [USER])
            calls.append((name,q['page'][0]))
            if name=='two':
                return [commit(1)]  # Same object reachable in both repositories.
            if q['page']==['1']:
                return [commit(i) for i in range(1,101)]
            return [commit(101,'2025-12-31T19:00:00Z'),  # Jan 1 in Kolkata
                    commit(102,'2025-12-01T00:00:00Z'),commit(103,author=2),
                    commit(104,'2027-01-01T00:00:00Z')]

        result = snapshot(fetch, datetime.fromisoformat('2026-10-31T10:00:00+05:30'))
        self.assertIn(('one','2'),calls)
        self.assertEqual(result['lifetime'],102)
        self.assertEqual(result['year_to_date'],101)
        self.assertEqual(result['monthly_counts'][0],1)
        self.assertEqual(result['monthly_average'],10.1)

    def test_incomplete_api_read_is_an_error(self):
        def failure(path):
            if path == f'/users/{USER}': return {'id':1}
            raise OSError('repository inventory unavailable')
        with self.assertRaises(OSError):
            snapshot(failure,datetime.fromisoformat('2026-10-31T10:00:00+05:30'))
