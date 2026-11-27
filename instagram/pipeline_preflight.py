"""Read-only gate: resolve published editions from main, never the social branch."""
import argparse
import json
import pathlib
from datetime import date, datetime
from zoneinfo import ZoneInfo

SITE = 'https://primeira-fila-revista.pages.dev'


def latest_edition(root, today):
    editions = []
    for path in pathlib.Path(root).glob('edicoes/????-??-??/dados/edicao-*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        day = path.parents[1].name
        date.fromisoformat(day)
        if data.get('status') != 'PUBLISHED' or day > today:
            continue
        if data.get('id') != 'EC-' + day or data.get('date') != day:
            raise ValueError('Published edition has inconsistent identity: ' + str(path))
        if data.get('publicUrl') != SITE + '/edicoes/' + day + '/':
            raise ValueError('Published edition lacks canonical public URL: ' + day)
        if not data.get('publishedVerifiedAt') or not data.get('publicationEvidence'):
            raise ValueError('Published edition lacks recorded publication evidence: ' + day)
        if not (path.parents[1] / 'index.html').is_file():
            raise ValueError('Published edition HTML missing: ' + day)
        articles = sorted(p.parent.name for p in (path.parents[1] / 'materias').glob('*/index.html'))
        if not articles:
            raise ValueError('Published edition has no articles: ' + day)
        editions.append({'id': data['id'], 'date': day, 'url': data['publicUrl'],
                         'publication_evidence': data['publicationEvidence'], 'articles': articles})
    if not editions:
        raise ValueError('NO_PUBLISHED_EDITION_IN_MAIN: source unavailable or no eligible edition; never infer from Instagram queue')
    return max(editions, key=lambda item: item['date'])


def inspect_queue(manifest, edition, today):
    from render_social import validate, validate_manifest
    validate_manifest(manifest)
    candidates = [p for p in manifest['posts'] if p.get('publish_local_date') == today
                  and p.get('approved') is True and p.get('eligibleForScheduling') is True]
    if len(candidates) != 1:
        raise ValueError('EDITORIAL_BLOCKED: expected one approved candidate for ' + today + ', found ' + str(len(candidates)))
    p = candidates[0]
    if p.get('source_edition_id') != edition['id']:
        raise ValueError('Candidate does not use latest published edition in main')
    allowed = {edition['url'] + 'materias/' + slug + '/' for slug in edition['articles']}
    if p.get('source_article_url') not in allowed:
        raise ValueError('Candidate source article is not present in main')
    checked = date.fromisoformat(p['verified_at'])
    age = (date.fromisoformat(today) - checked).days
    if not 0 <= age <= 2 or p['valid_through_local_date'] < today:
        raise ValueError('Candidate facts are stale, future-dated or expired')
    if not validate(p):
        raise ValueError('Candidate is not eligible')
    return p['id']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', type=pathlib.Path, required=True)
    ap.add_argument('--manifest', type=pathlib.Path)
    ap.add_argument('--date', default=datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat())
    args = ap.parse_args()
    edition = latest_edition(args.source_root, args.date)
    print(json.dumps({'canonical_edition': edition}, ensure_ascii=False))
    if args.manifest:
        if date.fromisoformat(args.date).weekday() >= 5:
            raise ValueError('NO_REGULAR_SLOT: weekend; no production output')
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        print('READY_TO_RENDER: ' + inspect_queue(manifest, edition, args.date))


if __name__ == '__main__':
    main()
