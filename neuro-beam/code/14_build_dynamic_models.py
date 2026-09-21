"""Build correlation-informed counterfactual neuron-model parameters for Top-500 genes.

The simulator is a normalized explanatory model. It does NOT estimate causal
biophysical effects of mutations or gene perturbations.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
CAT=DATA/"top500_discovery_catalog.json"

MECH_PREFIXES=("SCN","KCN","KCNA","KCNC","KCNQ","CACN","HCN","CLCN","ATP1A","TRP")

def assoc_map(g):
    return {x["feature"]:float(x["rho"]) for x in g.get("electricalAssociations",[]) if x.get("rho") is not None}

def get(a,key,default=0.0):
    v=a.get(key,default)
    return 0.0 if v is None or not np.isfinite(v) else float(v)

def main():
    cat=json.loads(CAT.read_text(encoding="utf-8"))
    models=[]
    rows=[]
    for g in cat["genes"]:
        a=assoc_map(g)
        # Normalized +1 expression-unit counterfactual mapping. Coefficients are
        # display/simulation scaling constants, not inferred physical effects.
        p={
          "vRestShift_mV":4.0*get(a,"vrest"),
          "inputResistanceMultiplier":float(np.exp(0.30*get(a,"ri"))),
          "tauMultiplier":float(np.exp(0.30*get(a,"tau"))),
          "fiGainMultiplier":float(np.exp(0.45*get(a,"f_i_curve_slope"))),
          "adaptationMultiplier":float(np.exp(0.35*get(a,"adaptation"))),
          "latencyMultiplier":float(np.exp(0.35*get(a,"latency"))),
          "sagMultiplier":float(np.exp(0.45*get(a,"sag"))),
          "thresholdCurrentMultiplier":float(np.exp(0.35*get(a,"threshold_i_long_square"))),
          "thresholdVoltageShift_mV":3.0*get(a,"threshold_v_long_square"),
          "spikeKineticsMultiplier":float(np.exp(0.30*get(a,"upstroke_downstroke_ratio_long_square")))
        }
        family="conductance-aware" if str(g["gene"]).upper().startswith(MECH_PREFIXES) else "phenotype-constrained"
        model={
          "rank":g["rank"],"gene":g["gene"],"mouseGene":g["mouseGene"],
          "modelMode":family,"discoveryScore":g["discoveryScore"],
          "bestElectricalFeature":g["bestElectricalFeature"],"bestRho":g["bestRho"],"bestQ":g["bestQ"],
          "parameters":p,
          "associations":g["electricalAssociations"],
          "interpretation":"Parameters are normalized correlation-informed counterfactual controls, not causal gene-effect estimates."
        }
        models.append(model)
        for k,v in p.items():
            rows.append({"rank":g["rank"],"gene":g["gene"],"mouse_gene":g["mouseGene"],
                         "model_mode":family,"parameter":k,"normalized_counterfactual_value":v,
                         "best_feature":g["bestElectricalFeature"],"best_rho":g["bestRho"],"best_q":g["bestQ"]})
    (DATA/"top500_dynamic_models.json").write_text(json.dumps({"models":models},indent=2),encoding="utf-8")
    pd.DataFrame(rows).to_csv(DATA/"top500_dynamic_model_parameters.csv",index=False)
    print(json.dumps({"models":len(models),"conductanceAware":sum(x["modelMode"]=="conductance-aware" for x in models)},indent=2))

if __name__=="__main__": main()
