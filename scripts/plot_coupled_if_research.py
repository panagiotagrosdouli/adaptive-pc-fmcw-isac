"""Generate an SVG feasibility map from a *fresh* post-freeze census.

Source-of-truth is run_coupled_if_research.census(), not manually transcribed
points. No manuscript source is changed. SVG legend distinguishes assumptions.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from runpy import run_path

census = run_path(str(Path(__file__).with_name("run_coupled_if_research.py")))["census"]

def svg_map(convention="complex",guard_fraction=0.0):
    # Census stores changed rows; reconstruct the exact same grid/feasibility.
    from pcfmcw_isac.paper1_physics_gate_ablation import RANGE_GRID_M, VELOCITY_GRID_MPS
    from pcfmcw_isac.policy_evaluation import profile_registry
    from pcfmcw_isac.coupled_if_research import coupled_physics,nominal_complex_if,nominal_positive_if,IFPassband
    ps=profile_registry()
    width,height=760,520
    x0,y0=85,75
    plot_w,plot_h=600,350
    dots=[]
    counts={"coupled_valid":0,"old_only":0,"unsupported":0}
    for r in RANGE_GRID_M:
        for v in VELOCITY_GRID_MPS:
            old=(r,v) in ((x["range_m"],x["radial_velocity_mps"]) for x in [])
            # old value explicitly obtained through the original gate
            from pcfmcw_isac.publication_protocol import EvaluationState,is_physics_feasible
            s=EvaluationState(12.,10.,r,v,0.,None,0.,0.,0)
            old=any(is_physics_feasible(p,s) for p in ps.values())
            coupled=False
            for p in ps.values():
                band=nominal_complex_if(p) if convention=="complex" else nominal_positive_if(p)
                band=IFPassband(band.lower_hz,band.upper_hz,guard_fraction*p.sample_rate_hz)
                coupled |= coupled_physics(p,r,v,passband=band).valid
            kind="coupled_valid" if coupled else ("old_only" if old else "unsupported")
            counts[kind]+=1
            x=x0+(r/60.)*plot_w
            y=y0+((60.-v)/120.)*plot_h
            color={"coupled_valid":"#16794f","old_only":"#bd5c00","unsupported":"#64748b"}[kind]
            dots.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="{color}"/>')
    grid=[]
    for i in range(7):
        x=x0+i*plot_w/6
        grid.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0+plot_h}" stroke="#ddd"/>')
        grid.append(f'<text x="{x}" y="{y0+plot_h+21}" font-size="12" text-anchor="middle">{i*10}</text>')
    for v in (-60,-30,0,30,60):
        y=y0+(60-v)/120*plot_h
        grid.append(f'<line x1="{x0}" y1="{y}" x2="{x0+plot_w}" y2="{y}" stroke="#ddd"/>')
        grid.append(f'<text x="{x0-12}" y="{y+4}" font-size="12" text-anchor="end">{v}</text>')
    legend="  ".join(f"{k}: {counts[k]}" for k in counts)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="760" height="520" viewBox="0 0 760 520">'
     '<rect width="100%" height="100%" fill="white"/>'
     '<text x="380" y="35" text-anchor="middle" font-size="17" font-family="sans-serif">Post-freeze PC-FMCW feasibility census</text>'
     f'<text x="380" y="55" text-anchor="middle" font-size="12" font-family="sans-serif">IF: {convention}; guard/Fs: {guard_fraction:g}; diagnostic only</text>'
     +''.join(grid+dots)
     +'<text x="385" y="475" text-anchor="middle" font-size="14">Range (m)</text>'
     +'<text x="20" y="245" font-size="14" transform="rotate(-90 20 245)" text-anchor="middle">Radial velocity (m/s)</text>'
     +f'<text x="380" y="501" text-anchor="middle" font-size="12">{legend}</text>'
     +'</svg>')

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--convention",choices=["complex","positive"],default="complex")
    p.add_argument("--guard-fraction",type=float,default=0.)
    p.add_argument("--output",default="artifacts/research_gaps/if_feasibility_map.svg")
    args=p.parse_args()
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(svg_map(args.convention,args.guard_fraction))
    print(output)

if __name__=="__main__":
    main()
