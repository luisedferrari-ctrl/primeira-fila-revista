"""Offline regression checks for ENTRESSALA's post-November 23 Instagram image policy."""
import copy
import unittest

from PIL import Image

import render_social as ed


def slide(filename, tier='mass'):
    return {
        'title': 'Evento real', 'eyebrow': 'AGENDA', 'subtitle': 'Bilheteria oficial',
        'file': filename, 'asset_type': 'photo',
        'photographer': 'Autor verificado', 'year': '2025',
        'license': 'CC BY 4.0',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'rights_checked_at': '2026-11-22',
        'context': 'FOTO DE ARQUIVO · ARTISTA',
        'date_label': '24 NOV 2026',
        'city': 'SÃO PAULO',
        'appeal_tier': tier,
        'depicts': 'Artista realmente anunciado',
        'specific_to_subject': True,
    }


def post(identifier, date='2026-11-24', slides=None):
    return {
        'id': identifier, 'publish_local_date': date,
        'valid_through_local_date': '2026-11-30',
        'approved': True, 'eligibleForScheduling': True,
        'caption': 'Veja a programação verificada.',
        'slides': slides if slides is not None else [slide('Fotografia A.jpg')],
    }


def history():
    return {'version': 1, 'effective_from': '2026-11-23',
            'used_sources': {}, 'visual_hashes': {}}


class EditorialImagePolicyTest(unittest.TestCase):
    def test_historical_duplicate_remains_readable_without_new_permission(self):
        historic = post('ANTIGO', '2026-11-18',
                        [slide('Foto antiga.jpg'), slide('Foto antiga.jpg')])
        self.assertTrue(ed.validate(historic))
        seen = ed.check_image_uniqueness({'posts': [historic]}, history())
        self.assertEqual(seen['commons:foto antiga.jpg']['post_id'], 'ANTIGO')

    def test_future_cannot_reuse_historical_photo(self):
        historic = post('ANTIGO', '2026-11-18', [slide('Eddie Vedder 2018.jpg')])
        fresh = post('NOVO', slides=[slide('Eddie_Vedder_2018.jpg')])
        with self.assertRaisesRegex(ValueError, 'Previously used image'):
            ed.check_image_uniqueness({'posts': [historic, fresh]}, history())

    def test_future_cannot_repeat_image_inside_carousel(self):
        p = post('NOVO', slides=[slide('Foto A.jpg'), slide('Foto_A.jpg')])
        with self.assertRaisesRegex(ValueError, 'INSIDE carousel'):
            ed.check_image_uniqueness({'posts': [p]}, history())

    def test_future_may_use_two_distinct_photos_same_artist(self):
        p = post('NOVO', slides=[slide('Artista show um.jpg'),
                                slide('Artista show dois.jpg')])
        self.assertTrue(ed.validate(p))
        self.assertEqual(len(ed.check_image_uniqueness({'posts': [p]}, history())), 2)

    def test_missing_date_or_city_blocks_new_post(self):
        p = post('NOVO')
        for field in ('date_label', 'city'):
            changed = copy.deepcopy(p)
            del changed['slides'][0][field]
            with self.assertRaisesRegex(ValueError, 'DATE and CITY'):
                ed.validate(changed)

    def test_generic_photo_blocks_new_post(self):
        p = post('NOVO')
        p['slides'][0]['specific_to_subject'] = False
        with self.assertRaisesRegex(ValueError, 'Generic or unverified'):
            ed.validate(p)

    def test_unrelated_venue_photo_blocks_new_post(self):
        p = post('NOVO')
        p['slides'][0]['context'] = 'FOTO DO LOCAL · ARQUIVO'
        with self.assertRaisesRegex(ValueError, 'Generic venue'):
            ed.validate(p)

    def test_secondary_at_end_only(self):
        p = post('NOVO', slides=[slide('A.jpg', 'secondary'),
                                slide('B.jpg', 'mass')])
        with self.assertRaisesRegex(ValueError, 'Mass attraction after secondary'):
            ed.validate(p)

    def test_authorized_poster_requires_documented_permission(self):
        p = post('NOVO')
        s = p['slides'][0]
        s.pop('file')
        s.update(asset_type='official_poster',
                 image_url='https://example.org/poster.jpg',
                 source_page_url='https://example.org/show',
                 license='PERMISSAO EDITORIAL',
                 instagram_use_allowed=True)
        with self.assertRaisesRegex(ValueError, 'documented republication rights'):
            ed.validate(p)
        s['permission_evidence_url'] = 'https://example.org/media-permissions'
        self.assertTrue(ed.validate(p))

    def test_authorized_photo_allowed_with_permission(self):
        p = post('NOVO')
        s = p['slides'][0]
        s.pop('file')
        s.update(asset_type='authorized_photo',
                 image_url='https://cdn.example.org/artist.jpg',
                 source_page_url='https://example.org/artist',
                 permission_evidence_url='https://example.org/press-terms',
                 license='PERMISSAO EDITORIAL',
                 instagram_use_allowed=True)
        self.assertTrue(ed.validate(p))
        self.assertEqual(ed.image_key(s), 'authorized_photo:https://cdn.example.org/artist.jpg')

    def test_different_url_query_not_duplicate_photo(self):
        p = post('NOVO', slides=[slide('A.jpg'), slide('B.jpg')])
        a = p['slides'][0]
        b = p['slides'][1]
        for s, query in ((a, '?size=small'), (b, '?size=big')):
            s.pop('file')
            s.update(asset_type='authorized_photo',
                     image_url='https://cdn.example.org/image.jpg' + query,
                     source_page_url='https://example.org/show',
                     permission_evidence_url='https://example.org/permission',
                     instagram_use_allowed=True, license='PERMISSAO EDITORIAL')
        with self.assertRaisesRegex(ValueError, 'INSIDE carousel'):
            ed.check_image_uniqueness({'posts': [p]}, history())

    def test_visual_duplicate_with_changed_filename_blocks(self):
        p = post('NOVO', slides=[slide('Foto A.jpg'), slide('Foto B.jpg')])
        hist = history()
        img = Image.new('RGB', (1000, 850), (100, 50, 20))
        ed.register_visual_hash(img, p['slides'][0], p, 1, hist)
        with self.assertRaisesRegex(ValueError, 'near-identical photo'):
            ed.register_visual_hash(img.copy(), p['slides'][1], p, 2, hist)

    def test_own_registry_entry_does_not_break_idempotent_rerender(self):
        p = post('NOVO')
        key = ed.image_key(p['slides'][0])
        hist = history()
        hist['used_sources'][key] = {'post_id': 'NOVO', 'publish_local_date': '2026-11-24'}
        seen = ed.check_image_uniqueness({'posts': [p]}, hist)
        self.assertEqual(seen[key]['post_id'], 'NOVO')


if __name__ == '__main__':
    unittest.main()
