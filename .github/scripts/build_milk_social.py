#!/usr/bin/env python3
"""Create a 1200x630 original-photo sharing image from the existing family photo."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
INK=(24,58,69)
PINE=(55,88,77)
PAPER=(251,249,244)
RULE=(195,201,189)

def font(sz, serif=False, italic=False, bold=False):
    base="/usr/share/fonts/truetype/dejavu/"
    name=("DejaVuSerif" if serif else "DejaVuSans") + ("-Italic" if italic else "-Bold" if bold else "") + ".ttf"
    path=Path(base+name)
    return ImageFont.truetype(str(path),sz) if path.exists() else ImageFont.load_default()

def render(root):
    original=root/"assets/family-notes/straw-lid-tip.webp"
    target=root/"assets/family-notes/milk-straw-og.jpg"
    if not original.is_file():
        raise FileNotFoundError(original)
    canvas=Image.new("RGB",(1200,630),PAPER)
    d=ImageDraw.Draw(canvas)
    d.rectangle((0,0,1200,12),fill=PINE)
    d.line((76,73,1124,73),fill=RULE,width=2)
    d.text((84,111),"THE FAMILY NOTEBOOK  /  NO. 01",font=font(19,bold=True),fill=PINE)
    d.text((81,177),"Sometimes the",font=font(65,serif=True),fill=INK)
    d.text((81,262),"straw is the",font=font(65,serif=True),fill=INK)
    d.text((81,347),"whole trick.",font=font(69,serif=True,italic=True),fill=INK)
    d.line((84,452,659,452),fill=RULE,width=2)
    d.text((84,478),"A familiar drink. A little kitchen fix.",font=font(25,serif=True),fill=PINE)
    d.text((84,519),"The practical details left in.",font=font(25,serif=True),fill=PINE)
    d.rectangle((788,97,1120,559),fill=(226,225,217))
    d.rectangle((777,86,1109,548),fill=(255,255,255))
    with Image.open(original) as img:
        img=img.convert("RGB")
        img.thumbnail((286,415),Image.Resampling.LANCZOS)
        x=777+(332-img.width)//2
        y=97+(415-img.height)//2
        canvas.paste(img,(x,y))
    d=ImageDraw.Draw(canvas)
    d.text((803,513),"FROM OUR OWN KITCHEN",font=font(12,bold=True),fill=PINE)
    d.line((76,577,1124,577),fill=RULE,width=2)
    d.text((82,588),"AN AUSOME LIFE",font=font(17,bold=True),fill=INK)
    d.text((357,588),"NEW ENGLAND  &  THE EVERYDAY",font=font(17),fill=PINE)
    target.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(target,quality=83,optimize=True,progressive=True)
    print("GENERATED_SOCIAL_PREVIEW",target,target.stat().st_size)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path("_site"))
    render(p.parse_args().root)
