"""Generate an animated terminal SVG (SMIL only -> works inside GitHub <img>)."""
from html import escape

FS = 15            # font size
CW = FS * 0.6      # monospace char width
LH = 23            # line height
X0 = 22
Y0 = 62
W = 760
TYPE = 0.065       # seconds per typed char

GREEN, BLUE, TXT, DIM, YEL = "#3ECF8E", "#58a6ff", "#c9d1d9", "#8b949e", "#e3b341"
PROMPT_USER = "fea@homelab"
PROMPT_PATH = ":~$ "

# (kind, payload, pause_after)
# kind: "cmd" typed after a prompt, "out" printed at once (list of (text, color) segments)
SCRIPT = [
    ("cmd", "whoami", 0.35),
    ("out", [("sysadmin · infra admin · writes the tools ops never got", TXT)], 0.6),
    ("cmd", "systemctl status fea", 0.35),
    ("out", [("● ", GREEN), ("fea.service", TXT), (" - infra by day, automation by night", DIM)], 0.12),
    ("out", [("     Loaded: ", DIM), ("loaded (/etc/systemd/system/fea.service; ", TXT), ("enabled", GREEN), (")", TXT)], 0.12),
    ("out", [("     Active: ", DIM), ("active (running)", GREEN), (" since boot", TXT)], 0.12),
    ("out", [("      Tasks: ", DIM), ("infra · automation · open-source tools", TXT)], 0.7),
    ("cmd", "cat ~/.motto", 0.35),
    ("out", [("If I have to do it twice, I script it.", YEL)], 0.5),
]

parts = []
t = 0.6
y = Y0
ids = 0


def appear(t_):
    return f'<set attributeName="opacity" to="1" begin="{t_:.2f}s" fill="freeze"/>'


def prompt_line(y_, t_):
    return (f'<text x="{X0}" y="{y_}" opacity="0">{appear(t_)}'
            f'<tspan fill="{GREEN}">{PROMPT_USER}</tspan><tspan fill="{BLUE}">{escape(PROMPT_PATH)}</tspan></text>')


for kind, payload, pause in SCRIPT:
    if kind == "cmd":
        parts.append(prompt_line(y, t))
        t += 0.25
        x = X0 + len(PROMPT_USER + PROMPT_PATH) * CW
        n = len(payload)
        ids += 1
        cid = f"c{ids}"
        vals = ";".join(f"{i * CW + (2 if i else 0):.1f}" for i in range(n + 1))
        times = ";".join(f"{i / n:.4f}" for i in range(n + 1))
        dur = n * TYPE
        parts.append(
            f'<clipPath id="{cid}"><rect x="{x - 1:.1f}" y="{y - FS}" width="0" height="{LH}">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{times}" calcMode="discrete" '
            f'begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
            f'<text x="{x:.1f}" y="{y}" fill="{TXT}" clip-path="url(#{cid})">{escape(payload)}</text>'
        )
        t += dur + pause
    else:
        spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in payload)
        parts.append(f'<text x="{X0}" y="{y}" opacity="0" xml:space="preserve">{appear(t)}{spans}</text>')
        t += pause
    y += LH

# final prompt + blinking cursor
parts.append(prompt_line(y, t))
cx = X0 + len(PROMPT_USER + PROMPT_PATH) * CW
parts.append(
    f'<rect x="{cx:.1f}" y="{y - FS + 2}" width="{CW:.1f}" height="{FS + 3}" fill="{GREEN}" opacity="0">'
    f'<animate attributeName="opacity" values="1;0" dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite" calcMode="discrete"/>'
    f'</rect>'
)
H = y + 26

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: whoami — sysadmin, infra admin, automation; motto: If I have to do it twice, I script it.">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,"DejaVu Sans Mono","Liberation Mono",Consolas,monospace;font-size:{FS}px;white-space:pre}}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M0.5 32 V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V32 Z" fill="#161b22" stroke="#30363d"/>
<circle cx="20" cy="16.5" r="6" fill="#ff5f57"/><circle cx="40" cy="16.5" r="6" fill="#febc2e"/><circle cx="60" cy="16.5" r="6" fill="#28c840"/>
<text x="{W / 2}" y="21" fill="{DIM}" text-anchor="middle" style="font-size:12px">{PROMPT_USER}: ~</text>
{chr(10).join(parts)}
</svg>
'''

import sys
out = sys.argv[1] if len(sys.argv) > 1 else "terminal.svg"
open(out, "w", encoding="utf-8").write(svg)
print(f"wrote {out}  {W}x{H}  total anim {t:.1f}s")
