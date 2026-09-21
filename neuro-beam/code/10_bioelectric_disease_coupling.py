"""NEURO-BEAM: same-cell bioelectric–transcriptomic coupling and disease bridge.

Uses Allen visual-cortex Patch-seq processed matrices from the scMNC companion
repository. The original preprocessing explicitly aligns electrophysiology rows
and gene-expression columns by transcriptomics_sample_id.

Outputs:
- gene × electrophysiology Spearman associations with BH-FDR
- within-broad-class robustness for candidate disease-bridge genes
- per-gene Bioelectric Coupling Score (BCS)
- per-disease Exploratory Bioelectric Alteration Index (EBAI), combining
  neuronal bioelectric coupling with cancer mutation prevalence.

EBAI is a hypothesis-generation metric, not a causal effect estimate.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, norm

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"; DATA.mkdir(parents=True,exist_ok=True)

BASE="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/"
E_URL=BASE+"efeature.csv"
G_URL=BASE+"geneExp_filtered.csv"
M_URL=BASE+"20200711_patchseq_metadata_mouse.csv"
D_BRIDGE=DATA/"disease_bioelectric_bridge.json"

CORE_EFEATURES=[
    "vrest","ri","sag","tau","f_i_curve_slope","adaptation","latency","avg_isi",
    "upstroke_downstroke_ratio_long_square","peak_v_long_square",
    "trough_v_long_square","fast_trough_v_long_square","threshold_v_long_square",
    "threshold_i_long_square","threshold_v_short_square","threshold_i_short_square",
    "threshold_v_ramp","threshold_i_ramp"
]

def bh(pvals):
    p=np.asarray(pvals,float)
    out=np.full(len(p),np.nan)
    ok=np.isfinite(p)
    idx=np.where(ok)[0]
    if not len(idx): return out
    po=p[idx]; order=np.argsort(po); ranked=po[order]
    q=ranked*len(ranked)/(np.arange(len(ranked))+1)
    q=np.minimum.accumulate(q[::-1])[::-1]
    q=np.clip(q,0,1)
    out[idx[order]]=q
    return out

def first_existing(cols,cands):
    for c in cands:
        if c in cols:return c
    return None

def load_aligned():
    # Reconstruct the exact source alignment used in data_clean_visual.R:
    # ephys ID -> third numeric token (ephys session) -> metadata
    # ephys_session_id -> transcriptomics_sample_id.
    e=pd.read_csv(E_URL)
    g=pd.read_csv(G_URL)
    m=pd.read_csv(M_URL)

    if "ID" not in e.columns:
        raise RuntimeError("Original electrophysiology table lacks ID")

    def ephys_session_token(v):
        import re
        toks=re.findall(r"\d+",str(v))
        # Source R code uses the 3rd token after splitting on non-digits;
        # the first token is empty, so this is the 2nd numeric token.
        return toks[1] if len(toks)>=2 else None

    e=e.copy()
    e["_session_key"]=e["ID"].map(ephys_session_token).astype(str)

    if "ephys_session_id" not in m.columns or "transcriptomics_sample_id" not in m.columns:
        raise RuntimeError("Metadata missing ephys_session_id/transcriptomics_sample_id")

    mmap=m[["ephys_session_id","transcriptomics_sample_id","t_type"]].copy()
    mmap["_session_key"]=mmap["ephys_session_id"].astype(str)
    # In case CSV parsing renders integer IDs as 123.0, normalize both forms.
    mmap["_session_key"]=mmap["_session_key"].str.replace(r"\.0$","",regex=True)
    e["_session_key"]=e["_session_key"].str.replace(r"\.0$","",regex=True)
    e=e.merge(mmap,on="_session_key",how="left")

    gene_col=first_existing(g.columns,["gene","Gene","GENE"])
    if gene_col is None:
        gene_col=g.columns[0]
    g=g.drop_duplicates(subset=[gene_col]).set_index(gene_col)

    # Restrict to exactly those same-cell IDs present as gene-expression columns.
    e=e[e["transcriptomics_sample_id"].astype(str).isin(g.columns)].copy()
    e=e.drop_duplicates(subset=["transcriptomics_sample_id"],keep="first")
    e=e.set_index(e["transcriptomics_sample_id"].astype(str))
    shared=[x for x in e.index.astype(str) if x in g.columns]
    if len(shared)<1000:
        raise RuntimeError(f"Insufficient explicit same-cell overlap after source reconstruction: {len(shared)}")

    e=e.loc[shared]
    g=g[shared]
    broad=e["t_type"].fillna("").astype(str).str.split().str[0]
    broad.index=shared

    return e,g,broad

def spearman_fast(x,y):
    mask=np.isfinite(x)&np.isfinite(y)
    n=int(mask.sum())
    if n<30:return np.nan,np.nan,n
    r,p=spearmanr(x[mask],y[mask],nan_policy="omit")
    return float(r),float(p),n

def main():
    e,g,broad=load_aligned()
    features=[f for f in CORE_EFEATURES if f in e.columns]
    if len(features)<8:
        raise RuntimeError(f"Too few core electrical features available: {features}")

    # Normalize expression only by log1p for rank correlations; ranks make
    # monotonic scale transformations immaterial.
    G=g.apply(pd.to_numeric,errors="coerce")
    genes=list(G.index.astype(str))
    rows=[]
    for feature in features:
        y=pd.to_numeric(e[feature],errors="coerce").to_numpy(float)
        pvals=[]; temp=[]
        for gene in genes:
            x=pd.to_numeric(G.loc[gene],errors="coerce").to_numpy(float)
            r,p,n=spearman_fast(x,y)
            temp.append((gene,r,p,n)); pvals.append(p)
        q=bh(pvals)
        for (gene,r,p,n),qq in zip(temp,q):
            rows.append({"gene":gene,"feature":feature,"rho":r,"p":p,"q":qq,"n":n})
    assoc=pd.DataFrame(rows)
    assoc.to_csv(DATA/"bioelectric_gene_associations.csv",index=False)

    # Candidate panel genes from disease bridge; compute within-class robustness.
    disease=json.loads(D_BRIDGE.read_text(encoding="utf-8"))
    candidate=set(disease.get("geneByStudyPercent",{}).keys())
    # Mouse Patch-seq symbols are typically title case (Tp53, Kcnc2), while
    # cBioPortal human HUGO symbols are uppercase. Match case-insensitively
    # while preserving the mouse symbol for expression lookup and human symbol
    # for disease lookup.
    gene_upper_to_mouse={str(g).upper():str(g) for g in genes}
    shared_human=sorted(candidate.intersection(set(gene_upper_to_mouse.keys())))
    shared_candidates=[gene_upper_to_mouse[g] for g in shared_human]
    mouse_to_human={gene_upper_to_mouse[g]:g for g in shared_human}
    class_names=[c for c in sorted(broad.dropna().unique()) if c and c!="Unknown"]

    robust_rows=[]
    for gene in shared_candidates:
        xall=pd.to_numeric(G.loc[gene],errors="coerce")
        for feature in features:
            yall=pd.to_numeric(e[feature],errors="coerce")
            ars=assoc[(assoc.gene==gene)&(assoc.feature==feature)]
            if ars.empty: continue
            raw=ars.iloc[0]
            cls=[]
            signs=[]
            for cl in class_names:
                idx=(broad==cl)
                if int(idx.sum())<50: continue
                r,p,n=spearman_fast(xall[idx].to_numpy(float),yall[idx].to_numpy(float))
                if np.isfinite(r):
                    cls.append({"class":cl,"rho":r,"p":p,"n":n})
                    if abs(r)>=0.05: signs.append(np.sign(r))
            same_sign=0
            if signs:
                target=np.sign(float(raw.rho))
                same_sign=sum(1 for s in signs if s==target)/len(signs)
            robust_rows.append({
                "gene":gene,"feature":feature,
                "rho":float(raw.rho),"q":float(raw.q),"n":int(raw.n),
                "classesTested":len(cls),"sameDirectionFraction":same_sign,
                "withinClass":cls
            })

    # Per-gene BCS: strongest FDR-significant feature association, weighted by
    # within-class direction consistency. Score is bounded [0,1].
    gene_scores=[]
    by_gene={}
    for gene in shared_candidates:
        candidates_g=[r for r in robust_rows if r["gene"]==gene and np.isfinite(r["rho"])]
        sig=[r for r in candidates_g if r["q"]<=0.05]
        use=sig if sig else candidates_g
        if not use: continue
        best=max(use,key=lambda r:abs(r["rho"])*max(.25,r["sameDirectionFraction"]))
        bcs=min(1.0,abs(best["rho"])*2.5)*max(.25,best["sameDirectionFraction"])
        item={
            "gene":mouse_to_human.get(gene,gene.upper()),"mouseGene":gene,"bioelectricCouplingScore":float(bcs),
            "bestFeature":best["feature"],"rho":best["rho"],"q":best["q"],
            "sameDirectionFraction":best["sameDirectionFraction"],
            "classesTested":best["classesTested"]
        }
        gene_scores.append(item);by_gene[mouse_to_human.get(gene,gene.upper())]=item
    gene_scores.sort(key=lambda x:x["bioelectricCouplingScore"],reverse=True)

    # Disease EBAI: mutation prevalence weighted by empirical neuronal BCS.
    disease_scores=[]
    studies=disease.get("studies",[])
    for s in studies:
        sid=s["studyId"]; vals=[]; detail=[]
        for gene,gs in by_gene.items():
            pct=disease["geneByStudyPercent"].get(gene,{}).get(sid)
            if pct is None: continue
            w=gs["bioelectricCouplingScore"]
            vals.append((pct/100.0)*w)
            detail.append({
                "gene":gene,"mutationPercent":pct,"BCS":w,
                "contribution":(pct/100.0)*w,
                "bestFeature":gs["bestFeature"],"rho":gs["rho"]
            })
        score=100*np.mean(vals) if vals else None
        detail.sort(key=lambda x:x["contribution"],reverse=True)
        disease_scores.append({
            "studyId":sid,"name":s.get("name",sid),"cancerTypeName":s.get("cancerTypeName",""),
            "exploratoryBioelectricAlterationIndex":score,
            "nGenesContributing":len(vals),
            "topContributors":detail[:12]
        })
    disease_scores.sort(key=lambda x:(x["exploratoryBioelectricAlterationIndex"] is not None,x["exploratoryBioelectricAlterationIndex"] or -1),reverse=True)

    # Top associations overall for researcher exploration.
    top_assoc=assoc[np.isfinite(assoc.rho)].copy()
    top_assoc["absrho"]=top_assoc.rho.abs()
    top_assoc=top_assoc.sort_values(["q","absrho"],ascending=[True,False]).head(250)
    top_assoc=top_assoc.drop(columns=["absrho"]).to_dict(orient="records")

    out={
        "source":{
            "electrophysiology":E_URL,"geneExpression":G_URL,"metadata":M_URL,
            "alignmentEvidence":"Source preprocessing orders electrophysiology rows and gene-expression columns by transcriptomics_sample_id."
        },
        "nMatchedCells":int(e.shape[0]),
        "nGenesTested":int(G.shape[0]),
        "electricalFeatures":features,
        "associationMethod":"Spearman rank correlation; BH-FDR within each electrical feature",
        "candidatePanelSharedGenes":shared_human,
        "geneBioelectricScores":gene_scores,
        "diseaseBioelectricScores":disease_scores,
        "topAssociations":top_assoc,
        "interpretation":"BCS and EBAI are exploratory association/prioritization metrics. They do not demonstrate that mutations cause neuronal bioelectric changes or that cancer tissue recapitulates neuronal physiology."
    }
    (DATA/"bioelectric_disease_bridge.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    pd.DataFrame(gene_scores).to_csv(DATA/"bioelectric_gene_scores.csv",index=False)
    pd.DataFrame([{k:v for k,v in x.items() if k!="topContributors"} for x in disease_scores]).to_csv(DATA/"disease_bioelectric_scores.csv",index=False)
    print(json.dumps({
        "matchedCells":out["nMatchedCells"],"genes":out["nGenesTested"],
        "features":len(features),"sharedCandidates":len(shared_candidates),
        "topGeneScores":gene_scores[:8],
        "diseaseScores":[{"study":x["studyId"],"EBAI":x["exploratoryBioelectricAlterationIndex"]} for x in disease_scores]
    },indent=2))

if __name__=="__main__": main()
