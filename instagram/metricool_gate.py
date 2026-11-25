"""ENTRESSALA extraordinary Metricool preflight, fail-closed and read-only.

This checks a candidate manifest against policy v2026-11-25 and produces a
structured decision. It deliberately DOES NOT call Metricool or publish.

Limit: the checker verifies the existence of recorded evidence and media
integrity, not the truth of third-party content or image-license claims.
Those require a genuinely independent editorial review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import re
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

try:
    from PIL import Image
except ImportError:  # environment error becomes a blocking finding
    Image = None

POLICY_VERSION = "entressala-metricool-extra-2026-11-25-v1"
BRAND_ID = "8230360"
TZ = ZoneInfo("America/Sao_Paulo")
REQUIRED_REVIEW = (
    "facts_checked", "rights_evidence_checked", "subject_match_checked",
    "visual_mobile_checked", "caption_checked", "dedupe_checked",
)
ALLOWED_LICENSES = {"CC BY", "CC BY-SA", "CC0", "PUBLIC DOMAIN", "WRITTEN PERMISSION"}
PHOTO_TYPES = {"authentic_photo"}
ALLOWED_TYPES = PHOTO_TYPES | {"authentic_artwork", "venue_photo", "ai_generated", "text_only", "official_poster"}

ISSUE_FIXES = {
    "MANIFEST_INVALID": "Corrigir o JSON e fornecer uma ficha completa antes de qualquer agendamento.",
    "POLICY_UNKNOWN": "Aplicar a versao homologada da politica e reexecutar a checagem.",
    "WRONG_CHANNEL": "Usar somente o canal extraordinario da marca Metricool correta.",
    "WRONG_BRAND": "Selecionar a marca Metricool ENTRESSALA (ID 8230360).",
    "ID_INVALID": "Gerar ID unico ENTRESSALA-EXTRA-AAAAMMDD-ASSUNTO.",
    "SCHEDULE_INVALID": "Informar data futura no fuso America/Sao_Paulo.",
    "CLASS_INVALID": "Classificar o post como event, radar ou news.",
    "HOOK_MISSING": "Descrever fato novo, notoriedade verificavel e motivo para compartilhamento.",
    "SOURCE_MISSING": "Anexar fonte primaria ou institucional, URL e data de rechecagem.",
    "SOURCE_STALE": "Revalidar a fonte primaria antes da publicacao (janela de 48 horas).",
    "SERVICE_MISSING": "Preencher servico coerente com a classe de pauta.",
    "SERVICE_CAPTION_MISMATCH": "Fazer constar na legenda os dados oficiais de servico.",
    "RADAR_MISLABELED": "Marcar datas e ingressos nao divulgados, sem inventar informacoes.",
    "CAPTION_MISSING": "Criar legenda com contexto verificado e referencia oficial.",
    "CTA_MISSING": "Inserir convite especifico para seguir @entressala_ e beneficio ao leitor.",
    "SLIDES_INVALID": "Usar de uma a quatro laminas completas; reels exigem processo distinto.",
    "MEDIA_UNAVAILABLE": "Anexar midia local acessivel para calcular hash e verificar resolucao.",
    "MEDIA_INVALID": "Exportar JPEG legivel, sRGB, com 1080 x 1350 pixels.",
    "MEDIA_HASH_MISMATCH": "Recalcular e revisar os bytes finais; repetir a aprovacao apos a alteracao.",
    "MEDIA_SOURCE_MISSING": "Registrar a origem unica e o hash do arquivo-fonte original.",
    "MEDIA_URL_MISSING": "Fornecer URL HTTPS da midia final que sera enviada ao Metricool.",
    "MEDIA_DUPLICATE": "Substituir imagem repetida e revalidar direitos e historico.",
    "RIGHTS_MISSING": "Obter permissao/licenca com prova publica, titular e data de verificacao.",
    "COVER_NOT_AUTHENTIC": "Usar fotografia autentica do artista/obra/evento, licenciada.",
    "COVER_NOT_RELEVANT": "Escolher foto que represente a atracao, nao o predio ou ilustracao generica.",
    "PHOTO_RATIO": "Usar fotografias reais em pelo menos 80% das laminas.",
    "ARTWORK_EXCEPTION_INVALID": "Documentar que a obra original e o proprio assunto e comprovar direitos.",
    "VISUAL_TEXT_MISSING": "Mostrar manchete, data/contexto, cidade quando aplicavel e CTA visivel.",
    "REVIEW_MISSING": "Completar revisao humana independente com prova e responsavel identificados.",
    "REVIEW_STALE": "Renovar revisao editorial e inspeção mobile antes de publicar.",
    "REMOTE_CHECK_MISSING": "Conferir conexao, duplicatas no Metricool e publicar apenas apos validacao.",
    "REMOTE_CHECK_STALE": "Revalidar o estado remoto antes de enviar ao Metricool.",
    "HISTORY_MISSING": "Fornecer historico de fontes de imagem para checagem anti-reuso.",
}


def parse_aware(value):
    if not isinstance(value, str) or not value:
        raise ValueError("empty datetime")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("datetime without timezone")
    return dt.astimezone(TZ)


def valid_url(url):
    return isinstance(url, str) and re.match(r"^https://[^/\s]+(?:/[^\s]*)?$", url) is not None


def nonblank(text, length=5):
    return isinstance(text, str) and len(text.strip()) >= length


def normalize(text):
    return re.sub(r"\s+", " ", str(text).casefold()).strip()


def sha256_file(p):
    d = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(131072), b""):
            d.update(chunk)
    return d.hexdigest()


def preflight(post, assets_root, history, now=None):
    now = (now or datetime.now(TZ)).astimezone(TZ)
    issues = []
    def fail(code, field, detail):
        issues.append({"code": code, "field": field, "finding": detail,
                       "resolution": ISSUE_FIXES.get(code, "Corrigir e revalidar.")})

    if not isinstance(post, dict):
        post = {}
        fail("MANIFEST_INVALID", "$", "Ficha deve ser um objeto JSON.")
    if post.get("policy_version") != POLICY_VERSION:
        fail("POLICY_UNKNOWN", "policy_version", "Versao nao corresponde a politica ativa.")
    if post.get("publication_channel") != "metricool_extra":
        fail("WRONG_CHANNEL", "publication_channel", "Canal diferente de metricool_extra.")
    if str(post.get("brand_id")) != BRAND_ID:
        fail("WRONG_BRAND", "brand_id", "Marca diferente de 8230360.")
    post_id = post.get("id", "")
    if not isinstance(post_id, str) or not re.fullmatch(r"ENTRESSALA-EXTRA-20\d{6}-[A-Z0-9-]+", post_id):
        fail("ID_INVALID", "id", "Identificador de post ausente/invalido.")
    try:
        when = parse_aware(post.get("publish_at"))
        if when <= now:
            fail("SCHEDULE_INVALID", "publish_at", "A data de agendamento ja passou.")
    except (ValueError, TypeError):
        fail("SCHEDULE_INVALID", "publish_at", "Data ausente ou sem fuso horario.")
    kind = post.get("content_kind")
    if kind not in ("event", "radar", "news"):
        fail("CLASS_INVALID", "content_kind", "Classe nao reconhecida.")
    if not (nonblank(post.get("subject"), 4) and nonblank(post.get("headline"), 15) and
            nonblank(post.get("novelty"), 20) and nonblank(post.get("share_reason"), 15) and
            nonblank(post.get("recognition_signal"), 15)):
        fail("HOOK_MISSING", "editorial", "Faltam assunto, fato novo, notoriedade, manchete ou motivo para compartilhar.")
    source = post.get("official_source") if isinstance(post.get("official_source"), dict) else {}
    if not (nonblank(source.get("name"), 3) and valid_url(source.get("url"))):
        fail("SOURCE_MISSING", "official_source", "Fonte nominal e URL HTTPS verificavel obrigatorias.")
    try:
        last = parse_aware(source.get("checked_at"))
        if not (timedelta() <= now - last <= timedelta(hours=48)):
            fail("SOURCE_STALE", "official_source.checked_at", "Fonte verificada fora da janela de 48 horas.")
    except (ValueError, TypeError):
        fail("SOURCE_STALE", "official_source.checked_at", "Verificacao sem registro datado valido.")
    service = post.get("service") if isinstance(post.get("service"), dict) else {}
    necessary = ("when", "where", "admission", "official_url") if kind in ("event", "radar") else ("when", "what", "context", "official_url")
    if not all(nonblank(service.get(k), 4) for k in necessary if k != "official_url") or not valid_url(service.get("official_url")):
        fail("SERVICE_MISSING", "service", "Faltam informacoes estruturadas de fonte ou servico.")
    if kind == "radar" and ("datas a anunciar" not in normalize(service.get("when")) or
                               "ingressos ainda nao divulgados" not in normalize(service.get("admission"))):
        fail("RADAR_MISLABELED", "service", "Radar sem marcadores explicitos de incerteza.")
    caption = post.get("caption")
    if not nonblank(caption, 70):
        fail("CAPTION_MISSING", "caption", "Legenda insuficiente.")
    if "siga @entressala_" not in normalize(caption):
        fail("CTA_MISSING", "caption", "Legenda nao inclui CTA especifico para seguir a conta.")
    if valid_url(service.get("official_url")) and service["official_url"] not in str(caption):
        fail("SERVICE_CAPTION_MISMATCH", "caption", "A URL oficial nao aparece na legenda.")
    for key in necessary:
        if key == "official_url" or not nonblank(service.get(key), 4):
            continue
        if normalize(service[key]) not in normalize(caption):
            fail("SERVICE_CAPTION_MISMATCH", "caption", "Legenda nao contem integralmente o campo "+key)
    slides = post.get("slides")
    if not isinstance(slides, list) or not 1 <= len(slides) <= 4:
        fail("SLIDES_INVALID", "slides", "Numero de laminas invalido; esta versao e para posts com 1 a 4 imagens.")
        slides = []
    original_subject_art = post.get("editorial_subject_kind") == "authentic_artwork_itself"
    artwork_exception = original_subject_art and nonblank(post.get("artwork_exception_reason"), 40)
    if original_subject_art and not artwork_exception:
        fail("ARTWORK_EXCEPTION_INVALID", "artwork_exception_reason", "Obra original exige justificativa editorial especifica.")
    images = []
    kinds = []
    checked_ids = set()
    known_used = history.get("used_sources", {}) if isinstance(history, dict) else {}
    if not isinstance(known_used, dict):
        known_used = {}
        fail("HISTORY_MISSING", "history.used_sources", "Historico invalido.")
    if not isinstance(history, dict) or not isinstance(history.get("used_sources"), dict):
        fail("HISTORY_MISSING", "history", "Sem historico de fontes anteriores.")
    for i, slide in enumerate(slides):
        label = "slides["+str(i)+"]"
        if not isinstance(slide, dict):
            fail("MANIFEST_INVALID", label, "Lamina nao e objeto.")
            continue
        media_kind = slide.get("media_kind")
        kinds.append(media_kind)
        if media_kind not in ALLOWED_TYPES:
            fail("MEDIA_INVALID", label+".media_kind", "Tipo de midia nao identificado.")
        source_id = normalize(slide.get("source_image_id"))
        if not source_id or not isinstance(slide.get("source_image_sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", slide["source_image_sha256"]):
            fail("MEDIA_SOURCE_MISSING", label, "Identidade/sha256 do arquivo-fonte nao documentados.")
        if source_id in checked_ids or source_id in {normalize(k) for k in known_used}:
            fail("MEDIA_DUPLICATE", label+".source_image_id", "Fonte de imagem repetida no post ou historico.")
        if source_id:
            checked_ids.add(source_id)
        if not valid_url(slide.get("media_url")):
            fail("MEDIA_URL_MISSING", label+".media_url", "URL HTTPS do arquivo final ausente.")
        file_rel=slide.get("file")
        if not isinstance(file_rel,str) or not file_rel or pathlib.Path(file_rel).is_absolute() or ".." in pathlib.Path(file_rel).parts:
            fail("MEDIA_UNAVAILABLE", label+".file", "Caminho local invalido ou inseguro.")
        else:
            p=(pathlib.Path(assets_root)/file_rel)
            if not p.is_file():
                fail("MEDIA_UNAVAILABLE", label+".file", "Arquivo local nao encontrado.")
            else:
                digest = sha256_file(p)
                images.append({"file": file_rel, "sha256":digest})
                if digest != slide.get("final_sha256"):
                    fail("MEDIA_HASH_MISMATCH", label+".final_sha256", "Hash final nao confere com arquivo enviado.")
                if Image is None:
                    fail("MEDIA_INVALID", label+".file", "Biblioteca Pillow indisponivel; nao houve verificacao de dimensao.")
                else:
                    try:
                        with Image.open(p) as im:
                            if im.format != "JPEG" or im.size != (1080,1350) or im.mode not in ("RGB", "L"):
                                fail("MEDIA_INVALID", label+".file", "JPEG 1080x1350 RGB obrigatorio; recebido "+str((im.format, im.size, im.mode)))
                            im.verify()
                    except Exception as e:
                        fail("MEDIA_INVALID", label+".file", "Arquivo nao pode ser decodificado: "+str(e))
        rights = slide.get("rights") if isinstance(slide.get("rights"),dict) else {}
        if (rights.get("license") not in ALLOWED_LICENSES or
            not nonblank(rights.get("holder"),3) or
            not valid_url(rights.get("evidence_url")) or
            not nonblank(rights.get("credit"),4)):
            fail("RIGHTS_MISSING", label+".rights", "Direitos de reutilizacao nao estao documentados conforme politica.")
        is_venue_subject = (media_kind == "venue_photo" and slide.get("venue_is_subject") is True)
        if i == 0 and media_kind != "authentic_photo" and not is_venue_subject and not (artwork_exception and media_kind=="authentic_artwork"):
            fail("COVER_NOT_AUTHENTIC", label+".media_kind", "Capa sem fotografia real pertinente.")
        if media_kind == "venue_photo" and not slide.get("venue_is_subject"):
            fail("COVER_NOT_RELEVANT", label+".media_kind", "Predio nao representa a atracao quando o predio nao e noticia.")
        if not slide.get("subject_specific"):
            fail("COVER_NOT_RELEVANT", label+".subject_specific", "Imagem nao foi validada como especifica da pauta.")
        visible=slide.get("visible_text") if isinstance(slide.get("visible_text"),dict) else {}
        if not (nonblank(visible.get("headline"),10) and nonblank(visible.get("when"),4) and
                nonblank(visible.get("source"),4)):
            fail("VISUAL_TEXT_MISSING",label+".visible_text", "Faltam manchete/data/contexto e fonte na arte.")
        if kind == "event" and not nonblank(visible.get("where"),4):
            fail("VISUAL_TEXT_MISSING",label+".visible_text.where", "Local nao visivel no slide de evento.")
        if i == len(slides)-1 and "siga @entressala_" not in normalize(visible.get("cta")):
            fail("CTA_MISSING",label+".visible_text.cta", "CTA visual ausente no ultimo slide.")
    if slides and not artwork_exception:
        ratio=sum(1 for s in slides if isinstance(s, dict) and (s.get("media_kind") in PHOTO_TYPES or (s.get("media_kind") == "venue_photo" and s.get("venue_is_subject") is True)))/len(slides)
        if ratio < .8:
            fail("PHOTO_RATIO", "slides", "Proporcao fotografica de "+str(round(ratio*100))+"%, abaixo de 80%.")
    human=post.get("human_review") if isinstance(post.get("human_review"),dict) else {}
    if (not nonblank(human.get("reviewer"),4) or
        not valid_url(human.get("evidence_url")) or
        any(human.get(f) is not True for f in REQUIRED_REVIEW)):
        fail("REVIEW_MISSING","human_review", "Revisao editorial humana completa e evidencia documental sao obrigatorias.")
    try:
        reviewed=parse_aware(human.get("checked_at"))
        if not timedelta() <= now-reviewed <= timedelta(hours=48):
            fail("REVIEW_STALE", "human_review.checked_at", "Revisao editorial fora da janela de 48 horas.")
    except (ValueError,TypeError):
        fail("REVIEW_STALE", "human_review.checked_at", "Revisao sem timestamp valido.")
    remote=post.get("remote_checks") if isinstance(post.get("remote_checks"),dict) else {}
    if not (remote.get("brand_connected") is True and
            remote.get("duplicate_absent") is True and
            valid_url(remote.get("evidence_url"))):
        fail("REMOTE_CHECK_MISSING", "remote_checks", "Faltam provas de conexao e consulta de duplicatas.")
    try:
        checked=parse_aware(remote.get("checked_at"))
        if not timedelta() <= now-checked <= timedelta(minutes=60):
            fail("REMOTE_CHECK_STALE", "remote_checks.checked_at", "Estado remoto nao confirmado nos ultimos 60 min.")
    except (ValueError,TypeError):
        fail("REMOTE_CHECK_STALE", "remote_checks.checked_at", "Consulta remota sem horario valido.")
    canonical=json.dumps(post,sort_keys=True,ensure_ascii=False,separators=(",",":"),default=str)
    digest=hashlib.sha256(canonical.encode()).hexdigest()
    return {
        "policy_version": POLICY_VERSION,
        "post_id": post_id or "UNKNOWN",
        "checked_at": now.isoformat(),
        "verdict": "BLOCKED" if issues else "APPROVED_FOR_METRICOOL_SUBMISSION",
        "publish_permitted": len(issues)==0,
        "issues": issues,
        "issue_count": len(issues),
        "manifest_sha256": digest,
        "media_hashes": images,
        "approval_digest": (digest if not issues else None),
        "caveat": "External facts, copyright ownership, actual subject match and platform/API status require independent verification. Direct Metricool API is not technically bound to this gate."
    }


def main(argv=None):
    ap=argparse.ArgumentParser(description="ENTRESSALA Metricool extraordinary fail-closed gate")
    ap.add_argument("--manifest",type=pathlib.Path,required=True)
    ap.add_argument("--assets-root",type=pathlib.Path,default=pathlib.Path("."))
    ap.add_argument("--history",type=pathlib.Path,required=True)
    ap.add_argument("--report",type=pathlib.Path,required=True)
    ap.add_argument("--now",help="ISO timestamp with timezone, for tests and reproducible checks")
    args=ap.parse_args(argv)
    try:
        candidate=json.loads(args.manifest.read_text(encoding="utf-8"))
        history=json.loads(args.history.read_text(encoding="utf-8"))
        now=parse_aware(args.now) if args.now else datetime.now(TZ)
        outcome=preflight(candidate,args.assets_root,history,now=now)
    except Exception as e:
        outcome={"verdict":"BLOCKED","publish_permitted":False,"issues":[{"code":"MANIFEST_INVALID","field":"$","finding":str(e),"resolution":ISSUE_FIXES["MANIFEST_INVALID"]}],"issue_count":1,"approval_digest":None}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(outcome,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:outcome.get(k) for k in ("post_id","verdict","issue_count","approval_digest")},ensure_ascii=False))
    if not outcome.get("publish_permitted"):
        for problem in outcome["issues"]:
            print("BLOCK " + problem["code"] + " " + problem["field"] + ": " + problem["finding"] + " | CORRIGIR: " + problem["resolution"])
    return 0 if outcome.get("publish_permitted") else 2


if __name__=="__main__":
    sys.exit(main())
