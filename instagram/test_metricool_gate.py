"""Offline synthetic unit tests; never call Metricool or claim historical approval."""
import copy
import hashlib
import json
import pathlib
import tempfile
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
from metricool_gate import POLICY_VERSION, REQUIRED_REVIEW, preflight

NOW = datetime(2026, 11, 25, 14, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.image = self.root / "photo.jpg"
        Image.new("RGB", (1080, 1350), (40, 70, 60)).save(self.image, "JPEG")
        media_hash = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.history = {"used_sources": {"commons:eddie vedder 2018.jpg": {"post_id": "HISTORICAL"}}}
        self.base = {
          "policy_version": POLICY_VERSION,
          "publication_channel": "metricool_extra",
          "brand_id": "8230360",
          "id": "ENTRESSALA-EXTRA-20261125-EXAMPLE",
          "publish_at": "2026-11-25T15:00:00-03:00",
          "content_kind": "event",
          "subject": "Evento Exemplo",
          "headline": "EVENTO EXEMPLO CONFIRMADO PARA CAMPINAS",
          "novelty": "Evento de hipotese confirmado so para teste tecnico do validador.",
          "share_reason": "Informacao util para enviar a quem gosta da atração.",
          "recognition_signal": "Nome identificado na comunidade local; apenas dado sintetico.",
          "official_source": {"name": "Organizador Exemplo", "url": "https://example.org/noticia", "checked_at": "2026-11-25T13:30:00-03:00"},
          "service": {"when": "27/11/2026, 18h", "where": "Centro Cultural, Campinas", "admission": "entrada gratuita", "official_url": "https://example.org/ingressos"},
          "caption": "Evento Exemplo confirmado, programa cultural publico. 27/11/2026, 18h. Centro Cultural, Campinas. entrada gratuita. https://example.org/ingressos. Siga @entressala_ para descobrir atividades culturais na sua região.",
          "slides": [{
            "file": "photo.jpg", "final_sha256": media_hash,
            "source_image_sha256": "a"*64,
            "source_image_id": "commons:foto exemplo teste original.jpg",
            "media_url": "https://example.org/photo.jpg", "media_kind": "authentic_photo", "subject_specific": True,
            "rights": {"license": "CC BY", "holder": "Foto Exemplo", "credit": "Foto: Exemplo", "evidence_url": "https://example.org/license"},
            "visible_text": {"headline": "EVENTO EXEMPLO EM CAMPINAS", "when": "27/11/2026", "where": "Centro Cultural, Campinas", "source": "Organizador Exemplo", "cta": "Siga @entressala_ para descobrir mais"}
          }],
          "editorial_review": {"reviewer_type": "assistant", "reviewer": "ChatGPT - fixture sintetica", "decision": "APPROVED", "checked_at": "2026-11-25T13:45:00-03:00", "evidence_url": "https://example.org/revisao", "facts_checked": True, "rights_evidence_checked": True, "subject_match_checked": True, "visual_mobile_checked": True, "caption_checked": True, "dedupe_checked": True, "editorial_appeal_checked": True, "authenticity_checked": True},
          "remote_checks": {"brand_connected": True, "duplicate_absent": True, "checked_at": "2026-11-25T13:50:00-03:00", "evidence_url": "https://example.org/metricool-check"}
        }

        review=self.base["editorial_review"]
        review["findings"]={f: "Evidencia sintetica de teste para "+f for f in REQUIRED_REVIEW}
        review["reviewed_media_sha256"]=[media_hash]
        review["reviewed_caption_sha256"]=hashlib.sha256(self.base["caption"].encode("utf-8")).hexdigest()

    def test_synthetic_baseline_approved(self):
        a = preflight(self.base, self.root, self.history, NOW)
        self.assertTrue(a["publish_permitted"], a["issues"])
        self.assertIsNotNone(a["approval_digest"])

    def assertBlocked(self, changed, code):
        a=preflight(changed,self.root,self.history,NOW)
        self.assertFalse(a["publish_permitted"])
        self.assertIn(code, {e["code"] for e in a["issues"]})
        self.assertIsNone(a["approval_digest"])
        for e in a["issues"]:
            self.assertTrue(e["finding"] and e["resolution"])

    def test_ai_event_cover_blocked(self):
        x=copy.deepcopy(self.base)
        x["slides"][0]["media_kind"]="ai_generated"
        self.assertBlocked(x,"COVER_NOT_AUTHENTIC")
        self.assertBlocked(x,"PHOTO_RATIO")

    def test_generic_venue_cover_blocked(self):
        x=copy.deepcopy(self.base)
        x["slides"][0]["media_kind"]="venue_photo"
        x["slides"][0]["venue_is_subject"]=False
        self.assertBlocked(x,"COVER_NOT_RELEVANT")

    def test_unlicensed_photo_blocked(self):
        x=copy.deepcopy(self.base)
        x["slides"][0]["rights"]["evidence_url"]=""
        self.assertBlocked(x,"RIGHTS_MISSING")

    def test_duplicate_source_blocked(self):
        x=copy.deepcopy(self.base)
        x["slides"][0]["source_image_id"]="commons:eddie vedder 2018.jpg"
        self.assertBlocked(x,"MEDIA_DUPLICATE")

    def test_changed_image_after_approval_blocked(self):
        x=copy.deepcopy(self.base)
        x["slides"][0]["final_sha256"]="0"*64
        self.assertBlocked(x,"MEDIA_HASH_MISMATCH")

    def test_missing_service_in_caption_blocked(self):
        x=copy.deepcopy(self.base)
        x["caption"]=x["caption"].replace("Centro Cultural, Campinas", "outro local")
        self.assertBlocked(x,"SERVICE_CAPTION_MISMATCH")

    def test_missing_visual_cta_blocked(self):
        x=copy.deepcopy(self.base)
        x["slides"][0]["visible_text"]["cta"]=""
        self.assertBlocked(x,"CTA_MISSING")

    def test_stale_editorial_review_blocked(self):
        x=copy.deepcopy(self.base)
        x["editorial_review"]["checked_at"]="2026-11-21T14:00:00-03:00"
        self.assertBlocked(x,"REVIEW_STALE")

    def test_unknown_brand_blocked(self):
        x=copy.deepcopy(self.base)
        x["brand_id"]="123"
        self.assertBlocked(x,"WRONG_BRAND")

    def test_no_remote_duplicate_check_blocked(self):
        x=copy.deepcopy(self.base)
        x["remote_checks"]["duplicate_absent"]=False
        self.assertBlocked(x,"REMOTE_CHECK_MISSING")

    def test_scheduled_in_past_blocked(self):
        x=copy.deepcopy(self.base)
        x["publish_at"]="2026-11-25T13:00:00-03:00"
        self.assertBlocked(x,"SCHEDULE_INVALID")

    def test_artwork_exception_requires_reason(self):
        x=copy.deepcopy(self.base)
        x["editorial_subject_kind"]="authentic_artwork_itself"
        x["slides"][0]["media_kind"]="authentic_artwork"
        self.assertBlocked(x,"ARTWORK_EXCEPTION_INVALID")

    def test_no_user_approval_required(self):
        self.assertNotIn("human_review", self.base)
        self.assertTrue(preflight(self.base,self.root,self.history,NOW)["publish_permitted"])

    def test_legacy_human_only_blocked(self):
        x=copy.deepcopy(self.base)
        x["human_review"]=x.pop("editorial_review")
        self.assertBlocked(x,"REVIEW_MISSING")

    def test_legacy_policy_blocked_for_new_submission(self):
        x=copy.deepcopy(self.base)
        x["policy_version"]="entressala-metricool-extra-2026-11-25-v1"
        self.assertBlocked(x,"POLICY_UNKNOWN")

    def test_negative_assistant_decision_blocked(self):
        x=copy.deepcopy(self.base)
        x["editorial_review"]["decision"]="REJECTED"
        self.assertBlocked(x,"REVIEW_MISSING")

    def test_missing_editorial_evidence_blocked(self):
        x=copy.deepcopy(self.base)
        del x["editorial_review"]["findings"]["rights_evidence_checked"]
        self.assertBlocked(x,"REVIEW_MISSING")

    def test_review_caption_hash_mismatch_blocked(self):
        x=copy.deepcopy(self.base)
        x["caption"] += " Texto alterado depois da revisao."
        self.assertBlocked(x,"REVIEW_CONTENT_MISMATCH")

    def test_review_media_hash_mismatch_blocked(self):
        x=copy.deepcopy(self.base)
        x["editorial_review"]["reviewed_media_sha256"]=["0"*64]
        self.assertBlocked(x,"REVIEW_CONTENT_MISMATCH")

    def test_unidentified_reviewer_blocked(self):
        x=copy.deepcopy(self.base)
        x["editorial_review"]["reviewer"]="Editor sem identificacao"
        self.assertBlocked(x,"REVIEW_MISSING")

if __name__ == "__main__":
    unittest.main()
