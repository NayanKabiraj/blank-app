"""Step 4: build the HyperFrames projects from script.json + measured audio timings.
Usage: python build.py   -> composition/<lang>/ (1920x1080) and composition/<lang>-short/ (1080x1920)
One sub-composition per scene. The sun is carried across every scene change."""
import json, math, random, shutil
from pathlib import Path

HERE = Path(__file__).parent
STUDIO = HERE.parent.parent
script = json.loads((HERE / "script.json").read_text(encoding="utf-8"))
TOKENS = (STUDIO / "brand" / "tokens.css").read_text(encoding="utf-8")
SHORT_SCENES = ["s1", "s4", "s5", "s7"]          # hook + the two strongest idea scenes + payoff

LABELS = {
 "en": {"day": "Day sky", "sunset": "Sunset", "long": "long", "short": "short", "air": "air molecules",
        "four": "4×", "bvr": "blue vs red", "painted": "painted", "glowing": "glowing",
        "spath": "short path", "lpath": "long path", "sin": "scattered", "left": "left over", "follow": "Follow"},
 "hi": {"day": "दिन का आसमान", "sunset": "सूर्यास्त", "long": "लंबी", "short": "छोटी", "air": "हवा के अणु",
        "four": "4×", "bvr": "नीला बनाम लाल", "painted": "रंगा हुआ", "glowing": "चमकता हुआ",
        "spath": "छोटा रास्ता", "lpath": "लंबा रास्ता", "sin": "बिखरा हुआ", "left": "बचा हुआ", "follow": "फ़ॉलो करें"},
}

def wave(x0, x1, y, wl, amp):
    pts = [(x, y - amp * math.sin((x - x0) / wl * 2 * math.pi)) for x in range(x0, x1 + 1, 4)]
    return "M " + " L ".join(f"{x} {yy:.1f}" for x, yy in pts)

def dots(seed, n, fn):
    r, out = random.Random(seed), []
    while len(out) < n:
        p = fn(r)
        if p and all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 70 ** 2 for q in out):
            out.append(p)
    return out

SUN = '<g id="@sun"><g id="@rays">' + "".join(
    f'<line x1="{math.cos(a) * 92:.1f}" y1="{math.sin(a) * 92:.1f}" x2="{math.cos(a) * 122:.1f}" y2="{math.sin(a) * 122:.1f}" class="s-sun"/>'
    for a in [i * math.pi / 4 for i in range(8)]) + '</g><circle r="70" class="f-sun"/><circle id="@warm" r="70" class="f-a2"/></g>'
PERSON = '<g id="@per"><circle cx="600" cy="722" r="24" class="f-text"/><path d="M 572 800 Q 572 752 600 752 Q 628 752 628 800 Z" class="f-text"/></g>'
GROUND = '<rect x="0" y="800" width="1200" height="100" class="f-bg2"/><line x1="0" y1="800" x2="1200" y2="800" class="s-text"/>'
DOME = "M 40 820 A 560 560 0 0 1 1160 820 Z"

# name -> (sun [x, y, scale, warm] at rest, svg body, js)
SC = {}
st = dots(1, 26, lambda r: (r.randint(40, 1160), r.randint(30, 760)))
SC["s1"] = ([600, 400, 1.2, 0], f'''
 <g id="@stars">{"".join(f'<circle id="@st{i}" cx="{x}" cy="{y}" r="{5 + i % 3 * 2}" class="f-text"/>' for i, (x, y) in enumerate(st))}</g>
 <path id="@sky" d="{DOME}" class="f-accent"/>
 <g id="@gp">{GROUND}{PERSON}</g>
 <text id="@q" x="900" y="420" class="t-big">?</text>''', '''
 F(q("gp"), 0.15);
 for (let i = 0; i < 26; i++) P(q("st" + i), C[1] - 0.1 + i * 0.025, 0.3);
 tl.fromTo(q("sky"), {opacity: 0, scaleY: 0.2, transformOrigin: "50% 100%"}, {opacity: 0.85, scaleY: 1, duration: 0.7, ease: "power3.out"}, C[2] + 0.35);
 tl.to(q("stars"), {opacity: 0.15, duration: 0.5, ease: "power2.out"}, C[2] + 0.35);
 P(q("q"), C[2] + 0.75, 0.5);''')

SC["s2"] = ([170, 150, 1, 0], '''
 <line id="@beam" x1="225" y1="200" x2="560" y2="400" class="s-sun w14" pathLength="1"/>
 <g id="@mag"><circle cx="620" cy="440" r="80" class="s-text nofill"/><line x1="678" y1="496" x2="740" y2="560" class="s-text"/></g>
 <line id="@l1" x1="570" y1="500" x2="380" y2="600" class="s-accent" pathLength="1"/>
 <line id="@l2" x1="670" y1="500" x2="840" y2="600" class="s-a2" pathLength="1"/>
 <g id="@d1"><circle cx="320" cy="690" r="105" class="f-accent"/></g>
 <g id="@d2"><circle cx="890" cy="690" r="105" class="f-a2"/></g>
 <text id="@t1" x="320" y="872" class="t-lbl mid">{{day}}</text>
 <text id="@t2" x="890" y="872" class="t-lbl mid">{{sunset}}</text>''', '''
 Dr(q("beam"), C[0] + 0.5, 0.7); P(q("mag"), C[0] + 1.1);
 Dr(q("l1"), C[0] + 2.0, 0.4); P(q("d1"), C[0] + 2.3); F(q("t1"), C[0] + 2.5);
 const m = C[1] + (E[1] - C[1]) * 0.55;
 Dr(q("l2"), m, 0.4); P(q("d2"), m + 0.3); F(q("t2"), m + 0.5);''')

fan = "".join(f'<line id="@f{i}" x1="545" y1="450" x2="1130" y2="{240 + i * 84}" class="s-{c} w18" pathLength="1"/>'
              for i, c in enumerate(["red", "orange", "yellow", "green", "blue", "violet"]))
SC["s3"] = ([130, 450, 1, 0], f'''
 <line id="@beam" x1="200" y1="450" x2="415" y2="450" class="s-sun w18" pathLength="1"/>
 <g id="@fan">{fan}</g>
 <path id="@prism" d="M 480 320 L 620 580 L 340 580 Z" class="s-text f-bg2"/>
 <path id="@w0" d="{wave(660, 1140, 450, 190, 46)}" class="s-sun nofill" pathLength="1"/>
 <path id="@wr" d="{wave(660, 1140, 250, 240, 50)}" class="s-red nofill" pathLength="1"/>
 <path id="@wb" d="{wave(660, 1140, 650, 80, 50)}" class="s-blue nofill" pathLength="1"/>
 <text id="@tr" x="660" y="160" class="t-lbl c-red">{{{{long}}}}</text>
 <text id="@tb" x="660" y="790" class="t-lbl c-blue">{{{{short}}}}</text>''', '''
 P(q("prism"), 0.5); Dr(q("beam"), C[0] + 0.3, 0.6);
 const m = C[0] + (E[0] - C[0]) * 0.5;
 for (let i = 0; i < 6; i++) Dr(q("f" + i), m + i * 0.09, 0.6);
 X(q("fan"), C[1] - 0.2); Dr(q("w0"), C[1] + 0.1, 0.9);
 X(q("w0"), C[2] - 0.25);
 Dr(q("wr"), C[2] + 0.05, 1.1); F(q("tr"), C[2] + 0.5);
 Dr(q("wb"), C[3] + 0.05, 1.1); F(q("tb"), C[3] + 0.5);''')

mol4 = dots(4, 15, lambda r: (lambda x, y: (x, y) if not (x > 820 and y < 470) and (x - 580) ** 2 + (y - 500) ** 2 > 190 ** 2 else None)(r.randint(300, 1120), r.randint(300, 720)))
rad = "".join(f'<line id="@b{i}" x1="{580 + math.cos(a) * 30:.0f}" y1="{500 + math.sin(a) * 30:.0f}" x2="{580 + math.cos(a) * 175:.0f}" y2="{500 + math.sin(a) * 175:.0f}" class="s-accent w10" pathLength="1"/>'
              for i, a in enumerate([j * 2 * math.pi / 9 + 0.2 for j in range(9)]))
SC["s4"] = ([150, 130, 1, 0], f'''
 <line id="@beam" x1="205" y1="178" x2="560" y2="483" class="s-sun w14" pathLength="1"/>
 <line id="@red" x1="600" y1="517" x2="930" y2="800" class="s-red w10" pathLength="1"/>
 <g id="@rad">{rad}</g>
 {"".join(f'<circle id="@m{i}" cx="{x}" cy="{y}" r="14" class="f-text"/>' for i, (x, y) in enumerate(mol4))}
 <circle id="@hit" cx="580" cy="500" r="20" class="f-text"/>
 <text id="@ta" x="300" y="872" class="t-lbl">{{{{air}}}}</text>
 <text id="@four" x="1000" y="300" class="t-huge mid c-accent">{{{{four}}}}</text>
 <text id="@tf" x="1000" y="380" class="t-lbl mid">{{{{bvr}}}}</text>''', '''
 const h = C[0] + (E[0] - C[0]) * 0.55;
 Dr(q("beam"), h - 0.6, 0.6); P(q("hit"), h, 0.35);
 for (let i = 0; i < 15; i++) { P(q("m" + i), C[1] + 0.1 + i * 0.07, 0.3);
   tl.fromTo(q("m" + i), {y: 0}, {y: i % 2 ? 9 : -9, duration: 1.3, yoyo: true, repeat: Math.max(1, Math.floor((D - C[1] - 2) / 1.3)), ease: "sine.inOut"}, C[1] + 1 + i * 0.07); }
 F(q("ta"), C[1] + 0.5);
 const b = C[2] + (E[2] - C[2]) * 0.3, r = C[2] + (E[2] - C[2]) * 0.78;
 for (let i = 0; i < 9; i++) Dr(q("b" + i), b + i * 0.06, 0.45);
 tl.fromTo(q("hit"), {scale: 1}, {scale: 1.5, duration: 0.2, yoyo: true, repeat: 1, ease: "power2.out", transformOrigin: "50% 50%"}, b);
 Dr(q("red"), r, 0.8);
 tl.fromTo(q("four"), {opacity: 0, scale: 1.8, transformOrigin: "50% 50%"}, {opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2)"}, C[3] + 0.25);
 F(q("tf"), C[3]);''')

def in_dome(r):
    a, d = r.uniform(math.pi * 1.06, math.pi * 1.94), r.uniform(200, 520)
    x, y = 600 + math.cos(a) * d, 820 + math.sin(a) * d
    return (round(x), round(y)) if abs(x - 600) > 60 or y < 600 else None
mol5 = dots(5, 20, in_dome)
pick = [i for i, (x, y) in enumerate(mol5) if y < 700][:7]
SC["s5"] = ([1040, 130, 0.8, 0], f'''
 <path id="@sky" d="{DOME}" class="f-accent"/>
 <path id="@glow" d="{DOME}" class="f-accent"/>
 {"".join(f'<line id="@c{k}" x1="{mol5[i][0]}" y1="{mol5[i][1]}" x2="600" y2="705" class="s-accent" pathLength="1"/>' for k, i in enumerate(pick))}
 {"".join(f'<g id="@m{i}"><circle cx="{x}" cy="{y}" r="14" class="f-text"/><circle id="@mb{i}" cx="{x}" cy="{y}" r="17" class="f-accent"/></g>' for i, (x, y) in enumerate(mol5))}
 <g id="@gp">{GROUND}{PERSON}</g>
 <g id="@pw"><text x="600" y="250" class="t-word mid">{{{{painted}}}}</text><line id="@strike" x1="330" y1="232" x2="870" y2="232" class="s-a2 w14" pathLength="1"/></g>
 <text id="@gw" x="600" y="250" class="t-word mid c-accent">{{{{glowing}}}}</text>''', f'''
 F(q("gp"), 0.1); tl.fromTo(q("sky"), {{opacity: 0}}, {{opacity: 0.12, duration: 0.4, ease: "power2.out"}}, 0.2);
 for (let i = 0; i < 20; i++) {{ P(q("m" + i), 0.3 + i * 0.04, 0.3);
   tl.fromTo(q("mb" + i), {{opacity: 0}}, {{opacity: 1, duration: 0.35, ease: "power2.out"}}, C[0] + 0.5 + i * 0.05); }}
 tl.fromTo(q("glow"), {{opacity: 0}}, {{opacity: 0.3, duration: 1, ease: "power2.out"}}, C[0] + 0.6);
 const c = C[1] + (E[1] - C[1]) * 0.35;
 for (let k = 0; k < {len(pick)}; k++) Dr(q("c" + k), c + k * 0.14, 0.5);
 P(q("pw"), C[2] + (E[2] - C[2]) * 0.45, 0.35); Dr(q("strike"), C[2] + (E[2] - C[2]) * 0.8, 0.3);
 X(q("pw"), C[3] - 0.2);
 P(q("gw"), C[3] + (E[3] - C[3]) * 0.35, 0.45);
 tl.to(q("glow"), {{opacity: 0.75, duration: 0.6, ease: "power2.out"}}, C[3] + (E[3] - C[3]) * 0.35);''')

ticks = "".join(f'<line id="@k{i}" x1="{880 - i * 34}" y1="656" x2="{880 - i * 34 - 50}" y2="{656 + (-1) ** i * 86}" class="s-accent" pathLength="1"/>' for i in range(7))
SC["s6"] = ([600, 110, 0.8, 0], f'''
 <ellipse id="@hz" cx="980" cy="700" rx="430" ry="210" class="f-a2"/>
 <circle cx="600" cy="1500" r="900" class="f-accent air"/>
 <line id="@nb" x1="600" y1="178" x2="600" y2="660" class="s-sun w10" pathLength="1"/>
 <line id="@ns" x1="600" y1="600" x2="600" y2="690" class="s-accent w18" pathLength="1"/>
 <text id="@tn" x="640" y="560" class="t-lbl">{{{{spath}}}}</text>
 <line id="@sb" x1="1030" y1="652" x2="640" y2="660" class="s-sun w10" pathLength="1"/>
 <line id="@ls" x1="910" y1="654" x2="640" y2="660" class="s-accent w18" pathLength="1"/>
 <text id="@tl" x="775" y="560" class="t-lbl mid">{{{{lpath}}}}</text>
 <g id="@ticks">{ticks}</g>
 <line id="@ob" x1="800" y1="657" x2="640" y2="660" class="s-a2 w18" pathLength="1"/>
 <circle cx="600" cy="1500" r="760" class="f-bg2 s-text"/>
 <g id="@per2"><circle cx="600" cy="676" r="22" class="f-text"/><path d="M 574 742 Q 574 700 600 700 Q 626 700 626 742 Z" class="f-text"/></g>''', '''
 tl.set(q("hz"), {opacity: 0}, 0);
 F(q("per2"), 0.1); Dr(q("nb"), 0.4, 0.5); Dr(q("ns"), 0.9, 0.3); F(q("tn"), 1.0);
 const mv = Math.max(1.6, C[0] + 0.4);
 X(q("nb"), mv - 0.1); X(q("ns"), mv - 0.1); X(q("tn"), mv - 0.1);
 tl.to(q("sun"), {x: 1100, y: 650, duration: 1.4, ease: "power2.inOut"}, mv);
 const lp = Math.max(mv + 1.4, C[0] + (E[0] - C[0]) * 0.6);
 Dr(q("sb"), lp, 0.5); Dr(q("ls"), lp + 0.4, 0.5); F(q("tl"), lp + 0.6);
 for (let i = 0; i < 7; i++) Dr(q("k" + i), C[1] + 0.5 + i * 0.16, 0.35);
 Dr(q("ob"), C[1] + (E[1] - C[1]) * 0.75, 0.5);
 tl.to(q("warm"), {opacity: 1, duration: 0.6, ease: "power2.out"}, C[2] + 0.3);
 tl.to(q("hz"), {opacity: 0.4, duration: 0.8, ease: "power2.out"}, C[2] + 0.3);''')
SC["s6"][0].extend([1100, 650, 1])   # where the sun ends: x, y, warm

SC["s7"] = ([600, 120, 0.8, 0], '''
 <path id="@arc" d="M 330 290 Q 600 170 870 290" class="s-text nofill" pathLength="1"/>
 <g id="@d1"><circle cx="330" cy="480" r="180" class="f-accent"/></g>
 <g id="@d2"><circle cx="870" cy="480" r="180" class="f-a2"/></g>
 <text id="@t1" x="330" y="740" class="t-lbl mid">{{sin}}</text>
 <text id="@t2" x="870" y="740" class="t-lbl mid">{{left}}</text>
 <g id="@cta"><rect x="400" y="790" width="400" height="96" rx="48" class="f-text"/><text x="600" y="856" class="t-cta mid">{{follow}}</text></g>''', '''
 P(q("d1"), C[0] + (E[0] - C[0]) * 0.25); F(q("t1"), C[0] + (E[0] - C[0]) * 0.6);
 P(q("d2"), C[1] + 0.25); Dr(q("arc"), C[1] + (E[1] - C[1]) * 0.45, 0.6); F(q("t2"), C[1] + (E[1] - C[1]) * 0.7);
 P(q("cta"), C[2] + 0.2, 0.45);''')

CSS = '''
 #root { position: absolute; inset: 0; font-family: var(--font-display); color: var(--text); }
 .hl { position: absolute; font-size: var(--headline); font-weight: 700; line-height: 1.12; letter-spacing: -0.01em; }
 .hl span { display: inline-block; white-space: pre; }
 .bar { position: absolute; height: 10px; width: 160px; background: var(--accent); border-radius: 5px; }
 .stage { position: absolute; }
 .stage svg { width: 100%; height: 100%; overflow: visible; }
 .f-text { fill: var(--text); } .f-accent { fill: var(--accent); } .f-a2 { fill: var(--accent-2); }
 .f-sun { fill: var(--sun); } .f-bg2 { fill: var(--bg-2); } .nofill { fill: none; } .air { opacity: 0.16; }
 [class*="s-"] { stroke-width: var(--stroke); stroke-linecap: round; stroke-linejoin: round; }
 .s-text { stroke: var(--text); } .s-accent { stroke: var(--accent); } .s-a2 { stroke: var(--accent-2); } .s-sun { stroke: var(--sun); }
 .s-red { stroke: var(--spec-red); } .s-orange { stroke: var(--spec-orange); } .s-yellow { stroke: var(--spec-yellow); }
 .s-green { stroke: var(--spec-green); } .s-blue { stroke: var(--spec-blue); } .s-violet { stroke: var(--spec-violet); }
 .w10 { stroke-width: 10px; } .w14 { stroke-width: 14px; } .w18 { stroke-width: 18px; }
 [pathLength] { stroke-dasharray: 1; }
 text { font-family: var(--font-body); font-weight: 600; fill: var(--text); }
 .t-lbl { font-size: 52px; } .t-big { font-size: 300px; font-weight: 700; } .t-huge { font-size: 210px; font-weight: 700; }
 .t-word { font-size: 120px; font-weight: 700; } .t-cta { font-size: 56px; font-weight: 700; fill: var(--bg); }
 .mid { text-anchor: middle; } .c-accent { fill: var(--accent); } .c-red { fill: var(--spec-red); } .c-blue { fill: var(--spec-blue); }
'''
LAYOUT = {
 "wide": dict(W=1920, H=1080, hl="left:120px; top:300px; width:640px;", bar="left:120px; top:250px;",
              stage="left:800px; top:165px; width:1000px; height:750px;"),
 "tall": dict(W=1080, H=1920, hl="left:90px; top:170px; width:900px; text-align:center;", bar="left:460px; top:120px;",
              stage="left:40px; top:470px; width:1000px; height:750px;"),
}

def scene_file(sid, lang, fmt, timing, prev):
    sun, svg, js = SC[sid]
    L, lab = LAYOUT[fmt], LABELS[lang]
    title = next(s for s in script["scenes"] if s["id"] == sid)["title"][lang]
    for k, v in lab.items():
        svg = svg.replace("{{" + k + "}}", v)
    svg = (f'<g id="@body">{svg}</g>' + SUN).replace("@", sid + "-")
    words = "".join(f'<span id="{sid}-h{i}">{w} </span>' for i, w in enumerate(title.split()))
    C = [c["start"] for c in timing["cues"]]; E = [c["end"] for c in timing["cues"]]; D = timing["duration"]
    return f'''<template>
<style>{CSS}
 #{sid}-hl {{ {L["hl"]} }} #{sid}-bar {{ {L["bar"]} }} #{sid}-stage {{ {L["stage"]} }}
</style>
<div id="{sid}" data-composition-id="{sid}" data-width="{L["W"]}" data-height="{L["H"]}">
 <div id="root">
  <div id="{sid}-bar" class="clip bar" data-start="0" data-duration="{D}"></div>
  <div id="{sid}-hl" class="clip hl" data-start="0" data-duration="{D}">{words}</div>
  <div id="{sid}-stage" class="clip stage" data-start="0" data-duration="{D}" data-layout-allow-overflow>
   <svg viewBox="0 0 1200 900" xmlns="http://www.w3.org/2000/svg">{svg}</svg>
  </div>
 </div>
</div>
<script>
(function () {{
 const tl = gsap.timeline({{paused: true}}), ID = "{sid}", q = n => "#" + ID + "-" + n;
 const C = {json.dumps(C)}, E = {json.dumps(E)}, D = {D}, LAST = {json.dumps(prev is None and False or timing.get("last", False))};
 const P = (s, t, d = 0.5) => tl.fromTo(s, {{opacity: 0, scale: 0.5, transformOrigin: "50% 50%"}}, {{opacity: 1, scale: 1, duration: d, ease: "back.out(1.7)"}}, Math.max(0, t));
 const F = (s, t, d = 0.45) => tl.fromTo(s, {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: d, ease: "power3.out"}}, Math.max(0, t));
 const Dr = (s, t, d = 0.6) => tl.fromTo(s, {{strokeDashoffset: 1}}, {{strokeDashoffset: 0, duration: d, ease: "power2.out"}}, Math.max(0, t));
 const X = (s, t, d = 0.25) => tl.to(s, {{opacity: 0, duration: d, ease: "power2.in"}}, Math.max(0, t));
 // the sun is carried over from where the previous scene left it
 const S0 = {json.dumps(prev or sun[:4])}, S1 = {json.dumps(sun[:4])};
 tl.fromTo(q("sun"), {{x: S0[0], y: S0[1], scale: S0[2]}}, {{x: S1[0], y: S1[1], scale: S1[2], duration: 0.7, ease: "power3.out"}}, 0);
 tl.fromTo(q("warm"), {{opacity: S0[3]}}, {{opacity: S1[3], duration: 0.7, ease: "power2.out"}}, 0);
 tl.fromTo(q("rays"), {{rotation: 0}}, {{rotation: D * 8, duration: D, ease: "none", svgOrigin: "0 0"}}, 0);
 tl.fromTo(q("bar"), {{scaleX: 0, transformOrigin: "0% 50%"}}, {{scaleX: 1, duration: 0.5, ease: "power3.out"}}, 0.1);
 document.querySelectorAll("#" + ID + "-hl span").forEach((w, i) =>
   tl.fromTo(w, {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}}, 0.2 + i * 0.08));
 {js}
 if (!LAST) {{ X(q("body"), D - 0.3); X("#" + ID + "-hl", D - 0.3); X(q("bar"), D - 0.3); }}
 window.__timelines[ID] = tl;
}})();
</script>
</template>
'''

def chunks(text, n=4):
    w = text.split(); k = max(1, round(len(w) / n)); size = math.ceil(len(w) / k)
    return [" ".join(w[i:i + size]) for i in range(0, len(w), size)]

def build(lang, fmt):
    timing = json.loads((HERE / "audio" / lang / "timing.json").read_text(encoding="utf-8"))
    by = {s["id"]: s for s in timing["scenes"]}
    ids = SHORT_SCENES if fmt == "tall" else [s["id"] for s in timing["scenes"]]
    out = HERE / "composition" / (lang if fmt == "wide" else f"{lang}-short")
    (out / "compositions").mkdir(parents=True, exist_ok=True); (out / "assets").mkdir(exist_ok=True)
    L = LAYOUT[fmt]
    hosts, t, prev, caps = [], 0.0, None, []
    for n, sid in enumerate(ids):
        tm = dict(by[sid]); tm["last"] = n == len(ids) - 1
        (out / "compositions" / f"{sid}.html").write_text(scene_file(sid, lang, fmt, tm, prev), encoding="utf-8")
        hosts.append(f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{t:.3f}" '
                     f'data-duration="{tm["duration"]}" data-track-index="1" data-track-kind="graphics" data-width="{L["W"]}" data-height="{L["H"]}"></div>')
        for c in tm["cues"]:
            parts = chunks(c["text"]); tot = sum(len(p) for p in parts); a = c["start"]
            for p in parts:
                d = (c["end"] - c["start"]) * len(p) / tot
                caps.append((round(t + a + 0.02, 3), round(d + (0.2 if p is parts[-1] else 0), 3), p)); a += d
        s = SC[sid][0]
        prev = [s[4], s[5], s[2], s[6]] if len(s) > 4 else s[:4]
        t += tm["duration"]
    total = round(t, 3)
    # audio: the scenes' own WAVs, in this cut's order
    import numpy as np, soundfile as sf
    wav = np.concatenate([sf.read(HERE / "audio" / lang / f"scene-{int(i[1:]):02d}.wav")[0] for i in ids])
    sf.write(out / "assets" / "voiceover.wav", wav, 24000)
    cap_host = ""
    if fmt == "tall":   # large burned-in captions for the Short
        groups = "".join(f'<div id="cap-{i}" class="clip capg" data-start="{a}" data-duration="{d}"><span id="cap-{i}-t">{p}</span></div>'
                         for i, (a, d, p) in enumerate(caps))
        (out / "compositions" / "captions.html").write_text(f'''<template>
<style>
 #root {{ position: absolute; inset: 0; font-family: var(--font-display); }}
 .capg {{ position: absolute; left: 0; width: 100%; top: 1290px; text-align: center; overflow: visible; }}
 .capg span {{ display: inline-block; max-width: 900px; font-size: 68px; font-weight: 700; line-height: 1.2; color: var(--bg);
   background: var(--text); padding: 14px 34px; border-radius: 28px; }}
</style>
<div id="captions" data-composition-id="captions" data-width="1080" data-height="1920"><div id="root">{groups}</div></div>
<script>
(function () {{
 const tl = gsap.timeline({{paused: true}});
 {json.dumps([c[0] for c in caps])}.forEach((a, i) =>
   tl.fromTo("#cap-" + i + "-t", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.14, ease: "power3.out"}}, a));
 window.__timelines["captions"] = tl;
}})();
</script>
</template>
''', encoding="utf-8")
        cap_host = (f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" '
                    f'data-duration="{total}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:5"></div>')
    (out / "index.html").write_text(f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={L["W"]}, height={L["H"]}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
/* brand/tokens.css (inlined at build time) */
{TOKENS}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ margin: 0; width: {L["W"]}px; height: {L["H"]}px; overflow: hidden; background: var(--bg); }}
#bg {{ position: absolute; inset: 0; background: var(--bg); }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{L["W"]}" data-height="{L["H"]}">
<div id="bg"></div>
{chr(10).join(hosts)}
{cap_host}
<audio id="voiceover" class="clip" data-start="0" data-duration="{total}" data-track-index="2" data-volume="1" src="assets/voiceover.wav"></audio>
</div>
<script>
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = gsap.timeline({{paused: true}});
</script>
</body>
</html>
''', encoding="utf-8")
    (out / "hyperframes.json").write_text(json.dumps({"name": f"{script['slug']}-{out.name}"}), encoding="utf-8") if not (out / "hyperframes.json").exists() else None
    (out / "timeline.json").write_text(json.dumps({"total": total, "scenes": [{"id": i, "duration": by[i]["duration"]} for i in ids], "captions": caps}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out.relative_to(HERE), total, "s")

if __name__ == "__main__":
    for lang in ("en", "hi"):
        for fmt in ("wide", "tall"):
            build(lang, fmt)
