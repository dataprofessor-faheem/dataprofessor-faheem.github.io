"""Fast calibration and uncertainty analysis for NEURO-BEAM grouped-CV predictions."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data"
df=pd.read_csv(DATA/"ml_grouped_cv_predictions.csv")

def metric_bootstrap(sub,col,nboot=250,seed=20260921):
    rng=np.random.default_rng(seed)
    subjects=sub.subject_id.astype(str).to_numpy()
    uniq=np.unique(subjects)
    groups={s:np.where(subjects==s)[0] for s in uniq}
    y=sub.observed.to_numpy(float);p=sub[col].to_numpy(float)
    vals=[]
    for _ in range(nboot):
        draw=rng.choice(uniq,size=len(uniq),replace=True)
        idx=np.concatenate([groups[s] for s in draw])
        yy=y[idx];pp=p[idx]
        r=spearmanr(yy,pp).statistic
        if np.isfinite(r):vals.append(float(r))
    return (float(np.quantile(vals,.025)),float(np.quantile(vals,.975))) if vals else (None,None)

def cal(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float)
    A=np.column_stack([np.ones(len(p)),p])
    b=np.linalg.lstsq(A,y,rcond=None)[0]
    return float(b[0]),float(b[1])

rows=[];cov=[]
for target in sorted(df.target.unique()):
    sub=df[df.target==target].copy()
    for model,col in {"Ridge":"ridge_pred","ExtraTrees":"extratrees_pred"}.items():
        y=sub.observed.to_numpy(float);p=sub[col].to_numpy(float);e=np.abs(y-p)
        lo,hi=metric_bootstrap(sub,col)
        inter,slope=cal(y,p)
        rows.append({
          "target":target,"model":model,"n":len(sub),
          "spearman":float(spearmanr(y,p).statistic),
          "spearman_ci_low":lo,"spearman_ci_high":hi,
          "calibration_intercept":inter,"calibration_slope":slope,
          "median_abs_error":float(np.median(e)),
          "p90_abs_error":float(np.quantile(e,.90)),
          "p95_abs_error":float(np.quantile(e,.95))
        })
        for fold in sorted(sub.fold.unique()):
            te=sub[sub.fold==fold];ca=sub[sub.fold!=fold]
            ce=np.abs(ca.observed-ca[col]);teerr=np.abs(te.observed-te[col])
            q90=float(np.quantile(ce,.90));q95=float(np.quantile(ce,.95))
            cov.append({"target":target,"model":model,"fold":int(fold),"n":len(te),"q90":q90,"q95":q95,
                        "coverage90":float(np.mean(teerr<=q90)),"coverage95":float(np.mean(teerr<=q95))})

r=pd.DataFrame(rows);c=pd.DataFrame(cov)
r.to_csv(DATA/"ml_calibration_uncertainty.csv",index=False)
c.to_csv(DATA/"ml_crossconformal_coverage.csv",index=False)
summary={
 "method":"subject bootstrap (250 resamples) + leave-one-fold-out residual coverage",
 "metrics":r.to_dict(orient="records"),
 "coverageSummary":c.groupby(["model","target"]).agg(coverage90=("coverage90","mean"),coverage95=("coverage95","mean"),q90=("q90","mean"),q95=("q95","mean")).reset_index().to_dict(orient="records"),
 "guardrail":"Intervals describe predictive uncertainty under grouped-CV sampling, not mechanistic uncertainty."
}
(DATA/"ml_calibration_uncertainty.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(json.dumps({"rows":len(r),"coverageRows":len(c)},indent=2))
