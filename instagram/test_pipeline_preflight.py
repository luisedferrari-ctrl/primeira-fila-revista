import json
import pathlib
import tempfile
import unittest
from pipeline_preflight import latest_edition, inspect_queue, SITE
from test_image_policy import post


class PipelinePreflightTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.edition('2026-11-19')

    def edition(self, day, status='PUBLISHED'):
        folder = self.root / 'edicoes' / day
        (folder / 'dados').mkdir(parents=True)
        (folder / 'materias' / 'blues').mkdir(parents=True)
        (folder / 'index.html').write_text('edition')
        (folder / 'materias' / 'blues' / 'index.html').write_text('article')
        (folder / 'dados' / ('edicao-' + day + '.json')).write_text(json.dumps({
            'id': 'EC-' + day, 'date': day, 'status': status,
            'publicUrl': SITE + '/edicoes/' + day + '/',
            'publishedVerifiedAt': day, 'publicationEvidence': 'recorded-smoke-run'}))

    def queue(self, items):
        return {'brand': 'ENTRESSALA', 'channel': '@entressala_', 'posts': items}

    def test_resolves_main_without_social_queue(self):
        self.assertEqual(latest_edition(self.root, '2026-11-24')['id'], 'EC-2026-11-19')

    def test_future_and_draft_do_not_replace_published(self):
        self.edition('2026-11-26')
        self.edition('2026-11-23', 'DRAFT')
        self.assertEqual(latest_edition(self.root, '2026-11-24')['id'], 'EC-2026-11-19')

    def test_unavailable_source_is_explicit_failure(self):
        with self.assertRaisesRegex(ValueError, 'NO_PUBLISHED_EDITION_IN_MAIN'):
            latest_edition(self.root / 'missing', '2026-11-24')

    def test_missing_article_blocks_source(self):
        (self.root / 'edicoes/2026-11-19/materias/blues/index.html').unlink()
        with self.assertRaisesRegex(ValueError, 'no articles'):
            latest_edition(self.root, '2026-11-24')

    def test_no_candidate_is_not_green_render(self):
        with self.assertRaisesRegex(ValueError, 'EDITORIAL_BLOCKED'):
            inspect_queue(self.queue([]), latest_edition(self.root, '2026-11-24'), '2026-11-24')

    def test_one_photo_is_valid_not_four_photo_minimum(self):
        self.assertEqual(inspect_queue(self.queue([post('ONE')]), latest_edition(self.root, '2026-11-24'), '2026-11-24'), 'ONE')

    def test_wrong_edition_is_rejected(self):
        p = post('WRONG'); p['source_edition_id'] = 'EC-2026-11-17'
        with self.assertRaisesRegex(ValueError, 'latest published'):
            inspect_queue(self.queue([p]), latest_edition(self.root, '2026-11-24'), '2026-11-24')

    def test_nonexistent_article_is_rejected(self):
        p = post('WRONG'); p['source_article_url'] = SITE + '/edicoes/2026-11-19/materias/absent/'
        with self.assertRaisesRegex(ValueError, 'not present'):
            inspect_queue(self.queue([p]), latest_edition(self.root, '2026-11-24'), '2026-11-24')

    def test_old_factcheck_is_rejected(self):
        p = post('STALE'); p['verified_at'] = '2026-11-19'
        with self.assertRaisesRegex(ValueError, 'stale'):
            inspect_queue(self.queue([p]), latest_edition(self.root, '2026-11-24'), '2026-11-24')
