#!/usr/bin/env python3
"""Generate ENTRESSALA Instagram carousels from individually verified CC photos.

Only creates review assets. It does NOT schedule, post, or change approval status.
Run: python3 tools/instagram/build_carousels.py
"""
import hashlib
import io
import json
import os
import pathlib
import textwrap
import time
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=pathlib.Path(__file__).resolve().parents[2]
OUTPUT=ROOT/"previews"/"entressala-2026-11-17"/"instagram"
ASSETS=OUTPUT/"originais"
OUTPUT.mkdir(parents=True,exist_ok=True)
ASSETS.mkdir(parents=True,exist_ok=True)
WIDTH,HEIGHT=1080,1350
GREEN="#14241F"; PAPER="#F3EDE1"; GOLD="#BDA579"
SOURCES={
"concerto":{"file":"Concerto na Sala São Paulo.jpg","author":"Henrique Boney","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2014","description":"Concerto real na Sala São Paulo, 2014"},
"parque":{"file":"Parque Ecológico - Indaiatuba - panoramio.jpg","author":"Danilo Bertelli","license":"CC BY 3.0","license_url":"https://creativecommons.org/licenses/by/3.0/","year":"2012","description":"Parque Ecológico de Indaiatuba, 2012"},
"estacao":{"file":"Estação Cultura Campinas.jpg","author":"Edison Marcon","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2018","description":"Estação Cultura de Campinas, 2018"},
"castro":{"file":"Teatro Castro Mendes (1).jpg","author":"Raphael Henrique Figueira","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2016","description":"Teatro Castro Mendes, Campinas"},
"pina":{"file":"Pinacoteca de São Paulo.jpg","author":"Nani carneiro","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","year":"2016","description":"Pinacoteca de São Paulo (Pina Luz), 2016"},
"eddie":{"file":"Eddie Vedder 2018.jpg","author":"Raph_PH","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","year":"2018","description":"Eddie Vedder em show de 2018 (foto de arquivo)"},
"roger":{"file":"Roger Daltrey (2008).jpg","author":"Mike Kubacheck","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","year":"2008","description":"Roger Daltrey em 2008 (foto de arquivo)"},
"edi":{"file":"Racionais MC's (12197895433).jpg","author":"Fernando Eduardo","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","year":"2013","description":"Edi Rock em apresentação de 2013 (foto de arquivo)"},
"pina_estacao":{"file":"Estação Pinacoteca - Largo General Osório, 66 – Luz - São Paulo - SP - panoramio (1).jpg","author":"CORRETOR-CARVALHO","license":"CC BY-SA 3.0","license_url":"https://creativecommons.org/licenses/by-sa/3.0/","year":"2012","description":"Edifício Pina Estação, 2012, não é foto da exposição"},
}
def get_photo(key):
    src=SOURCES[key]
    fn=src["file"].replace(" ","_")
    m=hashlib.md5(fn.encode("utf-8")).hexdigest()
    url=f"https://upload.wikimedia.org/wikipedia/commons/{m[0]}/{m[:2]}/{urllib.parse.quote(fn, safe='()')}"
    src["url"]="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(fn,safe="()")
    src["image_url"]=url
    path=ASSETS/(key+".jpg")
    if not path.exists():
        req=urllib.request.Request(url,headers={"User-Agent":"ENTRESSALA Cultural Magazine (licensed Wikimedia Commons image retrieval for social editorial)"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req,timeout=45) as response:
                    raw=response.read()
                with Image.open(io.BytesIO(raw)) as test:
                    if test.width<600 or test.height<600: raise ValueError("image too small")
                    rgb=ImageOps.exif_transpose(test).convert("RGB")
                    rgb.save(path,quality=95)
                break
            except Exception:
                if attempt==2: raise
                time.sleep(3+attempt*4)
    with Image.open(path) as photo:
        return photo.convert("RGB").copy()

def font_path(serif=False,bold=False):
    variants=[
        ("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf" if serif else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf" if serif else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf")
    ]
    for file in variants:
        if os.path.exists(file): return file
    raise RuntimeError("font unavailable")
def font(size,serif=False,bold=False):
    return ImageFont.truetype(font_path(serif,bold),size)
def lines_for(text,draw,ff,max_width,max_lines=4):
    out=[]
    for paragraph in text.split("\n"):
        if not paragraph.strip(): continue
        cur=""
        for token in paragraph.split(" "):
            test=(cur+" "+token).strip()
            if draw.textbbox((0,0),test,font=ff)[2]<=max_width:
                cur=test
            else:
                if cur: out.append(cur)
                cur=token
        if cur:out.append(cur)
    if len(out)>max_lines: raise ValueError("Text exceeds max lines: "+text)
    return out
def draw_text_lines(draw,lines,x,y,ff,fill,line_gap=13):
    ascent=ff.getmetrics()[0]+ff.getmetrics()[1]
    for line in lines:
        draw.text((x,y),line,font=ff,fill=fill,stroke_width=0)
        y+=ascent+line_gap
    return y

def image_canvas(photo):
    img=ImageOps.fit(photo,(WIDTH,HEIGHT),method=Image.Resampling.LANCZ,centering=(0.5,0.4))
    return img.convert("RGBA")
def gradient_overlay(img):
    layer=Image.new("RGBA",(WIDTH,HEIGHT),(13,25,22,0))
    px=layer.load()
    # Preserve upper photographic region; gentle bottom gradient protects legibility.
    for y in range(HEIGHT):
        t=y/HEIGHT
        a=int(13+240*(max(0,(t-0.37)/0.63)**1.25))
        for x in range(WIDTH):
            px[x,y]=(12,27,24,min(242,a))
    return Image.alpha_composite(img,layer)

SLIDES=[
{"id":"post01_01","photo":"concerto","section":"EDITORIAL  /  01","title":"ENTRESSALA","subtitle":"Uma revista sobre o que acontece entre Indaiatuba, Campinas e São Paulo.","cover":True},
{"id":"post01_02","photo":"parque","section":"INDAIATUBA","title":"A cultura começa perto.","subtitle":"Uma agenda que presta atenção também ao que acontece na nossa região."},
{"id":"post01_03","photo":"estacao","section":"CAMPINAS","title":"Campinas tem sua própria cena.","subtitle":"Música, festivais, teatro e lugares que fazem parte da cidade."},
{"id":"post01_04","photo":"concerto","section":"SÃO PAULO","title":"Algumas noites pedem estrada.","subtitle":"Um grande show, uma exposição, um espetáculo que vale a viagem."},
{"id":"post01_05","photo":"pina","section":"A REVISTA","title":"O programa é seu.\nA pesquisa é nossa.","subtitle":"Reportagens, seleção cultural e informação para decidir para onde ir."},
{"id":"post02_01","photo":"eddie","section":"NA AGENDA  /  20—22 NOV 2026","title":"Um fim de semana entre palcos e museus.","subtitle":"São Paulo e Campinas, com horários e fontes oficiais."},
{"id":"post02_02","photo":"eddie","section":"MÚSICA  /  SÃO PAULO","title":"Eddie Vedder no Ibirapuera","subtitle":"20 e 22 nov · ingressos esgotados (consulta em 17/11).","archive":True},
{"id":"post02_03","photo":"roger","section":"MÚSICA  /  SÃO PAULO","title":"Roger Daltrey e Chris Isaak","subtitle":"Sábado, 21 nov · bilheteria oficial com ingressos em 17/11.","archive":True},
{"id":"post02_04","photo":"edi","section":"MÚSICA  /  CAMPINAS","title":"Hip Hop Festival na Estação Cultura","subtitle":"Domingo, 22 nov · 13h às 22h · entrada gratuita.","archive":True},
{"id":"post02_05","photo":"pina_estacao","section":"ARTES  /  SÃO PAULO","title":"Sara Ramo na Pina Estação","subtitle":"A fúria dos restos vivos · em cartaz até 18 abr 2027.","place":True},
{"id":"post02_06","photo":"estacao","section":"ANTES DE SAIR","title":"Confira a programação oficial.","subtitle":"Ingressos, horários e acessibilidade podem mudar. Fontes e créditos na legenda.","place":True},
]
def make_slide(spec):
    photo=get_photo(spec["photo"])
    im=gradient_overlay(image_canvas(photo))
    d=ImageDraw.Draw(im)
    x=66
    d.rectangle((0,0,WIDTH,11),fill=PAPER)
    d.text((x,55),"ENTRESSALA",font=font(39,serif=True),fill=PAPER)
    d.text((WIDTH-118,66),spec["id"].split("_")[1].zfill(2)+" / "+("05" if spec["id"].startswith("post01") else "06"),font=font(24),fill=PAPER)
    # Rule below wordmark
    d.line([(x,128),(WIDTH-x,128)],fill=GOLD,width=2)
    d.text((x,700),spec["section"],font=font(28),fill=GOLD)
    # White editorial serif heading, sized to fit without blocking faces.
    title=spec["title"]
    size=(94 if spec.get("cover") else 76)
    while True:
        ff=font(size,serif=True)
        try:
            lines=lines_for(title,d,ff,WIDTH-130,max_lines=4)
            if len(lines)*int(size*1.38)<=360:break
        except ValueError:pass
        size-=2
        if size<43:raise ValueError(title)
    end=draw_text_lines(d,lines,x,760,ff,PAPER,7)
    dy=max(1090,end+30)
    fsub=font(32)
    desc=lines_for(spec["subtitle"],d,fsub,WIDTH-130,max_lines=3)
    draw_text_lines(d,desc,x,dy,fsub,PAPER,12)
    photo_info=SOURCES[spec["photo"]]
    if spec.get("archive"):
        d.rounded_rectangle((x,572,x+312,626),7,fill=(242,235,221,245))
        d.text((x+17,581),"FOTO DE ARQUIVO",font=font(25),fill=GREEN)
    if spec.get("place"):
        d.rounded_rectangle((x,572,x+265,626),7,fill=(242,235,221,245))
        d.text((x+17,581),"FOTO DO LOCAL",font=font(25),fill=GREEN)
    d.line([(x,1282),(WIDTH-x,1282)],fill=GOLD,width=2)
    credit=f"Foto: {photo_info['author']} · {photo_info['year']} · {photo_info['license']}"
    d.text((x,1301),credit,font=font(22),fill=PAPER)
    out=OUTPUT/(spec["id"]+".png")
    im.convert("RGB").save(out,optimize=True)
    return str(out)

def montage(files,post):
    items=[Image.open(f).convert("RGB") for f in files]
    thumbW=320;thumbH=400;cols=3;rows=(len(items)+cols-1)//cols
    sheet=Image.new("RGB",(cols*thumbW+(cols+1)*18,rows*thumbH+(rows+1)*18),color="#EFEAE1")
    for i,p in enumerate(items):
        z=p.resize((thumbW,thumbH),Image.Resampling.LANCZ)
        sheet.paste(z,(18+(i%cols)*(thumbW+18),18+(i//cols)*(thumbH+18)))
    sheet.save(OUTPUT/("PREVIA_"+post+".jpg"),quality=90)
results=[]
for slide in SLIDES:
    results.append(make_slide(slide))
montage(results[:5],"POST01")
montage(results[5:],"POST02")
manifest={
 "status":"ARTWORK_GENERATED_NOT_PUBLISHED","created_at":"2026-11-17",
 "img_count":len(results),"channel":"@entressala_",
 "published":False,"scheduled":False,
 "approval_note":"User said pode partir para as publicações; final rendered assets still require QA prior to scheduling.",
 "slides":SLIDES,"sources":SOURCES,
 "event_references":[
 "https://www.ticketmaster.com.br/event/best-of-blues-and-rock",
 "https://campinas.sp.gov.br/noticias/estacao-cultura-recebe-13-edicao-do-campinas-hip-hop-festival-no-dia-22-de-novembro-151750",
 "https://pinacoteca.org.br/programacao/exposicoes/sara-ramo/"
 ]}
(OUTPUT/"CREDITOS_E_CONTROLE.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print("Generated",len(results),"PNGs at",OUTPUT)
