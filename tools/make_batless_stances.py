#!/usr/bin/env python3
"""Pose data for the bat swing. Does not rewrite the kid paintings.

art/char_<id>_batless.png are painted source files (ComfyUI). Running this
script leaves those PNGs alone. Hand pivots and the cocked-bat angle live in
art/bat_poses.json, which the game reads.

  python3 tools/make_batless_stances.py
      prints the pose file and does not write images

  python3 tools/make_batless_stances.py --measure-bat
      refreshes only the art/bat.png grip block inside bat_poses.json
"""
from __future__ import annotations

import colorsys
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"
IDS = ["duke", "lou", "tank", "ricky", "milo", "pearl", "walt", "peewee"]


def is_wood(r: int, g: int, b: int) -> bool:
    if r < 175 or g < 125 or b > 160:
        return False
    if g - b < 42 or g - b > 90:
        return False
    if r - g > 78 or r - g < 20:
        return False
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return 0.07 <= h <= 0.125 and 0.40 <= s <= 0.66 and 0.70 <= v <= 0.99


def is_highlight(r: int, g: int, b: int) -> bool:
    return r > 215 and g > 185 and b > 145 and (r - b) < 100 and g > b


def is_dark(r: int, g: int, b: int) -> bool:
    return max(r, g, b) < 95 and (r + g + b) < 230


def is_knob(r: int, g: int, b: int) -> bool:
    if r < 185 or g < 140 or b < 55 or b > 165:
        return False
    return abs(r - g) < 75 and g > b + 6


def neighbors(x: int, y: int, w: int, h: int):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                yield nx, ny


def find_seed(img: np.ndarray):
    h, w = img.shape[:2]
    alpha = img[:, :, 3] > 40
    ys, xs = np.where(alpha & (np.arange(h)[:, None] > int(h * 0.55)))
    if len(xs) < 10:
        ys, xs = np.where(alpha)
    cx, cy = float(xs.mean()), float(ys.mean())
    ys, xs = np.where(alpha)
    score = (cx - xs) + (cy - ys) * 0.85
    score = np.where(ys < h * 0.78, score, -1e9)
    i = int(score.argmax())
    x, y = int(xs[i]), int(ys[i])
    for t in np.linspace(0.04, 0.35, 18):
        xx = int(np.clip(round(x + (cx - x) * t), 0, w - 1))
        yy = int(np.clip(round(y + (cy - y) * t), 0, h - 1))
        r, g, b, a = (int(v) for v in img[yy, xx])
        if a > 220 and is_wood(r, g, b):
            return xx, yy, cx, cy
    raise RuntimeError("no wood seed")


def flood_wood(img: np.ndarray, sx: int, sy: int) -> np.ndarray:
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    q = deque([(sx, sy)])
    mask[sy, sx] = 1
    while q:
        x, y = q.popleft()
        for nx, ny in neighbors(x, y, w, h):
            if mask[ny, nx] or img[ny, nx, 3] < 70:
                continue
            r, g, b = (int(v) for v in img[ny, nx, :3])
            if is_wood(r, g, b) or is_highlight(r, g, b):
                mask[ny, nx] = 1
                q.append((nx, ny))
    return mask


def near_transparent(alpha: np.ndarray, radius: int = 26) -> np.ndarray:
    """True where a transparent pixel sits within `radius` (box, then refine)."""
    h, w = alpha.shape
    inv = alpha < 30
    # Integral image of transparent pixels for a fast box test, then a
    # tighter circle check only on candidates.
    integ = np.zeros((h + 1, w + 1), np.int32)
    integ[1:, 1:] = np.cumsum(np.cumsum(inv.astype(np.int32), axis=0), axis=1)
    ys, xs = np.where(alpha > 40)
    free = np.zeros((h, w), np.uint8)
    r = radius
    for x, y in zip(xs.tolist(), ys.tolist()):
        x0, y0 = max(0, x - r), max(0, y - r)
        x1, y1 = min(w - 1, x + r), min(h - 1, y + r)
        count = (
            integ[y1 + 1, x1 + 1]
            - integ[y0, x1 + 1]
            - integ[y1 + 1, x0]
            + integ[y0, x0]
        )
        if count:
            free[y, x] = 1
    return free


def pca_axis(xs: np.ndarray, ys: np.ndarray):
    pts = np.stack([xs.astype(np.float64), ys.astype(np.float64)], axis=1)
    mean = pts.mean(axis=0)
    cov = np.cov((pts - mean).T)
    _, vecs = np.linalg.eigh(cov)
    axis = vecs[:, 1]
    axis = axis / (np.linalg.norm(axis) + 1e-9)
    return mean, axis


def dist_to_axis(xs, ys, mean, axis):
    rel = np.stack([xs.astype(np.float64), ys.astype(np.float64)], 1) - mean
    proj = rel @ axis
    perp = rel - proj[:, None] * axis
    return np.hypot(perp[:, 0], perp[:, 1]), proj


def is_fringe(r: int, g: int, b: int) -> bool:
    """Dark bat-outline or leftover tan, not skin, shirts, or gray plastic."""
    if is_wood(r, g, b) or is_highlight(r, g, b) or is_knob(r, g, b):
        return True
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    if s < 0.35:
        return False
    # Thick brown stroke around the barrel.
    if v < 0.55 and 0.02 <= h <= 0.12 and s >= 0.4:
        return True
    # Inner tan the strict wood test missed. Keep this darker than skin
    # and shirt highlights so a cheek or a yellow jersey is not eaten.
    if r > 140 and g > 90 and b < 160 and 28 <= (g - b) <= 78 and 12 <= (r - g) <= 72:
        if 0.05 <= h <= 0.13 and 0.32 <= s <= 0.70 and 0.42 <= v <= 0.84:
            return True
    return False


def eat_fringe(img, out, mean, axis, radius):
    h, w = img.shape[:2]
    cleared = (img[:, :, 3] > 40) & (out[:, :, 3] < 40)
    dist = np.full((h, w), 999, np.int16)
    q = deque()
    ys, xs = np.where(cleared)
    for x, y in zip(xs.tolist(), ys.tolist()):
        dist[y, x] = 0
        q.append((x, y))
    while q:
        x, y = q.popleft()
        d = int(dist[y, x])
        if d >= 11:
            continue
        for nx, ny in neighbors(x, y, w, h):
            if dist[ny, nx] <= d + 1:
                continue
            if out[ny, nx, 3] < 30:
                # Travel through pixels we already removed, not through the
                # empty backdrop, so the search cannot hop onto the cap.
                if img[ny, nx, 3] > 40:
                    dist[ny, nx] = d + 1
                    q.append((nx, ny))
                continue
            r, g, b = (int(v) for v in out[ny, nx, :3])
            if not is_fringe(r, g, b):
                continue
            dist[ny, nx] = d + 1
            q.append((nx, ny))
            out[ny, nx, 3] = 0


def snip_handle_stub(img: np.ndarray, out: np.ndarray, gx: float, gy: float) -> None:
    """Drop the painted knob and grip left between the fists.

    Only small wood/knob blobs at or below the hand pivot. Eyes and hair
    sit above the hands, and the big outline stays because it is huge.
    """
    h, w = out.shape[:2]
    seen = np.zeros((h, w), np.uint8)
    kill = []
    ys, xs = np.where(out[:, :, 3] > 80)
    for x, y in zip(xs.tolist(), ys.tolist()):
        if seen[y, x]:
            continue
        r, g, b = (int(v) for v in out[y, x, :3])
        batish = is_wood(r, g, b) or is_knob(r, g, b) or is_dark(r, g, b)
        if not batish:
            seen[y, x] = 1
            continue
        q = deque([(x, y)])
        seen[y, x] = 1
        pts = []
        woodish = 0
        while q:
            cx, cy = q.popleft()
            pts.append((cx, cy))
            rr, gg, bb = (int(v) for v in out[cy, cx, :3])
            if is_wood(rr, gg, bb) or is_knob(rr, gg, bb):
                woodish += 1
            for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                if nx < 0 or ny < 0 or nx >= w or ny >= h or seen[ny, nx]:
                    continue
                if out[ny, nx, 3] < 80:
                    seen[ny, nx] = 1
                    continue
                r2, g2, b2 = (int(v) for v in out[ny, nx, :3])
                if is_wood(r2, g2, b2) or is_knob(r2, g2, b2) or is_dark(r2, g2, b2):
                    seen[ny, nx] = 1
                    q.append((nx, ny))
                else:
                    seen[ny, nx] = 1
        if not (40 <= len(pts) <= 2400):
            continue
        arr = np.array(pts)
        mx, my = float(arr[:, 0].mean()), float(arr[:, 1].mean())
        if my < gy - 18:
            continue
        if abs(mx - gx) > 70 or abs(my - gy) > 80:
            continue
        if woodish < len(pts) * 0.35 and len(pts) > 900:
            continue
        kill.extend(pts)
    for x, y in kill:
        out[y, x, 3] = 0


def remove_one(path: Path):
    img = np.array(Image.open(path).convert("RGBA"))
    h, w = img.shape[:2]
    sx, sy, body_x, body_y = find_seed(img)
    wood = flood_wood(img, sx, sy)
    free_map = near_transparent(img[:, :, 3], 28)
    free = (wood == 1) & (free_map == 1)
    if free.sum() < 80:
        free = wood == 1
    fys, fxs = np.where(free)
    # Axis from the barrel tip only. A tan shirt can share the wood color;
    # fitting the whole blob bends the axis through the shirt.
    dist_body = np.hypot(fxs - body_x, fys - body_y)
    dist_seed = np.hypot(fxs - sx, fys - sy)
    tip_sel = dist_seed <= max(150.0, np.percentile(dist_seed, 40))
    if tip_sel.sum() < 40:
        tip_sel = dist_body >= np.percentile(dist_body, 60)
    mean, axis = pca_axis(fxs[tip_sel], fys[tip_sel])
    # Orient the axis so +axis points from the barrel tip toward the body.
    d_free, proj_free = dist_to_axis(fxs, fys, mean, axis)
    end_a = mean + axis * proj_free.min()
    end_b = mean + axis * proj_free.max()
    if np.hypot(*(end_a - (body_x, body_y))) < np.hypot(*(end_b - (body_x, body_y))):
        axis = -axis
        end_a, end_b = end_b, end_a
        proj_free = -proj_free
    tip = end_a  # farther from the body
    near = end_b
    radius = float(np.percentile(d_free, 92) + 7.0)
    radius = float(np.clip(radius, 16.0, 30.0))

    keep = np.zeros((h, w), np.uint8)
    ys, xs = np.where(wood == 1)
    d_wood, proj_wood = dist_to_axis(xs, ys, mean, axis)
    # Keep wood that belongs to the bat ribbon, including the bit that
    # overlaps the body, and drop tan shirts that leaked off-axis.
    for x, y, d, p in zip(xs.tolist(), ys.tolist(), d_wood.tolist(), proj_wood.tolist()):
        if d <= radius and p >= proj_free.min() - 8:
            keep[y, x] = 1

    # Grow the handle from the barrel by adjacency so a dark belt or
    # shoe along the same line cannot join the mask across a gap.
    grown = deque()
    gys, gxs = np.where(keep == 1)
    for x, y in zip(gxs.tolist(), gys.tolist()):
        grown.append((x, y, 0))
    while grown:
        x, y, dist = grown.popleft()
        if dist >= 100:
            continue
        for nx, ny in neighbors(x, y, w, h):
            if keep[ny, nx] or img[ny, nx, 3] < 50:
                continue
            rel = np.array([nx - mean[0], ny - mean[1]], dtype=np.float64)
            along = float(rel @ axis)
            perp = float(np.linalg.norm(rel - axis * along))
            if perp > radius + 2 or along < proj_free.min() - 6:
                continue
            r, g, b = (int(v) for v in img[ny, nx, :3])
            if is_dark(r, g, b) or is_knob(r, g, b) or is_wood(r, g, b):
                keep[ny, nx] = 1
                grown.append((nx, ny, dist + 1))

    # Dark outline of the free barrel only. Skip outline pixels that lean on
    # skin or cloth so the silhouette of the kid stays closed.
    outline = []
    kys, kxs = np.where(keep == 1)
    seen = set()
    for x, y in zip(kxs.tolist(), kys.tolist()):
        for nx, ny in neighbors(x, y, w, h):
            if keep[ny, nx] or (nx, ny) in seen or img[ny, nx, 3] < 40:
                continue
            r, g, b = (int(v) for v in img[ny, nx, :3])
            if not is_dark(r, g, b):
                continue
            rel = np.array([nx - mean[0], ny - mean[1]])
            along = float(rel @ axis)
            perp = float(np.linalg.norm(rel - axis * along))
            if perp > radius + 5:
                continue
            body = 0
            trans = 0
            for xx, yy in neighbors(nx, ny, w, h):
                if img[yy, xx, 3] < 30:
                    trans += 1
                elif not keep[yy, xx]:
                    rr, gg, bb = (int(v) for v in img[yy, xx, :3])
                    if not is_dark(rr, gg, bb) and not is_wood(rr, gg, bb):
                        body += 1
            if trans > 0 and body <= 1:
                outline.append((nx, ny))
                seen.add((nx, ny))
    for x, y in outline:
        keep[y, x] = 1

    out = img.copy()
    ys, xs = np.where(keep == 1)
    for x, y in zip(xs.tolist(), ys.tolist()):
        out[y, x, 3] = 0
    # The barrel's painted outline is a thick dark stroke the wood flood
    # never enters, and a grain line can split off a strip of wood. Eat
    # that fringe, but only along the bat axis so the kid's own outline
    # (the same dark brown) stays put.
    eat_fringe(img, out, mean, axis, radius)

    # Put back any original pixel that is not actually bat-colored. The
    # mask can nick an ear, a cheek, or a sleeve; those stay painted.
    cy, cx = np.where((img[:, :, 3] > 40) & (out[:, :, 3] < 40))
    for x, y in zip(cx.tolist(), cy.tolist()):
        r, g, b = (int(v) for v in img[y, x, :3])
        if is_wood(r, g, b) or is_highlight(r, g, b) or is_knob(r, g, b) or is_fringe(r, g, b):
            continue
        out[y, x] = img[y, x]

    # Fill only where the bat crossed the body: body pixels remain on
    # both sides of the axis. The barrel has empty space beside it.
    perp = np.array([-axis[1], axis[0]], dtype=np.float64)
    hole = np.zeros((h, w), np.uint8)
    cy, cx = np.where((img[:, :, 3] > 40) & (out[:, :, 3] < 40))
    for x, y in zip(cx.tolist(), cy.tolist()):
        sides = 0
        for sign in (1.0, -1.0):
            for step in range(3, 32):
                xx = int(round(x + perp[0] * sign * step))
                yy = int(round(y + perp[1] * sign * step))
                if xx < 0 or yy < 0 or xx >= w or yy >= h:
                    break
                if out[yy, xx, 3] >= 40:
                    sides += 1
                    break
                if img[yy, xx, 3] < 40:
                    break
        if sides == 2:
            hole[y, x] = 1
    for _ in range(40):
        hole_y, hole_x = np.where(hole == 1)
        if len(hole_x) == 0:
            break
        fills = []
        for x, y in zip(hole_x.tolist(), hole_y.tolist()):
            skins = []
            for nx, ny in neighbors(x, y, w, h):
                if out[ny, nx, 3] < 40:
                    continue
                r, g, b = (int(v) for v in out[ny, nx, :3])
                if is_fringe(r, g, b) or is_wood(r, g, b):
                    continue
                skins.append(out[ny, nx, :3])
            if skins:
                fills.append((x, y, np.mean(skins, axis=0)))
                hole[y, x] = 0
        if not fills:
            break
        for x, y, col in fills:
            out[y, x, :3] = col.astype(np.uint8)
            out[y, x, 3] = 255

    # Grip pivot: dark pixels nearest the body, else the near end of the wood.
    grip = (keep == 1) & (img[:, :, 0] < 110) & (img[:, :, 3] > 80)
    if grip.sum() >= 12:
        gys, gxs = np.where(grip)
        _, gproj = dist_to_axis(gxs, gys, mean, axis)
        # Hands sit at the body end of the taped grip, not the middle of it.
        sel = gproj >= np.percentile(gproj, 65)
        gx, gy = float(gxs[sel].mean()), float(gys[sel].mean())
    else:
        gx, gy = float(near[0]), float(near[1])
    # Barrel tip: opaque wood pixel farthest from the grip along the axis.
    wood_left = (keep == 1) & (img[:, :, 3] > 80)
    tys, txs = np.where(wood_left)
    if len(txs) == 0:
        tx, ty = float(tip[0]), float(tip[1])
    else:
        rel = np.stack([txs - gx, tys - gy], 1).astype(np.float64)
        along = rel @ axis
        # tip is the end opposite the body, which is the smaller projection
        # after we oriented `axis` toward the body. Use the min.
        j = int(along.argmin())
        tx, ty = float(txs[j]), float(tys[j])

    snip_handle_stub(img, out, gx, gy)
    # Pearl's barrel hides behind her cap, so the traced grip lands on her
    # hair. The fists and knob are over on the right; pin the bat there.
    if "pearl" in path.name:
        gx, gy = 0.78 * w, 0.485 * h
        knob_x, knob_y = 0.90 * w, 0.515 * h
        ys, xs = np.where(out[:, :, 3] > 40)
        for x, y in zip(xs.tolist(), ys.tolist()):
            if (x - knob_x) ** 2 + (y - knob_y) ** 2 > 34 ** 2:
                continue
            r, g, b = (int(v) for v in out[y, x, :3])
            if is_dark(r, g, b) or (is_knob(r, g, b) and x > w * 0.84):
                out[y, x, 3] = 0
        snip_handle_stub(img, out, gx, gy)
    dx = tx - gx
    dy = ty - gy
    # View angle of the cocked bat, y-up, 0 = barrel pointing right.
    angle = float(np.arctan2(-dy, dx))
    meta = {
        "u": round(gx / w, 4),
        "v": round(gy / h, 4),
        "tip_u": round(tx / w, 4),
        "tip_v": round(ty / h, 4),
        "length_px": round(float(np.hypot(dx, dy)), 1),
        "angle": round(angle, 4),
        "img_w": int(w),
        "img_h": int(h),
        "cleared": int(((img[:, :, 3] > 40) & (out[:, :, 3] < 40)).sum()),
    }
    return out, meta


def bat_geometry(path: Path):
    img = np.array(Image.open(path).convert("RGBA"))
    h, w = img.shape[:2]
    alpha = img[:, :, 3] > 40
    ys, xs = np.where(alpha)
    # Knob is the opaque pixel farthest toward the lower right; the barrel
    # tip is the opaque pixel farthest toward the upper left.
    score_knob = xs.astype(np.float64) + ys.astype(np.float64)
    score_tip = -(xs.astype(np.float64) + ys.astype(np.float64))
    k = int(score_knob.argmax())
    t = int(score_tip.argmax())
    # Step inward so the pivot sits on the taped grip, not the round knob.
    kx, ky = float(xs[k]), float(ys[k])
    tx, ty = float(xs[t]), float(ys[t])
    direction = np.array([tx - kx, ty - ky])
    direction /= np.linalg.norm(direction) + 1e-9
    grip = np.array([kx, ky]) + direction * 42.0
    return {
        "w": w,
        "h": h,
        "grip_u": round(float(grip[0]) / w, 4),
        "grip_v": round(float(grip[1]) / h, 4),
        "tip_u": round(tx / w, 4),
        "tip_v": round(ty / h, 4),
        "length_px": round(float(np.hypot(tx - grip[0], ty - grip[1])), 1),
    }


def main():
    import sys
    poses_path = ART / "bat_poses.json"
    print("Painted batless stances are the source of truth:")
    for kid in IDS:
        png = ART / f"char_{kid}_batless.png"
        print(f"  {png.name:28} {'ok' if png.is_file() else 'MISSING'}")
    print("This script does not overwrite them.")
    if "--measure-bat" not in sys.argv:
        print("Pose pivots stay in", poses_path)
        return
    poses = json.loads(poses_path.read_text())
    poses["bat"] = bat_geometry(ART / "bat.png")
    poses["painted_batless"] = True
    poses_path.write_text(json.dumps(poses, indent=2) + "\n")
    print("refreshed bat.png grip in", poses_path)


if __name__ == "__main__":
    main()
