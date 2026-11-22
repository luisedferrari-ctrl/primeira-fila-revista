"""Offline regression checks for ENTRESSALA's Instagram image policy effective November 19."""
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
        'venue_label': 'Teatro Municipal',
        'cta_label': 'Siga @entressala_ para descobrir mais',
    }


def post(identifier, date='2026-11-24', slides=None):
    return {
        'id': identifier, 'publish_local_date': date,
        'valid_through_local_date': '2026-11-30',
        'approved': True, 'eligibleForScheduling': True,
        'caption': ('Um concerto para descobrir.\n\nQUANDO: 24 NOV 2026 · 19H\n'
                    'ONDE: Teatro Municipal, Rua Central 100, São Paulo\n'
                    'INGRESSOS: Entrada gratuita com reserva\n'
                    'LINK OFICIAL: https://example.org/official\n\n'
                    'Siga @entressala_ para descobrir os próximos eventos.'),
        'service_items': [{
            'kind': 'event',
            'when': '24 NOV 2026 · 19H',
            'where': 'Teatro Municipal, Rua Central 100, São Paulo',
            'admission': 'Entrada gratuita com reserva',
            'official_url': 'https://example.org/official',
        }],
        'kind': 'selecao_semana',
        'verified_at': '2026-11-22',
        'factual_sources': ['https://example.org/official'],
        'source_edition_id': 'EC-2026-11-19',
        'source_article_url': 'https://primeira-fila-revista.pages.dev/edicoes/2026-11-19/materias/blues/',
        'slides': slides if slides is not None else [slide('Fotografia A.jpg')],
    }


def history():
    return {'version': 1, 'effective_from': '2026-11-19',
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

    def test_url_query_variation_cannot_bypass_duplicate_detection(self):
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

    def test_new_post_without_source_article_is_blocked(self):
        p = post('NOVO')
        p.pop('source_article_url')
        with self.assertRaisesRegex(ValueError, 'Source edition article'):
            ed.validate(p)
        p = post('NOVO')
        p['source_edition_id'] = 'EC-2026-11-18'
        with self.assertRaisesRegex(ValueError, 'Source edition article'):
            ed.validate(p)

    def test_historical_posts_do_not_require_new_source_fields(self):
        p = post('HISTORICO', date='2026-11-18')
        p.pop('source_edition_id')
        p.pop('source_article_url')
        self.assertTrue(ed.validate(p))

    def test_two_approved_posts_for_same_local_date_are_blocked(self):
        a, b = post('A'), post('B')
        with self.assertRaisesRegex(ValueError, 'More than one approved automatic post'):
            ed.validate_manifest({'brand': 'ENTRESSALA', 'channel': '@entressala_', 'posts': [a, b]})

    def test_missing_event_service_blocks_new_post(self):
        p = post('NOVO')
        p.pop('service_items')
        with self.assertRaisesRegex(ValueError, 'verified service_items'):
            ed.validate(p)

    def test_missing_venue_in_image_blocks_new_post(self):
        p = post('NOVO')
        del p['slides'][0]['venue_label']
        with self.assertRaisesRegex(ValueError, 'Visible VENUE'):
            ed.validate(p)

    def test_missing_follow_cta_in_caption_blocks_new_post(self):
        p = post('NOVO')
        p['caption'] = p['caption'].replace('Siga @entressala_', 'Veja nosso perfil')
        with self.assertRaisesRegex(ValueError, 'Caption must contain'):
            ed.validate(p)

    def test_missing_follow_cta_in_final_slide_blocks_new_post(self):
        p = post('NOVO', slides=[slide('Foto A.jpg'), slide('Foto B.jpg')])
        p['slides'][-1].pop('cta_label')
        with self.assertRaisesRegex(ValueError, 'Last new slide'):
            ed.validate(p)

    def test_missing_ticket_or_official_link_in_caption_blocks_new_post(self):
        p = post('NOVO')
        p['caption'] = p['caption'].replace('Entrada gratuita com reserva', '')
        with self.assertRaisesRegex(ValueError, 'Caption omits verified service admission'):
            ed.validate(p)
        p = post('NOVO')
        p['caption'] = p['caption'].replace('https://example.org/official', '')
        with self.assertRaisesRegex(ValueError, 'Caption omits verified service official_url'):
            ed.validate(p)

    def test_undated_radar_must_say_dates_and_tickets_unannounced(self):
        p = post('RADAR')
        p['service_items'][0]['kind'] = 'radar'
        p['service_items'][0]['when'] = '2027 · DATAS A ANUNCIAR'
        p['service_items'][0]['admission'] = 'INGRESSOS AINDA NÃO DIVULGADOS'
        p['slides'][0]['date_label'] = '2027 · DATAS A ANUNCIAR'
        p['caption'] = ('Exposição no MASP. QUANDO: 2027 · DATAS A ANUNCIAR\n'
                        'ONDE: Teatro Municipal, Rua Central 100, São Paulo\n'
                        'INGRESSOS: INGRESSOS AINDA NÃO DIVULGADOS\n'
                        'LINK OFICIAL: https://example.org/official\n'
                        'Siga @entressala_ para acompanhar a programação.')
        self.assertTrue(ed.validate(p))
        p['service_items'][0]['when'] = '2027 · Em breve'
        p['caption'] = p['caption'].replace('2027 · DATAS A ANUNCIAR', '2027 · Em breve')
        with self.assertRaisesRegex(ValueError, 'Undated radar'):
            ed.validate(p)

    def test_image_service_fields_do_not_apply_retroactively(self):
        p = post('HISTORICO', date='2026-11-18')
        p.pop('service_items')
        p['caption'] = 'Legenda original histórica.'
        p['slides'][0].pop('venue_label')
        p['slides'][0].pop('cta_label')
        self.assertTrue(ed.validate(p))

    def test_weekend_regular_post_is_blocked(self):
        p = post('NOVO-FDS', date='2026-11-21')
        with self.assertRaisesRegex(ValueError, 'Monday-Friday'):
            ed.validate_manifest({'brand': 'ENTRESSALA', 'channel': '@entressala_', 'posts': [p]})


if __name__ == '__main__':
    unittest.main()
