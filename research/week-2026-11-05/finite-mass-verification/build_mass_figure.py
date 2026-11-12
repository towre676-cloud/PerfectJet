#!/usr/bin/env python3
"""Create original analytic SVG 14A from the exact universal bounds."""
from pathlib import Path
import math
out=Path(__file__).with_name('finite_mass_envelope_figure.svg')

C={'navy':'#21394b','teal':'#006b72','gold':'#bb7b3b','rust':'#a54c42','muted':'#586f79','grid':'#dae4e3','paper':'#fafcfb'}
chunks=['''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 960 492" role="img" aria-labelledby="mass-figure-title mass-figure-desc">
<title id="mass-figure-title">Sharp projective mass ratio and certified full-integral envelope</title>
<desc id="mass-figure-desc">Left: the convex scalar density as a function of projective ratio b, enclosed by its chord and tangent at rho 9 over 8. Right: exact lower and upper bounds for the normalized finite mass response for rho between seven eighths and nine eighths. The shaded region contains the full normalized integral response.</desc>
<rect width="960" height="492" fill="#ffffff"/>
<path d="M38 58 H922" stroke="#b9cccf" stroke-width="1"/>
<text x="40" y="30" font-family="Arial,Helvetica,sans-serif" font-size="11" font-weight="700" fill="#006b72" letter-spacing="2.5">THE FIRST MASS JET / A FINITE ENVELOPE</text>
<text x="40" y="92" font-family="Georgia,serif" font-size="25" fill="#21394b">A continuum enclosed by two equal-mass observables</text>
<text x="42" y="122" font-family="Arial,Helvetica,sans-serif" font-size="12.5" fill="#586f79">Projective positivity makes the endpoint bounds exact, not statistical.</text>
<text x="51" y="168" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#21394b">A · Integrand geometry at ρ = 9/8</text>
<text x="521" y="168" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#21394b">B · Normalized finite mass response</text>
''']

def line(x1,y1,x2,y2,c,w=1,dash=''):
 return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{c}" stroke-width="{w}" {f"stroke-dasharray={dash!r}" if dash else ""}/>'

def poly(points,color,width=2.5,dash='',fill='none'):
 p=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
 return f'<polyline points="{p}" stroke="{color}" stroke-width="{width}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round" {f"stroke-dasharray={dash!r}" if dash else ""}/>'

# Panel A: b in [0,1], f(b)=(1+b/8)^-3, chord above, tangent below.
x0,x1,y0,y1=64,435,190,409
Xa=lambda b:x0+(x1-x0)*b
Ya=lambda f:y1-(f-.60)/(.43)*(y1-y0)
for f in [.6,.7,.8,.9,1.0]:
 y=Ya(f);chunks.append(line(x0,y,x1,y,C['grid'],.8));chunks.append(f'<text x="{x0-13}" y="{y+4:.1f}" font-family="Arial" font-size="10" text-anchor="end" fill="{C["muted"]}">{f:.1f}</text>')
for b in [0,.25,.5,.75,1]:
 x=Xa(b);chunks.append(line(x,y0,x,y1,C['grid'],.7));chunks.append(f'<text x="{x:.1f}" y="{y1+19}" font-family="Arial" font-size="10" text-anchor="middle" fill="{C["muted"]}">{b:g}</text>')
bs=[i/150 for i in range(151)]
f=lambda b:(1+b/8)**(-3)
chord=lambda b:1+((8/9)**3-1)*b
tangent=lambda b:1-3*b/8
P=[(Xa(b),Ya(f(b))) for b in bs]
Q=[(Xa(b),Ya(chord(b))) for b in bs]
T=[(Xa(b),Ya(tangent(b))) for b in bs]
shade=P+list(reversed(Q))
chunks.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in shade)+'" fill="#d7e9e7" opacity="0.7"/>')
chunks.extend([poly(P,C['teal'],3),poly(Q,C['gold'],2.1),poly(T,C['rust'],1.6,'5 5')])
chunks.append(f'<text x="{(x0+x1)/2}" y="{y1+39}" font-family="Georgia" font-size="13" text-anchor="middle" fill="{C["navy"]}">b = a₇U / F₁  ∈ [0, 1]</text>')

# Panel B: normalized response in certified band across rho range.
x0,x1,y0,y1=543,915,190,409
Xb=lambda r:x0+(r-.875)/.25*(x1-x0)
Yb=lambda y:y1-(y+.19)/(.36)*(y1-y0)
for t in [-.15,-.1,-.05,0,.05,.1,.15]:
 y=Yb(t);chunks.append(line(x0,y,x1,y,C['grid'],.8));chunks.append(f'<text x="{x0-13}" y="{y+4:.1f}" font-family="Arial" font-size="10" text-anchor="end" fill="{C["muted"]}">{t:+.2f}</text>')
for rho in [.875,.9375,1,1.0625,1.125]:
 x=Xb(rho);chunks.append(line(x,y0,x,y1,C['grid'],.7));chunks.append(f'<text x="{x:.1f}" y="{y1+19}" font-family="Arial" font-size="10" text-anchor="middle" fill="{C["muted"]}">{rho:.4g}</text>')
rr=[.875+i*.25/220 for i in range(221)]
low=lambda r:(1-r**-3)/3
up=lambda r:r-1
P=[(Xb(r),Yb(low(r))) for r in rr]
Q=[(Xb(r),Yb(up(r))) for r in rr]
shade=P+list(reversed(Q))
chunks.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in shade)+'" fill="#d7e9e7" opacity="0.9"/>')
chunks.append(poly(P,C['teal'],3))
chunks.append(poly(Q,C['rust'],2.1,'6 4'))
for r in [.875,1.125]:
 for fun,c in [(low,C['teal']),(up,C['rust'])]:
  x,y=Xb(r),Yb(fun(r));chunks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{c}" stroke="white" stroke-width="1.5"/>')
chunks.append(f'<text x="{(x0+x1)/2}" y="{y1+39}" font-family="Georgia" font-size="13" text-anchor="middle" fill="{C["navy"]}">ρ = m₇²/M   ·   (I(ρ) − I₁) / I′₁</text>')
chunks.append('''<g font-family="Arial,Helvetica,sans-serif" font-size="10.5" fill="#21394b">
<path d="M64 471 h21" stroke="#006b72" stroke-width="3"/><text x="93" y="475">Exact density</text>
<path d="M222 471 h21" stroke="#bb7b3b" stroke-width="2"/><text x="251" y="475">Endpoint chord</text>
<path d="M411 471 h21" stroke="#a54c42" stroke-width="2" stroke-dasharray="6 4"/><text x="440" y="475">Linear tangent</text>
<rect x="605" y="462" width="21" height="13" fill="#d7e9e7" stroke="#9cbbbb" stroke-width=".7"/><text x="633" y="475">Certified response band</text>
</g>
</svg>''')
out.write_text('\n'.join(chunks))
print(out)
