"""Verify privacy, pagination, and failure handling without network access."""
import importlib.util
import json
from pathlib import Path
import shutil
import unittest
import uuid
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('collector',Path(__file__).resolve().parents[1]/'scripts/collect_stats.py')
collector=importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

def repo(i,name=None,private=False,fork=False,owner='Abhi-lash19'):
    name=name or f'project-{i}'
    return {'id':i,'name':name,'private':private,'fork':fork,'archived':False,'language':'Python','owner':{'login':owner},'html_url':f'https://github.com/{owner}/{name}'}

class CollectorTests(unittest.TestCase):
    def setUp(self):
        temporary_parent=Path(__file__).resolve().parents[1]/'.preview'
        temporary_parent.mkdir(exist_ok=True)
        self.root=temporary_parent/('test-'+uuid.uuid4().hex)
        self.root.mkdir()
        assert self.root.resolve().is_relative_to(temporary_parent.resolve())
        self.addCleanup(shutil.rmtree,self.root)
        (self.root/'data').mkdir()
        self.file=self.root/'data/github-stats.json'
    def run_collector(self,fetch):
        with patch.object(collector,'ROOT',self.root),patch.object(collector,'get',side_effect=fetch):
            collector.collect()
        return json.loads(self.file.read_text())
    def test_pagination_collects_beyond_first_hundred(self):
        calls=[]
        def fetch(path):
            calls.append(path)
            if '/languages' in path:return {'Python':12}
            return [repo(i) for i in range(100)] if path.endswith('&page=1') else [repo(100)]
        result=self.run_collector(fetch)
        self.assertEqual(len(result['repositories']),101)
        self.assertTrue(any('page=2' in p for p in calls))
    def test_private_and_foreign_repositories_never_enter_snapshot(self):
        def fetch(path):
            if '/languages' in path:return {'Python':12}
            return [repo(1,'Abhi-lash19'),repo(2,'fork',fork=True),repo(3,'public'),repo(4,'private',private=True),repo(5,'foreign',owner='another-user')]
        result=self.run_collector(fetch)
        self.assertEqual([r['name'] for r in result['repositories']],['Abhi-lash19','fork','public'])
        self.assertEqual([r['name'] for r in result['repositories'] if r['project']],['public'])
    def test_failed_language_request_preserves_previous_snapshot(self):
        original='{"saved":"last good snapshot"}\n'
        self.file.write_text(original)
        def fetch(path):
            if '/languages' in path:raise OSError('network failure')
            return [repo(1)]
        with self.assertRaises(OSError):self.run_collector(fetch)
        self.assertEqual(self.file.read_text(),original)

if __name__=='__main__':unittest.main()
