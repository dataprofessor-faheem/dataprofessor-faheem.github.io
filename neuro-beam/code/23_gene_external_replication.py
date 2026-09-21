"""Gene-level external M1 replication for Top-500 NEURO-BEAM genes."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data"
MBASE="https://raw.githubusercontent.com/berenslab/mini-atlas/master/data/"
BIO=DATA/"top500_bioelectric_matrix.csv"
CAT=DATA/"top500_gene_catalog.csv"

# Traits with closest semantic correspondence. Sag/adaptation are deliberately excluded.
MAP={
 "vrest":"Resting membrane potential (mV)",
 "ri":"Input resistance (MOhm)",
 "tau":"Membrane time constant (ms)",
 "latency":"Latency (ms)",
 "upstroke_downstroke_ratio_long_square":"Upstroke-to-downstroke ratio",
 "threshold_i_long_square":"Rheobase (pA)"
}

def main():
    b=pd.read_csv(BIO)
    cat=pd.read_csv(CAT)
    meta=cat[["gene","mouse_gene","rank"]].drop_duplicates().sort_values("rank")
    eph=pd.read_csv(MBASE+"m1_patchseq_ephys_features.csv")
    ex=pd.read_csv(MBASE+"m1_patchseq_exon_counts.csv.gz",compression="gzip")
    intr=pd.read_csv(MBASE+"m1_patchseq_intron_counts.csv.gz",compression="gzip")
    ex=ex.set_index(ex.columns[0]);intr=intr.set_index(intr.columns[0])
    ix=ex.index.intersection(intr.index)
    counts=ex.loc[ix].apply(pd.to_numeric,errors="coerce").fillna(0)+intr.loc[ix].apply(pd.to_numeric,errors="coerce").fillna(0)
    counts.columns=[str(c)[1:] if str(c).startswith("X") else str(c) for c in counts.columns]
    cellcol="cell id";eph=eph.set_index(eph[cellcol].astype(str))
    cells=[c for c in counts.columns.astype(str) if c in eph.index]
    counts=counts[cells];eph=eph.loc[cells]
    lib=counts.sum(axis=0).replace(0,np.nan)
    expr=np.log1p(counts.divide(lib,axis=1)*1e6)

    rows=[]
    for _,m in meta.iterrows():
        hg=str(m.gene);mg=str(m.mouse_gene);rank=int(m["rank"])
        if mg not in expr.index:continue
        x=pd.to_numeric(expr.loc[mg],errors="coerce").to_numpy(float)
        trait_rows=[]
        for vf,mf in MAP.items():
            if mf not in eph.columns:continue
            y=pd.to_numeric(eph[mf],errors="coerce").to_numpy(float)
            ok=np.isfinite(x)&np.isfinite(y)
            if ok.sum()<100:continue
            mr=spearmanr(x[ok],y[ok]).statistic
            vr=b[(b.gene==hg)&(b.feature==vf)]
            if vr.empty:continue
            vrow=vr.iloc[0];v1=float(vrow.rho);q=float(vrow.q) if pd.notna(vrow.q) else np.nan
            sign_same=bool(np.sign(v1)==np.sign(mr)) if np.isfinite(mr) else False
            strength=float(np.sqrt(abs(v1*mr))) if np.isfinite(mr) else np.nan
            trait_rows.append({
              "gene":hg,"mouse_gene":mg,"rank":rank,"trait":vf,
              "v1_rho":v1,"v1_q":q,"m1_rho":float(mr),"n_m1":int(ok.sum()),
              "sign_concordant":sign_same,"geometric_abs_strength":strength
            })
        rows.extend(trait_rows)

    df=pd.DataFrame(rows);df.to_csv(DATA/"gene_external_m1_trait_replication.csv",index=False)
    sums=[]
    for g,x in df.groupby("gene"):
        # Primary replication evidence weights only V1-significant traits.
        sig=x[x.v1_q<=0.05]
        use=sig if len(sig)>=3 else x
        fingerprint=spearmanr(use.v1_rho,use.m1_rho).statistic if len(use)>=4 else np.nan
        signfrac=float(use.sign_concordant.mean()) if len(use) else np.nan
        meanstrength=float(use.geometric_abs_strength.mean()) if len(use) else np.nan
        # bounded replication score [0,1]
        fpterm=max(0,float(fingerprint)) if np.isfinite(fingerprint) else 0.0
        score=0.45*signfrac+0.35*min(1,meanstrength/0.5)+0.20*fpterm
        sums.append({
          "gene":g,"mouse_gene":x.mouse_gene.iloc[0],"rank":int(x["rank"].iloc[0]),
          "traits_evaluated":int(len(use)),"sign_concordance_fraction":signfrac,
          "mean_geometric_abs_strength":meanstrength,
          "trait_fingerprint_spearman":float(fingerprint) if np.isfinite(fingerprint) else None,
          "external_replication_score":float(np.clip(score,0,1))
        })
    sd=pd.DataFrame(sums).sort_values(["external_replication_score","rank"],ascending=[False,True])
    sd.to_csv(DATA/"gene_external_m1_replication_summary.csv",index=False)
    payload={
      "nGenes":int(sd.gene.nunique()),"nM1Cells":len(cells),"traits":MAP,
      "summary":sd.to_dict(orient="records"),
      "guardrail":"M1 replication is based only on semantically closest traits and gene-expression/electrical rank associations. It is not a gene perturbation test."
    }
    (DATA/"gene_external_m1_replication.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"nGenes":payload["nGenes"],"top":sd.head(12).to_dict(orient="records")},indent=2))

if __name__=="__main__":main()
