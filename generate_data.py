"""Create the synthetic registry and test certificates (same recipe as the CA1 paper).
Run once:  python generate_data.py
Output: data/registry.csv and data/certificates/*.png  (file name ends with the true label)."""
import io, random
from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter

random.seed(7)
ROOT = Path(__file__).resolve().parent / "data"; OUT = ROOT / "certificates"; OUT.mkdir(parents=True, exist_ok=True)


def font(bold: bool, serif: bool, size: int):
    names = (["DejaVuSerif-Bold.ttf", "timesbd.ttf", "georgiab.ttf"] if bold else ["DejaVuSerif.ttf", "times.ttf", "georgia.ttf"]) if serif \
        else ["DejaVuSans.ttf", "arial.ttf"]
    for n in names:
        for base in ["", "/usr/share/fonts/truetype/dejavu/", "C:/Windows/Fonts/", "/Library/Fonts/"]:
            try: return ImageFont.truetype(base + n, size)
            except OSError: pass
    return ImageFont.load_default(size)


FIRST = ["Aarav","Vivaan","Aditya","Sai","Arjun","Reyansh","Krishna","Ishaan","Rohan","Kiran","Ananya","Diya","Priya","Sneha","Kavya",
         "Meera","Lakshmi","Pooja","Divya","Riya","Rahul","Vikram","Suresh","Naveen","Harsha","Deepak","Manoj","Sanjay","Ravi","Teja"]
LAST = ["Sharma","Reddy","Yadav","Kumar","Naidu","Verma","Gupta","Rao","Singh","Patel","Iyer","Nair","Das","Mishra","Choudhary","Joshi"]
UNIS = ["Jharkhand State University", "Ranchi Institute of Technology", "Dhanbad College of Engineering"]
PROGS = ["Bachelor of Technology", "Bachelor of Science", "Master of Computer Applications"]
BG = (252, 249, 240); W, H = 1400, 990


def record(used):
    while True:
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        if name not in used: used.add(name); break
    return dict(cert_id=f"JH{random.randint(100000, 999999)}", name=name, roll=f"{random.randint(20,23)}{random.randint(10000,99999)}",
                university=random.choice(UNIS), program=random.choice(PROGS), year=str(random.randint(2021, 2025)),
                cgpa=f"{random.uniform(6.0, 9.6):.2f}")


def render(r):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([20, 20, W-20, H-20], outline=(120, 80, 30), width=6); d.rectangle([38, 38, W-38, H-38], outline=(170, 130, 60), width=2)
    d.text((W/2, 110), r["university"], font=font(True, True, 46), fill=(30, 40, 90), anchor="mm")
    d.text((W/2, 175), "PROVISIONAL DEGREE CERTIFICATE", font=font(True, True, 30), fill=(120, 40, 30), anchor="mm")
    d.text((W/2, 260), "This is to certify that", font=font(False, True, 28), fill=(20, 20, 20), anchor="mm")
    d.text((W/2, 325), r["name"], font=font(True, True, 44), fill=(10, 10, 10), anchor="mm")
    d.text((W/2, 395), f"has been awarded the degree of {r['program']}", font=font(False, True, 28), fill=(20, 20, 20), anchor="mm")
    for i, t in enumerate([f"Roll Number: {r['roll']}", f"Year of Passing: {r['year']}", f"CGPA: {r['cgpa']}", f"Certificate ID: {r['cert_id']}"]):
        d.text((180, 500 + i*62), t, font=font(False, False, 30), fill=(20, 20, 20))
    cx, cy = 1080, 640
    d.ellipse([cx-110, cy-110, cx+110, cy+110], outline=(150, 30, 30), width=5); d.ellipse([cx-90, cy-90, cx+90, cy+90], outline=(150, 30, 30), width=2)
    d.text((cx, cy), "SEAL", font=font(True, True, 34), fill=(150, 30, 30), anchor="mm")
    d.line([180, 860, 480, 860], fill=(40, 40, 40), width=2); d.text((180, 875), "Controller of Examinations", font=font(False, True, 22), fill=(40, 40, 40))
    return im


def jpeg(im, q=90):
    b = io.BytesIO(); im.save(b, "JPEG", quality=q); b.seek(0); return Image.open(b).convert("RGB")


def noise(im):
    if random.random() < 0.5: im = im.filter(ImageFilter.GaussianBlur(random.uniform(0.3, 0.8)))
    if random.random() < 0.3: im = im.rotate(random.uniform(-1, 1), fillcolor=BG)
    return im


def main():
    used = set(); reg = [record(used) for _ in range(120)]
    pd.DataFrame(reg).to_csv(ROOT / "registry.csv", index=False)
    n = 0
    def save(im, label):
        nonlocal n; jpeg(noise(im)).save(OUT / f"{n:03d}_{label}.png"); n += 1
    for r in reg[:30]: save(render(r), "genuine")
    for r in reg[30:40]:
        im = jpeg(render(r)); d = ImageDraw.Draw(im); new = f"{min(9.9, float(r['cgpa']) + random.uniform(0.8, 2.0)):.2f}"
        d.rectangle([175, 620, 760, 666], fill=BG); d.text((180, 624), f"CGPA: {new}", font=font(False, False, 30), fill=(20, 20, 20))
        save(im, "marks_edit")
    for r in reg[40:50]:
        im = jpeg(render(r)); d = ImageDraw.Draw(im); other = f"{random.choice(FIRST)} {random.choice(LAST)}"
        d.rectangle([250, 295, W-250, 360], fill=BG); d.text((W/2, 325), other, font=font(True, True, 44), fill=(10, 10, 10), anchor="mm")
        save(im, "name_swap")
    ids = {x["cert_id"] for x in reg}
    for _ in range(10):
        fake = record(used)
        while fake["cert_id"] in ids: fake["cert_id"] = f"JH{random.randint(100000, 999999)}"
        save(render(fake), "fabricated")
    print(f"registry.csv: {len(reg)} records | certificates: {n} images in {OUT}")


if __name__ == "__main__":
    main()
