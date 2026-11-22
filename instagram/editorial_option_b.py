"""ENTRESSALA option B: regional-first cultural news, announcements and event coverage.
Pure validation/rendering only. Never schedules or publishes anything.
"""
import re
import unicodedata
from PIL import Image, ImageDraw, ImageOps

OPTION_B_FROM = "2026-11-23"
ALLOWED_SCOPES = ("regional", "brasil", "internacional")


def is_option_b_post(post):
    return str(post.get("publish_local_date", "")) >= OPTION_B_FROM


def slide_service(post, slide):
    services = post.get("service_items") or []
    if not services:
        raise ValueError("Verified service_items required for news-first publication")
    if len({s.get("kind") for s in services}) > 1 and "service_index" not in slide:
        raise ValueError("Mixed news/event carousel requires service_index on every slide")
    index = slide.get("service_index", 0)
    if isinstance(index, bool) or not isinstance(index, int) or not (0 <= index < len(services)):
        raise ValueError("Invalid service_index for editorial carousel")
    return services[index]


def validate_news_service(service, caption, post_id, factual_sources, url_validator):
    if service.get("verified") is not True:
        raise ValueError("News item must be independently verified: " + post_id)
    for key in ("when", "topic", "source_name", "source_url"):
        value = str(service.get(key) or "").strip()
        if len(value) < (15 if key in ("topic", "source_url") else 4):
            raise ValueError("News item missing verified " + key + ": " + post_id)
        if unicodedata.normalize("NFKC", value).casefold() not in unicodedata.normalize("NFKC", caption).casefold():
            raise ValueError("Caption omits news " + key + ": " + post_id)
    if not re.search(r"\b20\d{2}\b", str(service["when"])):
        raise ValueError("News must identify a real date/year: " + post_id)
    url_validator(service["source_url"])
    if service["source_url"] not in factual_sources:
        raise ValueError("News source_url missing from factual_sources: " + post_id)


def validate_option_b_post(post):
    if post.get("editorial_scope") not in ALLOWED_SCOPES:
        raise ValueError("Option B requires editorial_scope regional/brasil/internacional: " + post["id"])
    angle = str(post.get("editorial_angle") or "").strip()
    if len(angle) < 18 or len(angle.split()) < 4:
        raise ValueError("Option B requires a specific journalistic editorial_angle: " + post["id"])
    return True


def validate_option_b_slide(post, slide, number):
    service = slide_service(post, slide)
    kind = service["kind"]
    if len(str(slide.get("title") or "").strip()) < 14:
        raise ValueError("News-first cover must contain a concrete headline: " + post["id"])
    if not str(slide.get("eyebrow") or "").strip():
        raise ValueError("News-first image needs an editorial section label: " + post["id"])
    if kind == "news":
        for field in ("subject_label", "news_deck"):
            if not str(slide.get(field) or "").strip():
                raise ValueError("News image lacks " + field + ": " + post["id"])
    else:
        for field in ("venue_label", "ticket_label"):
            if not str(slide.get(field) or "").strip():
                raise ValueError("Visible " + ("VENUE" if field == "venue_label" else "TICKETS") +
                                 " is mandatory on every NEW slide: " + post["id"])
        if kind == "radar":
            date = unicodedata.normalize("NFKD", str(slide["date_label"]).upper()).encode(
                "ascii", "ignore").decode("ascii")
            tickets = unicodedata.normalize("NFKD", str(slide["ticket_label"]).upper()).encode(
                "ascii", "ignore").decode("ascii")
            if "DATAS A ANUNCIAR" not in date or "INGRESSOS AINDA NAO DIVULGADOS" not in tickets:
                raise ValueError("Radar image must show unannounced dates and tickets: " + post["id"])
    if not str(slide.get("link_label") or "").strip():
        raise ValueError("Verified source link label missing on news-first card: " + post["id"])
    return True


def _one_line(draw, text, y, get_font, color, max_width=950, size=28, min_size=18, bold=False):
    value = str(text).strip()
    if not value:
        raise ValueError("News-first visual has a blank service line")
    for sz in range(size, min_size - 1, -1):
        font = get_font("sans_bold" if bold else "sans", sz)
        bb = draw.textbbox((0, 0), value, font=font)
        if bb[2] - bb[0] <= max_width:
            draw.text((65, y), value, font=font, fill=color)
            return
    raise ValueError("News-first line cannot fit at readable size: " + value[:100])


def _headline_lines(draw, text, get_font, max_width=950):
    for sz in range(82, 49, -2):
        font = get_font("sans_bold", sz)
        lines, current = [], ""
        for word in str(text).strip().upper().split():
            trial = (current + " " + word).strip()
            if current and draw.textbbox((0, 0), trial, font=font)[2] > max_width:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
        if len(lines) <= 3 and all(draw.textbbox((0, 0), l, font=font)[2] <= max_width for l in lines):
            if 720 + len(lines) * int(sz * 1.12) <= 1030:
                return font, lines
    raise ValueError("News-first headline too long to fit image: " + str(text)[:90])


def draw_news_first_card(photo, post, slide, number, total, get_font):
    """Use authentic source images, strong original typography and compact service."""
    service = slide_service(post, slide)
    kind = service["kind"]
    w, h = 1080, 1350
    im = ImageOps.fit(photo, (w, h), method=Image.Resampling.LANCZOS,
                      centering=(0.5, 0.42)).convert("RGBA")
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad = ImageDraw.Draw(shade)
    for y in range(145):
        grad.line((0, y, w, y), fill=(8, 13, 20, int(112 * (1 - y / 145))))
    for y in range(550, h):
        amount = (y - 550) / 800
        grad.line((0, y, w, y), fill=(9, 16, 25, int(242 * (amount ** 0.68))))
    im = Image.alpha_composite(im, shade)
    d = ImageDraw.Draw(im)
    cream, gold = (255, 252, 244), (238, 189, 96)
    d.text((65, 48), "E N T R E S S A L A", font=get_font("sans_bold", 28), fill=cream)
    d.text((878, 54), "{:02d}/{:02d}".format(number, total), font=get_font("sans", 25), fill=cream)
    d.line((65, 108, 1015, 108), fill=gold, width=3)
    _one_line(d, str(slide["eyebrow"]).upper(), 136, get_font, cream, size=25)
    _one_line(d, "{}  ·  {}".format(slide["date_label"], slide["city"]).upper(),
              680, get_font, gold, size=28, bold=True)
    font, lines = _headline_lines(d, slide["title"], get_font)
    cursor = 720
    for line in lines:
        d.text((65, cursor), line, font=font, fill=cream, stroke_width=1, stroke_fill=(5, 13, 18))
        cursor += int(font.size * 1.12)
    sub_y = max(955, cursor + 4)
    if sub_y + 44 > 1092:
        raise ValueError("Headline/subtitle overlap with service area: " + post["id"])
    _one_line(d, slide["subtitle"], sub_y, get_font, cream, size=28, min_size=21)
    d.line((65, 1085, 1015, 1085), fill=(170, 161, 144), width=2)
    if kind == "news":
        row1 = "ASSUNTO: " + str(slide["subject_label"])
        row2 = str(slide["news_deck"])
        row3 = "FONTE: " + str(slide["link_label"])
    else:
        row1 = "LOCAL: " + str(slide["venue_label"])
        row2 = str(slide["ticket_label"])
        row3 = "SITE: " + str(slide["link_label"])
    _one_line(d, row1, 1102, get_font, gold, size=25, min_size=19)
    _one_line(d, row2, 1145, get_font, cream, size=25, min_size=19)
    _one_line(d, row3, 1188, get_font, cream, size=23, min_size=19)
    if number == total:
        _one_line(d, slide["cta_label"], 1234, get_font, gold, size=26, min_size=20, bold=True)
    else:
        _one_line(d, "ENTRESSALA  ·  CULTURA EM FOCO", 1234, get_font, gold, size=23)
    d.line((65, 1293, 1015, 1293), fill=(170, 161, 144), width=2)
    label = "Arte" if slide.get("asset_type") == "official_poster" else "Foto"
    credit = "{}: {}".format(label, slide["photographer"])
    if "ARQUIVO" in str(slide.get("context") or "").upper() or slide.get("is_archival"):
        credit += " · arquivo"
    _one_line(d, credit, 1305, get_font, cream, size=18, min_size=17)
    return im.convert("RGB")
