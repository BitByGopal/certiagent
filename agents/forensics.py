"""Forensics agent: Error Level Analysis (ELA)."""
import io
import numpy as np
from PIL import Image, ImageChops

THRESHOLD = 2.41  # calibrated on 20 genuine certificates in the CA1 study


def ela(image: Image.Image, quality: int = 90):
    img = image.convert("RGB")
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=quality); buf.seek(0)
    diff = np.asarray(ImageChops.difference(img, Image.open(buf).convert("RGB"))).astype(np.float32).mean(axis=2)
    h, w = diff.shape; b = 16
    blocks = diff[: h // b * b, : w // b * b].reshape(h // b, b, w // b, b).mean(axis=(1, 3))
    active = blocks[blocks > 0.5]
    score = 0.0 if active.size < 20 else float(np.percentile(active, 99) / (np.median(active) + 1e-3))
    return score, diff


def run(image: Image.Image) -> dict:
    score, diff = ela(image)
    heat = (255 * np.clip(diff / (np.percentile(diff, 99.5) + 1e-6), 0, 1)).astype(np.uint8)
    return {"forensics": {"ela_score": round(score, 3), "threshold": THRESHOLD,
                          "suspicious": score > THRESHOLD}, "ela_map": Image.fromarray(heat)}
