"""Calibration and uncertainty analysis for NEURO-BEAM grouped-CV predictions."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
PRED=DATA/"ml_grouped_cv_predictions.csv"

def bootstrap_ci(df, target, model_col, nboot=1000, seed=20260921):
    rng=np.random.default_rng(seed)
    sub=df[df.target==target].copy()
    subjects=sub.subject_id.astype(str).unique()
    vals=[]
    for _ in range(nboot):
        ss=rng.choice(subjects,size=len(subjects),replace=True)
        parts=[]
        for s in ss:
            q=sub[sub.subject_id.astype(str)==str(s)]
            if len(q): parts.append(q)
        if not parts: continue
        x=pd.concat(parts,ignore_index=True)
        y=x.observed.to_numpy(float);p=x[model_col].to_numpy(float)
        if len(y)<20: continue
        r=spearmanr(y,p).statistic
        vals.append(float(r))
    if not vals:return [None,None]
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]

def calibration(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float)
    ok=np.isfinite(y)&np.isfinite(p);y=y[ok];p=p[ok]
    if len(y)<10:return {}
    A=np.column_stack([np.ones(len(p)),p])
    coef=np.linalg.lstsq(A,y,rcond=None)[0]
    return {"intercept":float(coef[0]),"slope":float(coef[1])}

def main():
    df=pd.read_csv(PRED)
    models={"Ridge":"ridge_pred","ExtraTrees":"extratrees_pred"}
    rows=[]
    conformal=[]
    for target in sorted(df.target.unique()):
        sub=df[df.target==target].copy()
        for model,col in models.items():
            y=sub.observed.to_numpy(float);p=sub[col].to_numpy(float)
            err=np.abs(y-p)
            cal=calibration(y,p)
            rho=spearmanr(y,p).statistic
            ci=bootstrap_ci(df,target,col,nboot=600)
            rows.append({
              "target":target,"model":model,"n":len(sub),
              "spearman":float(rho),"spearman_ci_low":ci[0],"spearman_ci_high":ci[1],
              "calibration_intercept":cal.get("intercept"),
              "calibration_slope":cal.get("slope"),
              "median_abs_error":float(np.median(err)),
              "p90_abs_error":float(np.quantile(err,.90)),
              "p95_abs_error":float(np.quantile(err,.95))
            })
            # Leave-one-fold-out residual quantile coverage.
            for fold in sorted(sub.fold.unique()):
                test=sub[sub.fold==fold];calib=sub[sub.fold!=fold]
                q90=float(np.quantile(np.abs(calib.observed-calib[col]),.90))
                q95=float(np.quantile(np.abs(calib.observed-calib[col]),.95))
                e=np.abs(test.observed-test[col])
                conformal.append({
                  "target":target,"model":model,"fold":int(fold),"n":len(test),
                  "q90":q90,"q95":q95,
                  "coverage90":float(np.mean(e<=q90)),
                  "coverage95":float(np.mean(e<=q95))
                })

    r=pd.DataFrame(rows);c=pd.DataFrame(conformal)
    r.to_csv(DATA/"ml_calibration_uncertainty.csv",index=False)
    c.to_csv(DATA/"ml_crossconformal_coverage.csv",index=False)
    summary={
      "method":"subject-bootstrap confidence intervals plus leave-one-fold-out residual intervals",
      "bootstrapUnit":"subject",
      "models":models,
      "metrics":r.to_dict(orient="records"),
      "coverageSummary":c.groupby(["model","target"]).agg(
          coverage90=("coverage90","mean"),coverage95=("coverage95","mean"),
          q90=("q90","mean"),q95=("q95","mean")
      ).reset_index().to_dict(orient="records"),
      "guardrail":"Residual intervals quantify empirical predictive uncertainty under the grouped-CV distribution; they are not mechanistic uncertainty."
    }
    (DATA/"ml_calibration_uncertainty.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps({"rows":len(r),"coverageRows":len(c),"extraTrees":r[r.model=="ExtraTrees"].head(5).to_dict(orient="records")},indent=2))

if __name__=="__main__":main()
