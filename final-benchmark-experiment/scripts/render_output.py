#!/usr/bin/env python3
"""
Render final benchmark PLY exports as BEV and side-view preview images.
Usage: python3 render_output.py <export_dir>
"""
import sys, os, struct, math
import numpy as np
import cv2

def load_ply(path):
    pts, colors = [], []
    with open(path, 'rb') as f:
        header = b""
        while True:
            line = f.readline()
            header += line
            if line.strip() == b"end_header":
                break
        hstr = header.decode(errors='ignore')
        lines = hstr.split('\n')
        n = int([l for l in lines if l.startswith('element vertex')][0].split()[-1])
        props = []
        in_vertex = False
        for line in lines:
            if line.startswith('element vertex'):
                in_vertex = True
                continue
            if line.startswith('element ') and in_vertex:
                break
            if in_vertex and line.startswith('property'):
                props.append(line.strip())
        bpp = sum(4 if ('float' in p or 'int' in p) else 1 for p in props)
        has_rgb = any(' red' in p for p in props) and any(' green' in p for p in props) and any(' blue' in p for p in props)
        raw = f.read(n * bpp)

    print(f"  {n:,} nokta, {bpp} byte/nokta, renk={'var' if has_rgb else 'yok'}")
    xs, ys, zs, rs, gs, bs = [], [], [], [], [], []
    for i in range(0, n, 1):
        off = i * bpp
        if off + 12 > len(raw): break
        x, y, z = struct.unpack_from('<fff', raw, off)
        xs.append(x); ys.append(y); zs.append(z)
        if has_rgb and off + 15 <= len(raw):
            try:
                r, g, b = struct.unpack_from('<BBB', raw, off + 12)
                rs.append(r); gs.append(g); bs.append(b)
            except:
                rs.append(180); gs.append(180); bs.append(180)
        else:
            rs.append(180); gs.append(180); bs.append(180)

    xs = np.array(xs); ys = np.array(ys); zs = np.array(zs)
    rs = np.array(rs); gs = np.array(gs); bs = np.array(bs)
    mask = np.isfinite(xs) & np.isfinite(ys) & np.isfinite(zs)
    return xs[mask], ys[mask], zs[mask], rs[mask], gs[mask], bs[mask]


def render_bev(xs, ys, zs, rs, gs, bs, out_path, res=0.04, size=900):
    """Kuş bakışı (BEV) — Z yüksekliğine göre renklendir"""
    # Merkeze al
    cx_w = (xs.max() + xs.min()) / 2
    cy_w = (ys.max() + ys.min()) / 2
    span = max(xs.max()-xs.min(), ys.max()-ys.min()) * 0.55
    span = max(span, 3.0)
    res  = span * 2 / size

    img = np.full((size, size, 3), 15, dtype=np.uint8)  # koyu arka plan

    pxs = ((xs - cx_w) / res + size//2).astype(int)
    pys = ((ys - cy_w) / res + size//2).astype(int)
    zn  = ((zs - zs.min()) / (zs.max() - zs.min() + 1e-6) * 255).astype(np.uint8)

    mask = (pxs >= 0) & (pxs < size) & (pys >= 0) & (pys < size)
    for i in np.where(mask)[0]:
        c = cv2.applyColorMap(np.array([[zn[i]]], dtype=np.uint8), cv2.COLORMAP_TURBO)[0][0]
        img[pys[i], pxs[i]] = c

    # Başlangıç noktası
    sx = int((0 - cx_w) / res + size//2)
    sy = int((0 - cy_w) / res + size//2)
    if 0 <= sx < size and 0 <= sy < size:
        cv2.circle(img, (sx, sy), 8, (0, 255, 0), -1)
        cv2.circle(img, (sx, sy), 10, (255, 255, 255), 1)
        cv2.putText(img, "Start", (sx+12, sy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

    # Ölçek çubuğu
    bar_m = 2.0
    bar_px = int(bar_m / res)
    bx, by = 40, size - 40
    cv2.line(img, (bx, by), (bx + bar_px, by), (255,255,255), 2)
    cv2.putText(img, f"{bar_m:.0f}m", (bx, by-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # Bilgi
    cv2.putText(img, f"BEV | nokta:{len(xs):,}", (10, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1)
    cv2.putText(img, f"X:[{xs.min():.1f},{xs.max():.1f}] Y:[{ys.min():.1f},{ys.max():.1f}]",
                (10, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150,150,150), 1)

    cv2.imwrite(out_path, img)
    print(f"  BEV kaydedildi: {out_path}")


def render_side(xs, ys, zs, out_path, res=0.04, size=900):
    """Yan görünüm (X-Z düzlemi)"""
    cx_w = (xs.max() + xs.min()) / 2
    span = max(xs.max()-xs.min(), zs.max()-zs.min()) * 0.55
    span = max(span, 2.0)
    res  = span * 2 / size

    img = np.full((size, size, 3), 15, dtype=np.uint8)
    pxs = ((xs - cx_w) / res + size//2).astype(int)
    pzs = (size//2 - (zs - (zs.max()+zs.min())/2) / res).astype(int)
    zn  = ((zs - zs.min()) / (zs.max() - zs.min() + 1e-6) * 255).astype(np.uint8)

    mask = (pxs >= 0) & (pxs < size) & (pzs >= 0) & (pzs < size)
    for i in np.where(mask)[0]:
        c = cv2.applyColorMap(np.array([[zn[i]]], dtype=np.uint8), cv2.COLORMAP_TURBO)[0][0]
        img[pzs[i], pxs[i]] = c

    cv2.putText(img, "YAN GORÜNUM (X-Z)", (10, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1)
    cv2.imwrite(out_path, img)
    print(f"  Yan görünüm kaydedildi: {out_path}")


def main():
    if len(sys.argv) < 2:
        # Argüman verilmediyse en son export klasörünü bul
        base = os.path.expanduser("~/Desktop/Project-Final/final-benchmark-experiment/outputs")
        dirs = sorted([d for d in os.listdir(base) if d.endswith("_export")])
        if not dirs:
            print("HATA: export klasörü bulunamadı.")
            sys.exit(1)
        export_dir = os.path.join(base, dirs[-1])
    else:
        export_dir = sys.argv[1]

    ply = os.path.join(export_dir, "rtabmap_cloud.ply")
    if not os.path.exists(ply):
        print(f"HATA: PLY bulunamadı: {ply}")
        sys.exit(1)

    print(f"PLY yükleniyor: {ply}")
    xs, ys, zs, rs, gs, bs = load_ply(ply)
    print(f"  X:[{xs.min():.2f},{xs.max():.2f}]  Y:[{ys.min():.2f},{ys.max():.2f}]  Z:[{zs.min():.2f},{zs.max():.2f}]")

    print("BEV render ediliyor...")
    render_bev(xs, ys, zs, rs, gs, bs,
               os.path.join(export_dir, "render_bev.png"))

    print("Yan görünüm render ediliyor...")
    render_side(xs, ys, zs,
                os.path.join(export_dir, "render_side.png"))

    print("Tamamlandi.")


if __name__ == "__main__":
    main()
