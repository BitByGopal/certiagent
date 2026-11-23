"""Run every certificate in data/certificates through the graph and report accuracy.
python evaluate.py rules      (fast, no API)
python evaluate.py llm        (uses Gemini; ~2 calls per image, mind the free-tier limits)"""
import sys, time, glob, json
from pathlib import Path
import pandas as pd
from PIL import Image
from graph import verify

mode = sys.argv[1] if len(sys.argv) > 1 else "rules"
rows = []
for p in sorted(glob.glob("data/certificates/*.png")):
    label = Path(p).stem.split("_", 1)[1]
    t = time.time(); out = verify(Image.open(p), mode)
    rows.append(dict(file=Path(p).name, kind=label, truth="genuine" if label == "genuine" else "fake",
                     verdict=out["verdict"], registry=out["registry"]["status"], ela=out["forensics"]["ela_score"],
                     mode=out["extraction_mode"], seconds=round(time.time() - t, 2)))
    print(rows[-1])
    if mode == "llm": time.sleep(12)   # stay under free-tier requests-per-minute
df = pd.DataFrame(rows); df.to_csv(f"results_{mode}.csv", index=False)
df["flagged"] = df.verdict != "GENUINE"
fake = df.truth == "fake"
print("\n=== Summary (", mode, ") ===")
print("Fakes caught      :", int((df.flagged & fake).sum()), "/", int(fake.sum()))
print("Genuine flagged   :", int((df.flagged & ~fake).sum()), "/", int((~fake).sum()))
print("Sent to REVIEW    :", int((df.verdict == "REVIEW").sum()))
print("Mean seconds/doc  :", round(df.seconds.mean(), 2))
print(pd.crosstab(df.kind, df.verdict))
