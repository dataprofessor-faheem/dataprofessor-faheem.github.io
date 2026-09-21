"""Frozen cross-region external validation: VIS Patch-seq -> M1 Patch-seq.

No M1 outcomes are used for feature selection or hyperparameter tuning.

Cross-platform expression representation:
- intersect genes between VIS processed gene matrix and M1 exon counts
- within-cell percentile-rank normalization in both datasets
- select top 300 variable genes using VIS only
- fixed ExtraTrees hyperparameters from internal grouped benchmark

Harmonized electrical targets are pre-specified below.
"""
from __future__ import annotations
import json,re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import r2_score,mean_absolute_error

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data";DATA.mkdir(parents=True,exist_ok=True)
VIS="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/"
M1="https://raw.githubusercontent.com/berenslab/mini-atlas/master/data/"

MAP={
  "vrest":("Resting membrane potential (mV)",1.0),
  "ri":("Input resistance (MOhm)",1.0),
  "tau":("Membrane time constant (ms)",1.0),
  "latency":("Latency (ms)",1000.0),
  "upstroke_downstroke_ratio_long_square":("Upstroke-to-downstroke ratio",1.0),
  "sag":("Sag ratio",1.0),
  "threshold_v_long_square":("AP threshold (mV)",1.0),
  "threshold_i_long_square":("Rheobase (pA)",1.0),
  "adaptation":("Spike frequency adaptation",1.0)
}
def toks(v):return re.findall(r"\d+",str(v))

def load_vis():
    e=pd.read_csv(VIS+"efeature.csv");g=pd.read_csv(VIS+"geneExp_filtered.csv");m=pd.read_csv(VIS+"20200711_patchseq_metadata_mouse.csv")
    e["_session_id"]=e.ID.map(lambda x:toks(x)[1] if len(toks(x))>=2 else None)
    mm=m[["ephys_session_id","transcriptomics_sample_id"]].copy();mm["_session_id"]=mm.ephys_session_id.astype(str).str.replace(r"\.0$","",regex=True)
    e["_session_id"]=e["_session_id"].astype(str).str.replace(r"\.0$","",regex=True);e=e.merge(mm,on="_session_id",how="left")
    gene_col="gene" if "gene" in g.columns else g.columns[0];g=g.drop_duplicates(gene_col).set_index(gene_col)
    e=e[e.transcriptomics_sample_id.astype(str).isin(g.columns)].drop_duplicates("transcriptomics_sample_id").copy()
    e.index=e["transcriptomics_sample_id"].astype(str)
    shared=[x for x in e.index if x in g.columns];e=e.loc[shared];g=g[shared]
    return e,g

def main():
    ve,vg=load_vis()
    me=pd.read_csv(M1+"m1_patchseq_ephys_features.csv").set_index("cell id")
    mc=pd.read_csv(M1+"m1_patchseq_exon_counts.csv.gz",compression="gzip")
    gene_col=mc.columns[0];mc=mc.drop_duplicates(gene_col).set_index(gene_col)

    m_cells=[x for x in me.index.astype(str) if x in mc.columns]
    me=me.loc[m_cells];mc=mc[m_cells]

    genes=sorted(set(vg.index.astype(str)).intersection(set(mc.index.astype(str))))
    if len(genes)<500:raise RuntimeError(f"Too few shared genes: {len(genes)}")
    vg=vg.loc[genes];mc=mc.loc[genes]

    # platform-robust, cell-internal rank representation
    Xv=vg.apply(pd.to_numeric,errors="coerce").fillna(0).rank(axis=0,pct=True).T
    Xm=mc.apply(pd.to_numeric,errors="coerce").fillna(0).rank(axis=0,pct=True).T

    targets=[];Yv=[];Ym=[]
    for vt,(mt,scale) in MAP.items():
        if vt not in ve.columns or mt not in me.columns:continue
        yv=pd.to_numeric(ve.loc[Xv.index,vt],errors="coerce")*scale
        ym=pd.to_numeric(me.loc[Xm.index,mt],errors="coerce")
        targets.append(vt);Yv.append(yv.to_numpy(float));Ym.append(ym.to_numpy(float))
    Yv=np.column_stack(Yv);Ym=np.column_stack(Ym)

    keepv=np.isfinite(Yv).all(axis=1);keepm=np.isfinite(Ym).all(axis=1)
    Xv=Xv.iloc[np.where(keepv)[0]];Yv=Yv[keepv]
    Xm=Xm.iloc[np.where(keepm)[0]];Ym=Ym[keepm]

    # VIS-only top-variable genes and fixed model.
    var=np.nanvar(Xv.to_numpy(float),axis=0);sel=np.argsort(var)[-min(300,len(var)):]
    selected=np.array(genes)[sel]
    model=ExtraTreesRegressor(n_estimators=350,max_features="sqrt",min_samples_leaf=4,n_jobs=-1,random_state=42)
    model.fit(Xv.to_numpy(float)[:,sel],Yv)
    pred=model.predict(Xm.to_numpy(float)[:,sel])

    rows=[]
    for j,t in enumerate(targets):
        y=Ym[:,j];p=pred[:,j];rho,_=spearmanr(y,p)
        rows.append({
          "target_vis":t,"target_m1":MAP[t][0],"n_m1":len(y),
          "spearman":float(rho),"r2":float(r2_score(y,p)),"mae":float(mean_absolute_error(y,p))
        })
    pd.DataFrame(rows).to_csv(DATA/"m1_external_validation_metrics.csv",index=False)
    pd.DataFrame({
      "cell_id":np.repeat(Xm.index.values,len(targets)),
      "target":np.tile(targets,len(Xm)),
      "observed":Ym.reshape(-1),
      "predicted":pred.reshape(-1)
    }).to_csv(DATA/"m1_external_validation_predictions.csv",index=False)

    imp=pd.DataFrame({"gene":selected,"importance":model.feature_importances_}).sort_values("importance",ascending=False)
    imp.to_csv(DATA/"m1_external_model_feature_importance.csv",index=False)
    out={
      "discoveryRegion":"visual cortex","externalRegion":"primary motor cortex",
      "nTrainVIS":int(len(Xv)),"nExternalM1":int(len(Xm)),
      "nSharedGenes":len(genes),"nSelectedGenes":len(selected),
      "expressionRepresentation":"within-cell percentile rank",
      "featureSelection":"top 300 variance genes in VIS only",
      "model":"ExtraTrees; fixed before external evaluation",
      "harmonization":{k:{"m1":v[0],"visMultiplier":v[1]} for k,v in MAP.items()},
      "metrics":rows,
      "guardrail":"M1 outcomes were not used to tune feature selection or model hyperparameters."
    }
    (DATA/"m1_external_validation_summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
