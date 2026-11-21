#!/usr/bin/env python3
"""Render ENTRESSALA's photographic Instagram carousels (never synthetic photos).

Requires: pillow, requests. Run on GitHub Actions; images fetched from Wikimedia Commons,
not baked into this repository. A bad fetch or invalid rights stops publication output.
"""
import argparse
import hashlib
import io
import json
import os
import pathlib
import re
import textwrap
import time
import unicodedata
import ipaddress
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import quote, urlsplit, urlunsplit

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / 'fila-editorial.json'
ASSET_DIR = ROOT / 'assets'
PUBLISH_FILE = ROOT / 'fila-publicavel.json'
IMAGE_HISTORY_FILE = ROOT / 'image-history.json'
POLICY_EFFECTIVE_DATE = '2026-11-19'
USER_AGENT = 'ENTRESSALACulturalEditorialBot/0.1 (https://github.com/luisedferrari-ctrl/primeira-fila-revista; rights-cleared images)'
PHOTO_CACHE = {}
NEXT_FETCH_EARLIEST = 0.0
OWNER = 'luisedferrari-ctrl/primeira-fila-revista'
BRANCH = 'entressala-piloto-2026-11'
W, H = 1080, 1350
COLOR_CREAM = (248, 244, 231)
COLOR_YELLOW = (224, 181, 99)


def commons_direct_url(name):
    normalized = name.replace(' ', '_')
    digest = hashlib.md5(normalized.encode('utf-8')).hexdigest()
    return 'https://upload.wikimedia.org/wikipedia/commons/{}/{}/{}'.format(digest[0], digest[:2], quote(normalized, safe='()_-.,'))


def commons_source_url(name):
    return 'https://commons.wikimedia.org/wiki/File:' + quote(name.replace(' ', '_'), safe='()_-.')


def is_new_post(post):
    return post.get('publish_local_date', '') >= POLICY_EFFECTIVE_DATE


def safe_https_image_url(url):
    parsed = urlsplit(str(url))
    host = parsed.hostname or ''
    if parsed.scheme != 'https' or not host or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('Official media must use a public HTTPS URL with no credentials')
    if host == 'localhost' or host.endswith('.local'):
        raise ValueError('Private media URL is not allowed')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('IP-address media URL is not allowed')
    return url


def image_source_url(slide):
    if slide.get('asset_type') in ('official_poster', 'authorized_photo'):
        return slide['image_url']
    return commons_direct_url(slide['file'])


def image_credit_source(slide):
    if slide.get('source_page_url'):
        return slide['source_page_url']
    return commons_source_url(slide['file'])


def image_license_evidence(slide):
    if slide.get('asset_type') in ('official_poster', 'authorized_photo'):
        return slide.get('permission_evidence_url', '')
    return slide.get('license_url', '')


def image_key(slide):
    if slide.get('asset_type') in ('official_poster', 'authorized_photo'):
        safe_https_image_url(slide.get('image_url', ''))
        u = urlsplit(slide['image_url'])
        return slide['asset_type'] + ':' + urlunsplit(('https', u.netloc.casefold(), u.path, '', ''))
    filename = unicodedata.normalize('NFKC', str(slide.get('file', '')))
    return 'commons:' + filename.replace('_', ' ').strip().casefold()


def load_image_history():
    if IMAGE_HISTORY_FILE.exists():
        data = json.loads(IMAGE_HISTORY_FILE.read_text(encoding='utf-8'))
        if not isinstance(data.get('used_sources'), dict) or not isinstance(data.get('visual_hashes'), dict):
            raise ValueError('Invalid image history registry')
        return data
    return {'version': 1, 'effective_from': POLICY_EFFECTIVE_DATE,
            'used_sources': {}, 'visual_hashes': {}}


def check_image_uniqueness(manifest, history):
    # Every published/historical source is reserved forever, including old duplicates
    # which are grandfathered but MUST NOT be used again.
    known = dict(history['used_sources'])
    for post in manifest['posts']:
        if not is_new_post(post):
            for slide in post.get('slides', []):
                key = image_key(slide)
                known.setdefault(key, {'post_id': post['id'], 'publish_local_date': post['publish_local_date']})

    for post in manifest['posts']:
        if not is_new_post(post) or not (post.get('approved') is True and post.get('eligibleForScheduling') is True):
            continue
        seen_inside = set()
        for slide in post.get('slides', []):
            key = image_key(slide)
            if key in seen_inside:
                raise ValueError('Repeated image INSIDE carousel {}: {}'.format(post['id'], key))
            seen_inside.add(key)
            owner = known.get(key)
            if owner and owner.get('post_id') != post['id']:
                raise ValueError('Previously used image cannot be reused: {} (prior post {})'.format(
                    key, owner.get('post_id')))
            known[key] = {'post_id': post['id'], 'publish_local_date': post['publish_local_date']}
    return known


def image_visual_hash(img):
    # 256-bit difference hash on underlying ORIGINAL image, not graphic/text overlay.
    small = img.convert('L').resize((17, 16), Image.Resampling.LANCZOS)
    px = list(small.getdata())
    value = 0
    for y in range(16):
        for x in range(16):
            value = (value << 1) | (1 if px[y * 17 + x] > px[y * 17 + x + 1] else 0)
    return '{:064x}'.format(value)


def register_visual_hash(img, slide, post, number, history):
    key = image_key(slide)
    digest = image_visual_hash(img)
    for prior_hash, prior in history['visual_hashes'].items():
        distance = (int(prior_hash, 16) ^ int(digest, 16)).bit_count()
        identical_slot = (prior.get('post_id') == post['id']
                          and prior.get('slide_number') == number
                          and prior.get('image_key') == key)
        if distance <= 3 and not identical_slot:
            raise ValueError('Same/near-identical photo detected across slides/posts: {} (used in {})'.format(
                key, prior.get('post_id')))
    history['visual_hashes'][digest] = {
        'post_id': post['id'], 'slide_number': number, 'image_key': key,
        'publish_local_date': post['publish_local_date']
    }


def get_font(kind, size):
    fonts = {
        'serif': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf'
        ],
        'serif_bold': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf'
        ],
        'sans': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
        ],
        'sans_bold': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'
        ]
    }
    for candidate in fonts[kind]:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size=size)
    raise FileNotFoundError('Missing available font: ' + kind)


def fetch_photo(slide, test_placeholders=False, slide_number=0):
    global NEXT_FETCH_EARLIEST
    if test_placeholders:
        # Development-only reference texture, NEVER published.
        img = Image.new('RGB', (1080, 1350), (29 + slide_number * 17, 55 + slide_number * 8, 47))
        d = ImageDraw.Draw(img)
        d.text((90, 400), 'TESTE DE LAYOUT - SEM FOTO REAL', fill=(255, 220, 200), font=get_font('sans_bold', 40))
        return img
    filename = slide.get('file') or slide.get('image_url')
    key = image_key(slide)
    if key in PHOTO_CACHE:
        return PHOTO_CACHE[key].copy()
    source = image_source_url(slide)
    if slide.get('asset_type') in ('official_poster', 'authorized_photo'):
        safe_https_image_url(source)
    response = None
    for attempt in range(1, 5):
        # Wikimedia rate limits automated requests; do not download in a burst.
        now = time.monotonic()
        if now < NEXT_FETCH_EARLIEST:
            time.sleep(NEXT_FETCH_EARLIEST - now)
        response = requests.get(source, headers={'User-Agent': USER_AGENT}, timeout=60)
        NEXT_FETCH_EARLIEST = time.monotonic() + 7.0
        if response.status_code in (429, 502, 503):
            suggested = response.headers.get('Retry-After', '')
            delay = min(180, int(suggested)) if suggested.isdigit() else 30 * attempt
            print('Rate limited by Wikimedia ({}), retry {} in {}s: {}'.format(response.status_code, attempt, delay, filename), flush=True)
            time.sleep(delay)
            continue
        response.raise_for_status()
        break
    else:
        raise RuntimeError('Wikimedia download blocked after pacing/retries: ' + filename + ' (nothing published)')
    if slide.get('asset_type') in ('official_poster', 'authorized_photo'):
        safe_https_image_url(response.url)
    if not response.headers.get('Content-Type', '').lower().startswith('image/'):
        raise ValueError('Commons did not return image: ' + source)
    if len(response.content) < 18000:
        raise ValueError('Image unexpectedly small: ' + filename)
    img = Image.open(io.BytesIO(response.content)).convert('RGB')
    if min(img.size) < 700:
        raise ValueError('Image insufficiently resolved: {} {}'.format(filename, img.size))
    PHOTO_CACHE[key] = img.copy()
    return img


def fit_title(draw, text, max_width=920, max_lines=3):
    for size in range(79, 48, -2):
        font = get_font('serif_bold', size)
        lines = []
        current = ''
        for word in text.split():
            trial = word if not current else current + ' ' + word
            if draw.textbbox((0, 0), trial, font=font)[2] > max_width and current:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
        if len(lines) <= max_lines:
            return font, lines
    raise ValueError('Headline is too long to fit three lines: ' + text)


def draw_card(photo, slide, number, total):
    im = ImageOps.fit(photo, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.42)).convert('RGBA')
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    grad = ImageDraw.Draw(overlay)
    for y in range(0, 180):
        a = int(105 * (1 - y / 180))
        grad.line((0, y, W, y), fill=(6, 15, 12, a))
    for y in range(675, H):
        f = min(1.0, (y - 675) / 520.0)
        a = int(235 * (f ** 0.7))
        grad.line((0, y, W, y), fill=(6, 15, 12, a))
    im = Image.alpha_composite(im, overlay)
    draw = ImageDraw.Draw(im)
    x = 70
    draw.text((x, 47), 'E N T R E S S A L A', font=get_font('serif', 28), fill=COLOR_CREAM)
    draw.text((868, 55), '{:02d}/{:02d}'.format(number, total), font=get_font('sans', 27), fill=COLOR_CREAM)
    draw.line((70, 116, 1010, 116), fill=COLOR_YELLOW, width=3)
    kicker = slide['eyebrow'].upper()
    if slide.get('date_label') and slide.get('city'):
        kicker = '{}  ·  {}'.format(slide['date_label'], slide['city']).upper()
    kicker_font = get_font('sans_bold', 29)
    if draw.textbbox((0, 0), kicker, font=kicker_font)[2] > 935:
        kicker_font = get_font('sans_bold', 23)
    if draw.textbbox((0, 0), kicker, font=kicker_font)[2] > 935:
        raise ValueError('Date and city label too long: ' + kicker)
    draw.text((x, 812), kicker, font=kicker_font, fill=COLOR_YELLOW)
    font, lines = fit_title(draw, slide['title'])
    line_height = int(font.size * 1.18)
    top = 863
    for line in lines:
        draw.text((x, top), line, font=font, fill=COLOR_CREAM, stroke_width=1, stroke_fill=(0, 0, 0))
        top += line_height
    subtitle = slide['subtitle']
    font_sub = get_font('sans', 29)
    if draw.textbbox((0, 0), subtitle, font=font_sub)[2] > 920:
        font_sub = get_font('sans', 25)
    draw.text((x, min(top + 16, 1168)), subtitle, font=font_sub, fill=COLOR_CREAM)
    draw.line((x, 1248, 1010, 1248), fill=(192, 182, 160), width=2)
    credit_kind = 'Arte' if slide.get('asset_type') == 'official_poster' else 'Foto'
    line = '{}  ·  {}: {} ({})  ·  {}  ·  diagramação'.format(
        slide.get('context', ''), credit_kind, slide['photographer'],
        slide.get('year', 's.d.'), slide['license'])
    size = 19
    font_credit = get_font('sans', size)
    while draw.textbbox((0,0), line, font=font_credit)[2] > 945 and size > 14:
        size -= 1
        font_credit = get_font('sans', size)
    draw.text((x, 1270), line, font=font_credit, fill=COLOR_CREAM)
    return im.convert('RGB')


def validate(post):
    if not (post.get('approved') is True and post.get('eligibleForScheduling') is True):
        return False
    slides = post['slides']
    if not 1 <= len(slides) <= 20:
        raise ValueError('1-20 licensed image slides required')
    if len(post.get('caption', '')) > 2100:
        raise ValueError('Instagram caption too long: ' + post['id'])
    fresh = is_new_post(post)
    if fresh:
        edition = str(post.get('source_edition_id') or '')
        article = str(post.get('source_article_url') or '')
        if not re.fullmatch(r'EC-\d{4}-\d{2}-\d{2}', edition):
            raise ValueError('Source edition ID missing or invalid: ' + post['id'])
        origin = 'https://primeira-fila-revista.pages.dev/edicoes/{}/'.format(edition[3:])
        if not article.startswith(origin) or article == origin:
            raise ValueError('Source edition article URL missing or mismatched: ' + post['id'])
        if not post.get('verified_at') or not post.get('valid_through_local_date') or not post.get('factual_sources'):
            raise ValueError('Verified source, expiry and fact-check are required: ' + post['id'])
    secondary_seen = False
    for idx, slide in enumerate(slides, start=1):
        if not slide.get('photographer') or not slide.get('rights_checked_at'):
            raise ValueError('Incomplete attribution/rights: ' + post['id'])
        asset_type = slide.get('asset_type', 'photo')
        if asset_type in ('official_poster', 'authorized_photo'):
            if not (fresh and slide.get('image_url') and slide.get('source_page_url')
                    and slide.get('permission_evidence_url') and slide.get('instagram_use_allowed') is True
                    and slide.get('license') == 'PERMISSAO EDITORIAL'):
                raise ValueError('Official image/poster lacks documented republication rights: ' + post['id'])
            safe_https_image_url(slide['image_url'])
            safe_https_image_url(slide['source_page_url'])
            safe_https_image_url(slide['permission_evidence_url'])
        else:
            if asset_type != 'photo' or not slide.get('file') or not slide.get('license_url'):
                raise ValueError('Missing photograph or license: ' + post['id'])
            if not (slide.get('license', '').startswith('CC BY ')
                    or slide['license'].startswith('CC BY-SA ')):
                raise ValueError('License not allowed: ' + slide['file'])
        if fresh:
            if not slide.get('date_label') or not slide.get('city'):
                raise ValueError('Visible DATE and CITY are mandatory on every NEW slide: ' + post['id'])
            if not slide.get('depicts') or slide.get('specific_to_subject') is not True:
                raise ValueError('Generic or unverified visual subject: ' + post['id'])
            if 'FOTO DO LOCAL' in str(slide.get('context', '')).upper() and not slide.get('venue_is_subject'):
                raise ValueError('Generic venue photograph cannot illustrate unrelated events: ' + post['id'])
            tier = slide.get('appeal_tier')
            if tier not in ('cover', 'mass', 'secondary'):
                raise ValueError('Slide appeal_tier missing: ' + post['id'])
            if tier == 'cover' and idx != 1:
                raise ValueError('Only the first slide may be the cover: ' + post['id'])
            if tier == 'mass' and secondary_seen:
                raise ValueError('Mass attraction after secondary attraction: ' + post['id'])
            if tier == 'secondary':
                secondary_seen = True
    return True

def validate_manifest(manifest):
    if manifest.get('brand') != 'ENTRESSALA' or manifest.get('channel') != '@entressala_' or not isinstance(manifest.get('posts'), list):
        raise ValueError('Invalid ENTRESSALA editorial manifest')
    seen_ids = set()
    scheduled_dates = {}
    for post in manifest['posts']:
        pid = post.get('id')
        if not pid or pid in seen_ids:
            raise ValueError('Duplicate or missing post ID: {}'.format(pid))
        seen_ids.add(pid)
        if not (is_new_post(post) and post.get('approved') is True and post.get('eligibleForScheduling') is True):
            continue
        intended = datetime.strptime(post['publish_local_date'], '%Y-%m-%d').date()
        if intended.weekday() >= 5:
            raise ValueError('Regular Instagram posts must be Monday-Friday, including holidays: {}'.format(pid))
        if intended in scheduled_dates:
            raise ValueError('More than one approved automatic post for local date {}: {} and {}'.format(
                intended, scheduled_dates[intended], pid))
        scheduled_dates[intended] = pid


def create_credits(post):
    out = ['# ENTRESSALA — créditos de imagens: ' + post['id'], '',
           'Fotografias reais ou cartazes oficiais com direitos documentados.',
           'Imagens de arquivo não são necessariamente registros da edição anunciada.',
           'As mídias podem ter cortes, vinheta e texto editorial sobreposto.', '']
    for idx, slide in enumerate(post['slides'], start=1):
        asset_name = ('Cartaz oficial' if slide.get('asset_type') == 'official_poster'
                      else 'Fotografia autorizada' if slide.get('asset_type') == 'authorized_photo'
                      else 'Fotografia')
        out.append('{}. **{}** — {}: {}, {}. Fonte: {}. Direitos: {} ({}). Contexto: {}. Adaptação: corte, vinheta e diagramação.'.format(
            idx, slide['title'], asset_name, slide['photographer'],
            slide.get('year', 's.d.'), image_credit_source(slide),
            slide['license'], image_license_evidence(slide),
            slide.get('context', '')))
        if slide.get('permission_evidence_url'):
            out.append('   Evidência de permissão: ' + slide['permission_evidence_url'])
    out.append('')
    out.append('Quando aplicável, respeitar todas as condições de atribuição e compartilhamento de obras CC BY-SA.')
    return '\n'.join(out) + '\n'

def render(manifest_path, test_placeholders=False):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    validate_manifest(manifest)
    history = load_image_history()
    known_sources = check_image_uniqueness(manifest, history)
    processed = []
    local_today = datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    for post in manifest['posts']:
        if not validate(post):
            continue
        # Fila curta: apenas posts recentes e proximos 10 dias; nunca reusar pauta vencida.
        intended_date = datetime.strptime(post['publish_local_date'], '%Y-%m-%d').date()
        expiry = datetime.strptime(post['valid_through_local_date'], '%Y-%m-%d').date()
        if not test_placeholders and (expiry < local_today or intended_date > local_today + timedelta(days=10)):
            continue
        folder = ASSET_DIR / post['id']
        folder.mkdir(parents=True, exist_ok=True)
        urls = []
        firstcomment = ['Créditos das fotografias (todas de arquivo, com cortes e sobreposição editorial):']
        signature = hashlib.sha256(json.dumps(post, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
        sigfile = folder / '_source_hash.txt'
        expected_files = [folder / '{:02d}.jpg'.format(index) for index in range(1, len(post['slides']) + 1)]
        cached = (not test_placeholders and sigfile.exists() and sigfile.read_text().strip() == signature
                  and all(p.exists() and p.stat().st_size > 50000 for p in expected_files))
        if cached:
            print('Reusing already credited JPEGs (no Wikimedia download): ' + post['id'], flush=True)
        for index, slide in enumerate(post['slides'], start=1):
            filename = '{:02d}.jpg'.format(index)
            if not cached:
                img = fetch_photo(slide, test_placeholders, index)
                if is_new_post(post) and not test_placeholders:
                    register_visual_hash(img, slide, post, index, history)
                composed = draw_card(img, slide, index, len(post['slides']))
                composed.save(folder / filename, 'JPEG', quality=89, optimize=True, subsampling=0)
            rawpath = 'instagram/assets/{}/{}'.format(post['id'], filename)
            urls.append('https://raw.githubusercontent.com/{}/{}/{}'.format(OWNER, BRANCH, rawpath))
            firstcomment.append('{}: {} ({}) · {}. Fonte: {} · licença/permissão {}'.format(
                index, slide['photographer'], slide.get('year', 's.d.'), slide['license'],
                image_credit_source(slide), image_license_evidence(slide)))
        if not test_placeholders:
            sigfile.write_text(signature + '\n', encoding='utf-8')
        if is_new_post(post) or not (folder / 'CREDITOS.md').exists():
            (folder / 'CREDITOS.md').write_text(create_credits(post), encoding='utf-8')
        item = {k:v for k,v in post.items() if k != 'slides'}
        item['images'] = urls
        item['credits_document'] = 'https://github.com/{}/blob/{}/instagram/assets/{}/CREDITOS.md'.format(OWNER, BRANCH, post['id'])
        item['first_comment'] = '\n'.join(firstcomment)[:2100]
        item['assetsReady'] = not test_placeholders
        if is_new_post(post):
            item['date_city_visible'] = True
            item['image_uniqueness_checked'] = not test_placeholders
        processed.append(item)
    result = {'brand': manifest['brand'], 'channel': manifest['channel'], 'version':3,
              'editorial_policy': 'reach-first-unique-images-2026-11-18', 'posts':processed,
              'notice': 'Publishing must verify images, factual validity and idempotency. Auto-publish only after verified assets; no synthesized event photography.'}
    path = ROOT / ('fila-preview-TESTE.json' if test_placeholders else 'fila-publicavel.json')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if not test_placeholders:
        history['used_sources'] = known_sources
        IMAGE_HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Processed {} posts with {} images. Manifest: {}'.format(len(processed), sum(len(p['images']) for p in processed), path))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--test-placeholders', action='store_true', help='TEST ONLY: artificial placeholders, assetsReady false, never publish')
    ap.add_argument('--manifest', type=pathlib.Path, default=SOURCE)
    args = ap.parse_args()
    render(args.manifest, args.test_placeholders)