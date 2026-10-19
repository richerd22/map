#!/usr/bin/env python3
"""Build map.cold.fyi from data/sites.json. No dependencies.

    python3 build.py

data/sites.json holds ONLY approved, public, live sites. New hostnames are proposed in the
Daily Digest from the Notion Domain Registry and added here after Richard approves them.
"""
import html, json, math, pathlib, random, datetime

ROOT = pathlib.Path(__file__).resolve().parent
e = lambda s: html.escape(str(s), quote=True)

W, H = 1000, 640
# constellation centers, as fractions of the field (one per group, in data order)
ANCHORS = [(0.19, 0.30), (0.50, 0.18), (0.81, 0.24), (0.79, 0.70), (0.21, 0.74), (0.50, 0.80), (0.50, 0.47)]


def layout(data):
    pts = []
    for gi, g in enumerate(data["groups"]):
        members = [s for s in data["sites"] if s["group"] == g["id"]]
        ax, ay = ANCHORS[gi % len(ANCHORS)]
        cx, cy = ax * W, ay * H
        rnd = random.Random(g["id"])  # stable positions per group
        golden = math.pi * (3 - math.sqrt(5))
        for i, s in enumerate(members):
            r = 16 + 21 * math.sqrt(i + 0.6)
            a = i * golden + rnd.uniform(-0.25, 0.25)
            x = cx + r * math.cos(a) * 1.25
            y = cy + r * math.sin(a)
            pts.append(dict(s, x=round(x, 1), y=round(y, 1), gi=gi))
    return pts


def field_svg(data, pts):
    out = [f'<svg class="field" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ftitle">',
           '<title id="ftitle">Every site, drawn as a dot and grouped by kind</title>']
    # faint background stars
    rnd = random.Random(7)
    for _ in range(140):
        out.append(f'<circle class="star" cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H):.0f}" r="{rnd.choice([0.6, 0.8, 1.0])}"/>')
    # constellation lines: each dot to its nearest earlier sibling
    for p in pts:
        sib = [q for q in pts if q["gi"] == p["gi"] and q is not p and pts.index(q) < pts.index(p)]
        if sib:
            q = min(sib, key=lambda q: (q["x"] - p["x"]) ** 2 + (q["y"] - p["y"]) ** 2)
            out.append(f'<line class="link g{p["gi"]}" x1="{q["x"]}" y1="{q["y"]}" x2="{p["x"]}" y2="{p["y"]}"/>')
    # group labels
    for gi, g in enumerate(data["groups"]):
        ax, ay = ANCHORS[gi % len(ANCHORS)]
        ys = [p["y"] for p in pts if p["gi"] == gi]
        ly = (min(ys) - 22) if ys else ay * H
        out.append(f'<text class="glabel" x="{ax * W:.0f}" y="{ly:.0f}" text-anchor="middle">{e(g["name"].lower())}</text>')
    # the dots
    for p in pts:
        out.append(f'<a class="dot g{p["gi"]}" href="https://{e(p["host"])}" data-name="{e(p["name"])}" data-host="{e(p["host"])}" data-blurb="{e(p["blurb"])}">'
                   f'<circle class="halo" cx="{p["x"]}" cy="{p["y"]}" r="16"/><circle class="core" cx="{p["x"]}" cy="{p["y"]}" r="3.2"/>'
                   f'<title>{e(p["name"])} - {e(p["host"])}</title></a>')
    out.append('</svg>')
    return "\n".join(out)


def index_html(data, pts):
    groups = []
    for gi, g in enumerate(data["groups"]):
        rows = "".join(
            f'<li class="site" data-q="{e((s["name"] + " " + s["host"] + " " + s["blurb"]).lower())}">'
            f'<a href="https://{e(s["host"])}"><span class="n">{e(s["name"])}</span><span class="h">{e(s["host"])}</span></a>'
            f'<span class="b">{e(s["blurb"])}</span></li>'
            for s in data["sites"] if s["group"] == g["id"])
        groups.append(f'<section class="grp" id="{e(g["id"])}"><h2><span class="sw g{gi}"></span>{e(g["name"])}</h2>'
                      f'<p class="gnote">{e(g["note"])}</p><ul>{rows}</ul></section>')
    roots = sorted({".".join(s["host"].split(".")[-2:]) for s in data["sites"]})
    n = len(data["sites"])
    updated = datetime.date.today().strftime("%b %-d, %Y")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>map.cold.fyi - every site is a dot</title>
<meta name="description" content="Every site in the cold.fyi and Third Polar Arch universe, on one page. {n} sites across {len(roots)} domains.">
<link rel="canonical" href="https://map.cold.fyi/">
<meta property="og:title" content="map.cold.fyi - every site is a dot">
<meta property="og:description" content="{n} sites across the cold.fyi and Third Polar Arch universe, on one page.">
<meta name="theme-color" content="#0a0a10">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet">
<link rel="stylesheet" href="map.css">
</head>
<body class="grain">
<header class="top">
  <a class="mark" href="https://cold.fyi">cold.fyi</a><span class="slash">/</span><span class="here">map</span>
</header>
<main>
  <section class="hero">
    <h1>every site is a dot.</h1>
    <p class="count">{n} sites. {len(roots)} domains. one universe. <span class="mut">updated {e(updated)}</span></p>
    <div class="fieldwrap">
      {field_svg(data, pts)}
      <div class="readout" id="readout" aria-live="polite"><span class="mut">hover a dot. tap twice to visit.</span></div>
    </div>
  </section>
  <section class="list" aria-label="All sites">
    <label class="find"><span>find</span><input id="q" type="search" placeholder="type to filter" autocomplete="off"></label>
    {''.join(groups)}
    <p class="none" id="none" hidden>nothing matches.</p>
  </section>
</main>
<footer class="foot">
  <p>made with &lt;3 in boston by <a href="https://thirdpolararch.com">Third Polar Arch</a></p>
  <p><a href="https://thirdpolararch.com/terms">terms</a> <a href="https://thirdpolararch.com/privacy">privacy</a> <a href="sites.json">sites.json</a></p>
</footer>
<script>
(function(){{
  var out=document.getElementById('readout'), armed=null;
  function show(a){{out.innerHTML='<b>'+a.dataset.name+'</b> <span class="h">'+a.dataset.host+'</span><br><span class="mut">'+a.dataset.blurb+'</span>';}}
  document.querySelectorAll('.dot').forEach(function(a){{
    a.addEventListener('mouseenter',function(){{show(a)}});
    a.addEventListener('focus',function(){{show(a)}});
    a.addEventListener('click',function(ev){{
      if(window.matchMedia('(hover: none)').matches && armed!==a){{ev.preventDefault();armed=a;show(a);}}
    }});
  }});
  var q=document.getElementById('q'), none=document.getElementById('none');
  q.addEventListener('input',function(){{
    var t=q.value.trim().toLowerCase(), any=false;
    document.querySelectorAll('.grp').forEach(function(g){{
      var vis=0; g.querySelectorAll('.site').forEach(function(s){{var m=!t||s.dataset.q.indexOf(t)>-1; s.hidden=!m; if(m)vis++;}});
      g.hidden=!vis; if(vis)any=true;
    }});
    none.hidden=any;
  }});
  document.addEventListener('keydown',function(ev){{if(ev.key==='/'&&document.activeElement!==q){{ev.preventDefault();q.focus();}}}});
}})();
</script>
</body>
</html>
"""


def main():
    data = json.loads((ROOT / "data/sites.json").read_text())
    pts = layout(data)
    (ROOT / "index.html").write_text(index_html(data, pts))
    feed = [{"host": s["host"], "url": f"https://{s['host']}", "name": s["name"], "blurb": s["blurb"],
             "group": s["group"]} for s in data["sites"]]
    (ROOT / "sites.json").write_text(json.dumps(feed, indent=1, ensure_ascii=False))
    today = datetime.date.today().isoformat()
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      f'<url><loc>https://map.cold.fyi/</loc><lastmod>{today}</lastmod></url></urlset>\n')
    print(f"built {len(data['sites'])} sites")


if __name__ == "__main__":
    main()
