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
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / 'fila-editorial.json'
ASSET_DIR = ROOT / 'assets'
PUBLISH_FILE = ROOT / 'fila-publicavel.json'
USER_AGENT = 'ENTRESSALACulturalEditorialBot/0.1 (https://github.com/luisedferrari-ctrl/primeira-fila-revista; rights-cleared images)'
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
    if test_placeholders:
        # Development-only reference texture, NEVER published.
        img = Image.new('RGB', (1080, 1350), (29 + slide_number * 17, 55 + slide_number * 8, 47))
        d = ImageDraw.Draw(img)
        d.text((90, 400), 'TESTE DE LAYOUT - SEM FOTO REAL', fill=(255, 220, 200), font=get_font('sans_bold', 40))
        return img
    filename = slide['file']
    source = commons_direct_url(filename)
    response = requests.get(source, headers={'User-Agent': USER_AGENT}, timeout=60)
    response.raise_for_status()
    if not response.headers.get('Content-Type', '').lower().startswith('image/'):
        raise ValueError('Commons did not return image: ' + source)
    if len(response.content) < 18000:
        raise ValueError('Image unexpectedly small: ' + filename)
    img = Image.open(io.BytesIO(response.content)).convert('RGB')
    if min(img.size) < 700:
        raise ValueError('Image insufficiently resolved: {} {}'.format(filename, img.size))
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
    draw.text((x, 812), kicker, font=get_font('sans_bold', 29), fill=COLOR_YELLOW)
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
    line = '{}  ·  Foto: {} ({})  ·  {}  ·  corte/diagramação'.format(slide['context'], slide['photographer'], slide['year'], slide['license'])
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
        raise ValueError('1-20 real photo slides required')
    if len(post.get('caption', '')) > 2100:
        raise ValueError('Instagram caption too long: ' + post['id'])
    for slide in slides:
        if not slide.get('file') or not slide.get('photographer') or not slide.get('license_url') or not slide.get('rights_checked_at'):
            raise ValueError('Incomplete attribution/rights: ' + post['id'])
        if not (slide['license'].startswith('CC BY ') or slide['license'].startswith('CC BY-SA ')):
            raise ValueError('License not allowed: ' + slide['file'])
    return True


def create_credits(post):
    out = ['# ENTRESSALA — créditos de fotografia: ' + post['id'], '',
           'Todas são fotografias reais. Nenhuma foto de arquivo representa necessariamente o evento noticiado.',
           'As imagens foram cortadas, tiveram ajustes de composição e receberam texto editorial.', '']
    for idx, slide in enumerate(post['slides'], start=1):
        out.append('{}. **{}** — Foto: {}, {}. Fonte: {}. Licença: {} ({}). Contexto: {}. Adaptação: corte, vinheta e sobreposição tipográfica.'.format(
            idx, slide['title'], slide['photographer'], slide['year'], commons_source_url(slide['file']), slide['license'], slide['license_url'], slide['context']))
    out.append('')
    out.append('Em cada derivação de uma obra CC BY-SA, o slide correspondente é oferecido sob a licença CC BY-SA compatível indicada no próprio crédito. Reprodução sujeita a essa licença.')
    return '\n'.join(out) + '\n'


def render(manifest_path, test_placeholders=False):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
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
        for index, slide in enumerate(post['slides'], start=1):
            img = fetch_photo(slide, test_placeholders, index)
            composed = draw_card(img, slide, index, len(post['slides']))
            filename = '{:02d}.jpg'.format(index)
            composed.save(folder / filename, 'JPEG', quality=89, optimize=True, subsampling=0)
            rawpath = 'instagram/assets/{}/{}'.format(post['id'], filename)
            urls.append('https://raw.githubusercontent.com/{}/{}/{}'.format(OWNER, BRANCH, rawpath))
            firstcomment.append('{}: {} ({}) · {}. Fonte: {} · licença {}'.format(index, slide['photographer'], slide['year'], slide['license'], commons_source_url(slide['file']), slide['license_url']))
        (folder / 'CREDITOS.md').write_text(create_credits(post), encoding='utf-8')
        item = {k:v for k,v in post.items() if k != 'slides'}
        item['images'] = urls
        item['credits_document'] = 'https://github.com/{}/blob/{}/instagram/assets/{}/CREDITOS.md'.format(OWNER, BRANCH, post['id'])
        item['first_comment'] = '\n'.join(firstcomment)[:2100]
        item['assetsReady'] = not test_placeholders
        processed.append(item)
    result = {'brand': manifest['brand'], 'channel': manifest['channel'], 'version':3, 'posts':processed,
              'notice': 'Publishing must verify images, factual validity and idempotency. Auto-publish only after verified assets; no synthesized event photography.'}
    path = ROOT / ('fila-preview-TESTE.json' if test_placeholders else 'fila-publicavel.json')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Processed {} posts with {} images. Manifest: {}'.format(len(processed), sum(len(p['images']) for p in processed), path))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--test-placeholders', action='store_true', help='TEST ONLY: artificial placeholders, assetsReady false, never publish')
    ap.add_argument('--manifest', type=pathlib.Path, default=SOURCE)
    args = ap.parse_args()
    render(args.manifest, args.test_placeholders)