"""Single isolated editorial preparation, no publishing."""
import hashlib, json, io, subprocess, sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
BRANCH="entressala-qa-cliff-booth-20261125"
BASE_URL="https://raw.githubusercontent.com/luisedferrari-ctrl/primeira-fila-revista/"+BRANCH+"/instagram/extra-qa/ENTRESSALA-EXTRA-20261125-CLIFF-BOOTH/"
source="https://upload.wikimedia.org/wikipedia/commons/4/4c/Brad_Pitt_2019_by_Glenn_Francis.jpg"
license_source="https://commons.wikimedia.org/wiki/File:Brad_Pitt_2019_by_Glenn_Francis.jpg"
official="https://www.netflix.com/tudum/articles/david-fincher-new-film-release-date"
regional="https://www.omelete.com.br/filmes/cliff-booth-quais-salas-passarao-no-brasil"
sessions="https://www.ingresso.com/cinema/kinoplex-dom-pedro?city=campinas"
now=datetime.now(ZoneInfo("America/Sao_Paulo"))
# Exact licensed original; never replace with synthetic image or arbitrary thumbnail.
r=requests.get(source,headers={"User-Agent":"ENTRESSALA editorial QA/1.0 (github.com/luisedferrari-ctrl/primeira-fila-revista)"},timeout=40)
r.raise_for_status()
assert r.headers.get("Content-Type","").startswith("image/"),"SOURCE_NOT_IMAGE"
source_bytes=r.content
photo=Image.open(io.BytesIO(source_bytes)).convert("RGB")
assert min(photo.size)>=1000, "SOURCE_RESOLUTION_INSUFFICIENT"
original_hash=hashlib.sha256(source_bytes).hexdigest()
(ROOT/"original.jpg").write_bytes(source_bytes)
W,H=1080,1350
ink=(9,16,25)
cream=(255,252,244)
amber=(238,189,96)
muted=(210,214,219)
reg="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(n,b=False): return ImageFont.truetype(bold if b else reg,n)
def line(d,xy,t,sz,col,b=False,maxw=950):
    while d.textlength(t,font=f(sz,b))>maxw and sz>20: sz-=1
    assert d.textlength(t,font=f(sz,b))<=maxw, t
    d.text(xy,t,font=f(sz,b),fill=col)
canvas=Image.new("RGB",(W,H),ink)
crop=ImageOps.fit(photo,(W,1030),Image.Resampling.LANCZOS,centering=(.5,0.0))
canvas.paste(crop,(0,0))
canvas=canvas.convert("RGBA")
overlay=Image.new("RGBA",(W,H))
od=ImageDraw.Draw(overlay)
for y in range(190):
    od.line((0,y,W,y),fill=(*ink,int(170*(1-y/190))))
for y in range(670,1030):
    a=int(255*((y-670)/360)**1.2)
    od.line((0,y,W,y),fill=(*ink,a))
canvas=Image.alpha_composite(canvas,overlay).convert("RGB")
d=ImageDraw.Draw(canvas)
line(d,(64,48),"E N T R E S S A L A",30,cream,True)
line(d,(824,53),"CINEMA",28,cream,True,maxw=192)
d.line((64,111,1016,111),fill=amber,width=3)
line(d,(64,745),"25 NOV 2026  /  BRASIL",30,amber,True)
line(d,(62,790),"NOVO FILME DE",62,cream,True)
line(d,(62,864),"BRAD PITT",92,cream,True)
line(d,(62,970),"SÓ EM 2 CINEMAS NO BRASIL",56,cream,True)
line(d,(65,1050),"CAMPINAS É UM DELES.",49,amber,True)
d.line((65,1120,1015,1120),fill=(116,128,141),width=2)
line(d,(65,1139),"CLIFF BOOTH  ·  IMAX  ·  KINOPLEX DOM PEDRO",31,cream,True)
line(d,(65,1180),"NETFLIX: 23 DE DEZEMBRO  ·  FONTE: NETFLIX / OMELETE",26,muted)
line(d,(65,1226),"Siga @entressala_ para descobrir o que vale ver.",30,amber,True)
line(d,(65,1278),"Foto: Glenn Francis / PacificProDigital.com · arquivo 2019 · CC BY-SA 4.0",20,muted)
out=ROOT/"01.jpg"
canvas.save(out,"JPEG",quality=95,optimize=True,subsampling=0)
canvas.resize((360,450),Image.Resampling.LANCZOS).save(ROOT/"preview.jpg","JPEG",quality=92)
headline="NOVO FILME DE BRAD PITT SÓ EM 2 CINEMAS NO BRASIL"
caption="""Brad Pitt volta ao papel que lhe rendeu um Oscar — e Campinas está no circuito restrito do novo filme.

As Novas Desventuras de Cliff Booth estreia em IMAX em 25/11/2026. Com direção de David Fincher e roteiro de Quentin Tarantino, a produção retoma o personagem de Era Uma Vez em... Hollywood, agora em 1977.

Segundo a assessoria do IMAX Brasil, em informação publicada pelo Omelete, apenas duas salas brasileiras receberão o longa: Campinas e Curitiba.

EM CAMPINAS: Kinoplex Dom Pedro, Av. Guilherme Campos, 500, Jardim Santa Genebra. Consulte horários, preço e disponibilidade em https://www.ingresso.com/cinema/kinoplex-dom-pedro?city=campinas.
NA NETFLIX: 23 de dezembro de 2026.
Fonte oficial: https://www.netflix.com/tudum/articles/david-fincher-new-film-release-date
Cobertura regional: https://www.omelete.com.br/filmes/cliff-booth-quais-salas-passarao-no-brasil

Você assistiria no IMAX ou esperaria chegar ao streaming? Envie para quem gosta de cinema.
Siga @entressala_ para descobrir as grandes estreias e experiências culturais que valem a sua atenção.

Foto de arquivo: © Glenn Francis, www.PacificProDigital.com (pré-estreia de Era Uma Vez em... Hollywood, 2019). Wikimedia Commons. Corte e diagramação ENTRESSALA; arte adaptada sob CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/

#ENTRESSALA #BradPitt #Cinema #Campinas #CliffBooth #Netflix"""
(ROOT/"legenda.txt").write_text(caption+"\n",encoding="utf-8")
notes="""# Evidências editoriais — candidato Cliff Booth

Estado: candidato, sem aprovação humana independente e sem autorização de envio.

Fontes consultadas em 25/11/2026, aproximadamente 16h15 BRT:
- Netflix Tudum (notícia atualizada em 25/11): """+official+"""
- Omelete (assessoria IMAX Brasil): """+regional+"""
- AdoroCinema, programação de Campinas: https://www.adorocinema.com/programacao/cinema-F0286/
- Ingresso.com (cinema e compra): """+sessions+"""
- Licença e titular da fotografia: """+license_source+"""
- Original exato: """+source+"""
- Autor: © Glenn Francis, www.PacificProDigital.com; 22/07/2019, pré-estreia de Era Uma Vez em... Hollywood. CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/
- Alterações: corte, escala, gradiente, manchete e design; composição adaptada distribuída sob CC BY-SA 4.0. Não é foto da nova produção, não implica endosso.
- Metricool marca 8230360: conta Instagram entressala_ conectada; consulta de posts 18/11 a 02/12 não encontrou Brad Pitt/Cliff Booth; Matsuri PUBLISHED. Fila regular no piloto: Fôlego previsto para 25/11, assunto diferente; não modificar a fila. Horário apenas proposto: 20h30 BRT, fora da janela regular ~19h, sujeito à reconciliação e à revisão humana.
- Histórico image-history.json do piloto: não consta a fonte Brad Pitt 2019 by Glenn Francis.jpg. Histórico não prova por si só ausência absoluta de duplicata; revisão humana e verificação visual ainda necessárias.

Não preencher flags de revisão humana sem revisão efetiva. Não agendar, não enviar ao Metricool, não modificar automações regulares.
"""
(ROOT/"EVIDENCIAS.md").write_text(notes,encoding="utf-8")
checked="2026-11-25T16:15:00-03:00"
manifest={
"policy_version":"entressala-metricool-extra-2026-11-25-v1","publication_channel":"metricool_extra","brand_id":"8230360","id":"ENTRESSALA-EXTRA-20261125-CLIFF-BOOTH",
"publish_at":"2026-11-25T20:30:00-03:00","content_kind":"news","subject":"Brad Pitt — As Novas Desventuras de Cliff Booth","headline":headline,
"novelty":"Estreia IMAX em 25/11/2026, com circuito brasileiro restrito e chegada à Netflix em 23/12.",
"recognition_signal":"Brad Pitt, vencedor do Oscar pelo papel de Cliff Booth, em filme de David Fincher com roteiro de Quentin Tarantino; interesse em cinema popular.",
"share_reason":"Campinas é uma das duas praças brasileiras citadas pelo IMAX Brasil; informação útil e surpreendente para fãs e moradores.",
"official_source":{"name":"Netflix Tudum","url":official,"checked_at":checked},
"service":{"when":"25/11/2026","what":"As Novas Desventuras de Cliff Booth","context":"Campinas e Curitiba","official_url":official},
"caption":caption,"slides":[{"file":"01.jpg","final_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"source_image_sha256":original_hash,"source_image_id":"commons:brad pitt 2019 by glenn francis.jpg","media_url":BASE_URL+"01.jpg","media_kind":"authentic_photo","subject_specific":True,"rights":{"license":"CC BY-SA","holder":"Glenn Francis / PacificProDigital.com","credit":"© Glenn Francis, www.PacificProDigital.com · arquivo 2019 · CC BY-SA 4.0","evidence_url":license_source},"visible_text":{"headline":headline,"when":"25 NOV 2026","where":"Kinoplex Dom Pedro, Campinas","source":"Netflix / Omelete","cta":"Siga @entressala_ para descobrir o que vale ver."}}],
"human_review":{},
"remote_checks":{"brand_connected":True,"duplicate_absent":True,"checked_at":checked,"evidence_url":BASE_URL+"EVIDENCIAS.md"}}
(ROOT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
# Real gate must fail closed: no independent human review was conducted.
ret=subprocess.run([sys.executable,"instagram/metricool_gate.py","--manifest",str(ROOT/"manifest.json"),"--assets-root",str(ROOT),"--history","instagram/image-history.json","--report",str(ROOT/"report.json")],check=False)
assert ret.returncode==2, "EXPECTED BLOCKED: human review absent, never auto-authorize"
report=json.loads((ROOT/"report.json").read_text())
assert report["verdict"]=="BLOCKED"
print("GATE:",report["verdict"],[i["code"] for i in report["issues"]])
