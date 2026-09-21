"""Build gene-conditioned dynamic membrane model parameter library.

The simulator is phenotype-constrained, not causal. Each gene's observed
Patch-seq correlation fingerprint is mapped to parameter shifts in an adaptive
leaky integrate-and-fire model with an Ih-like sag term.

Higher-expression-like and lower-expression-like simulations simply reverse
the sign of the observed association fingerprint; they are not experimental
gene perturbation estimates.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
BIO=DATA/"top500_bioelectric_matrix.csv"
CAT=DATA/"top500_cancer_bioelectric_genes.csv"

BASELINE={
  "E_L_mV":-68.0,
  "V_reset_mV":-63.0,
  "V_threshold_mV":-50.0,
  "tau_m_ms":20.0,
  "R_MOhm":100.0,
  "refractory_ms":2.0,
  "adaptation_b_pA":20.0,
  "tau_w_ms":120.0,
  "g_h_relative":0.10,
  "E_h_mV":-35.0,
  "input_gain":1.0,
  "latency_bias_ms":0.0,
  "spike_width_ms":1.2
}

FEATURE_MAP={
  "vrest":("E_L_mV",4.0),
  "ri":("R_MOhm",25.0),
  "tau":("tau_m_ms",7.0),
  "threshold_v_long_square":("V_threshold_mV",4.0),
  "threshold_i_long_square":("input_gain",-0.30),
  "f_i_curve_slope":("input_gain",0.40),
  "adaptation":("adaptation_b_pA",18.0),
  "sag":("g_h_relative",0.20),
  "latency":("latency_bias_ms",18.0),
  "avg_isi":("refractory_ms",1.5),
  "upstroke_downstroke_ratio_long_square":("spike_width_ms",-0.35),
  "fast_trough_v_long_square":("V_reset_mV",3.0),
  "trough_v_long_square":("V_reset_mV",2.0),
  "threshold_v_short_square":("V_threshold_mV",2.0),
  "threshold_i_short_square":("input_gain",-0.15),
  "threshold_v_ramp":("V_threshold_mV",2.0),
  "threshold_i_ramp":("input_gain",-0.15),
  "peak_v_long_square":("spike_width_ms",0.15)
}

def main():
    bio=pd.read_csv(BIO)
    cat=pd.read_csv(CAT)
    ranks=dict(zip(cat.gene,cat["rank"]))
    dps=dict(zip(cat.gene,cat.discovery_priority_score))

    out=[]
    csv_rows=[]
    for gene,x in bio.groupby("gene"):
        x=x.copy()
        fingerprints=[]
        shifts={k:0.0 for k in BASELINE}
        for _,r in x.iterrows():
            f=str(r["feature"]); rho=float(r["rho"]); q=float(r["q"]) if pd.notna(r["q"]) else None
            fingerprints.append({"feature":f,"rho":rho,"q":q,"n":int(r["n"])})
            if f in FEATURE_MAP:
                p,scale=FEATURE_MAP[f]
                # q-weight limits influence of weak/non-significant associations.
                sig_weight=1.0 if q is not None and q<=0.05 else 0.35
                shifts[p]+=rho*scale*sig_weight

        # Bound shifts to conservative ranges.
        bounds={
          "E_L_mV":(-6,6),"V_reset_mV":(-5,5),"V_threshold_mV":(-6,6),
          "tau_m_ms":(-10,10),"R_MOhm":(-40,40),"refractory_ms":(-1.5,3),
          "adaptation_b_pA":(-20,35),"g_h_relative":(-0.15,0.35),
          "input_gain":(-0.45,0.55),"latency_bias_ms":(-20,35),
          "spike_width_ms":(-0.45,0.65)
        }
        for p,(lo,hi) in bounds.items():
            shifts[p]=float(np.clip(shifts[p],lo,hi))

        high={}
        low={}
        for p,v in BASELINE.items():
            high[p]=float(v+shifts.get(p,0))
            low[p]=float(v-shifts.get(p,0))
        # Physical/implementation guards
        for d in (high,low):
            d["tau_m_ms"]=max(5.0,d["tau_m_ms"])
            d["R_MOhm"]=max(25.0,d["R_MOhm"])
            d["refractory_ms"]=max(0.8,d["refractory_ms"])
            d["adaptation_b_pA"]=max(0.0,d["adaptation_b_pA"])
            d["g_h_relative"]=max(0.0,d["g_h_relative"])
            d["input_gain"]=max(0.25,d["input_gain"])
            d["spike_width_ms"]=max(0.4,d["spike_width_ms"])

        best=max(fingerprints,key=lambda z:abs(z["rho"])) if fingerprints else None
        item={
          "gene":gene,
          "rank":int(ranks.get(gene,0)),
          "discoveryPriorityScore":float(dps.get(gene,0)),
          "baseline":BASELINE,
          "parameterShiftHighExpressionLike":shifts,
          "highExpressionLike":high,
          "lowExpressionLike":low,
          "electricalFingerprint":sorted(fingerprints,key=lambda z:abs(z["rho"]),reverse=True),
          "bestAssociation":best,
          "model":"adaptive LIF + Ih-like sag phenomenological simulator",
          "interpretation":"Association-conditioned model only; not a causal gene perturbation model."
        }
        out.append(item)
        for condition,params in [("baseline",BASELINE),("high_expression_like",high),("low_expression_like",low)]:
            for p,v in params.items():
                csv_rows.append({
                  "gene":gene,"rank":ranks.get(gene),"condition":condition,
                  "parameter":p,"value":v,
                  "model":"adaptive LIF + Ih-like sag",
                  "interpretation":"phenotype-constrained association model"
                })

    out=sorted(out,key=lambda z:z["rank"] or 999999)
    (DATA/"top500_dynamic_model_library.json").write_text(json.dumps({"genes":out,"baseline":BASELINE,"featureParameterMap":FEATURE_MAP},indent=2),encoding="utf-8")
    pd.DataFrame(csv_rows).to_csv(DATA/"top500_dynamic_model_parameters.csv",index=False)
    print(json.dumps({"genes":len(out),"first":[{"gene":x["gene"],"rank":x["rank"],"best":x["bestAssociation"]} for x in out[:5]]},indent=2))

if __name__=="__main__": main()
