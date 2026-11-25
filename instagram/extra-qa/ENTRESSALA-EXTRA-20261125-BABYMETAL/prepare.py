from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,hashlib,io,json
p=Path(__file__).parent
url="https://upload.wikimedia.org/wikipedia/commons/2/22/BABYMETAL%2C_O2_Arena%2C_London_%2831365068001%29.jpg"
r=requests.get(url,headers={"User-Agent":"ENTRESSALA editorial QA/1.0 (github.com/luisedferrari-ctrl/primeira-fila-revista)"},timeout=25)
r.raise_for_status()
assert hashlib.sha1(r.content).hexdigest()=="03756989268ee90b66e4dd348707b08b1700427e", "SOURCE_CHECKSUM_MISMATCH"
(p/"original.jpg").write_bytes(r.content)
im=Image.open(io.BytesIO(r.content)).convert("RGB")
assert im.size==(4608,3456)
ink=(9,16,25); ivory=(255,252,244); amber=(238,189,96)
canvas=ImageOps.fit(im,(1080,1350),Image.Resampling.LANCZOS,centering=(.50,.40)).convert("RGBA")
overlay=Image.new("RGBA",canvas.size);g=ImageDraw.Draw(overlay)
for y in range(170):g.line((0,y,1080,y),fill=(*ink,int(155*(1-y/170))))
for y in range(640,1350):g.line((0,y,1080,y),fill=(*ink,int(253*((y-640)/710)**.8)))
canvas=Image.alpha_composite(canvas,overlay).convert("RGB")
d=ImageDraw.Draw(canvas)
def f(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def line(y,t,s,c,b=False):
 while d.textlength(t,font=f(s,b))>950 and s>20:s-=1
 assert d.textlength(t,font=f(s,b))<=950
 d.text((64,y),t,font=f(s,b),fill=c)
line(48,"E N T R E S S A L A   /   MÚSICA",29,ivory,True)
d.line((64,110,1016,110),fill=amber,width=3)
line(740,"28 NOV 2026  /  SÃO PAULO",32,amber,True)
line(795,"BABYMETAL",88,ivory,True)
line(901,"VOLTA A SÃO PAULO",58,ivory,True)
line(981,"O METAL JAPONÊS NO ESPAÇO UNIMED",34,ivory,True)
d.line((64,1049,1016,1049),fill=amber,width=2)
line(1070,"SÁBADO, 21H  ·  PORTÕES ÀS 19H",34,amber,True)
line(1125,"INGRESSOS E DISPONIBILIDADE: EVENTIM.COM.BR",27,ivory,True)
line(1190,"Siga @entressala_ para descobrir grandes shows.",29,amber,True)
line(1270,"Foto: Drew de F Fawkes · Londres, 2016 · arquivo · CC BY 2.0",23,ivory)
out=p/"01.jpg";canvas.save(out,"JPEG",quality=94,subsampling=0,optimize=True)
canvas.resize((360,450),Image.Resampling.LANCZOS).save(p/"preview.jpg","JPEG",quality=92)
(p/"hashes.json").write_text(json.dumps({"original_sha1":hashlib.sha1(r.content).hexdigest(),"original_sha256":hashlib.sha256(r.content).hexdigest(),"final_sha256":hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
