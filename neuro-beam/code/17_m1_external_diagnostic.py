import pandas as pd, json
from pathlib import Path
BASE="https://raw.githubusercontent.com/berenslab/mini-atlas/master/data/"
meta=pd.read_csv(BASE+"m1_patchseq_meta_data.csv",sep="\t")
e=pd.read_csv(BASE+"m1_patchseq_ephys_features.csv")
counts=pd.read_csv(BASE+"m1_patchseq_exon_counts.csv.gz",compression="gzip",nrows=8)
out={
 "meta_shape":[int(meta.shape[0]),int(meta.shape[1])],
 "meta_columns":list(meta.columns),
 "meta_head":meta.head(3).astype(str).to_dict(orient="records"),
 "ephys_shape":[int(e.shape[0]),int(e.shape[1])],
 "ephys_columns":list(e.columns),
 "ephys_head":e.head(3).astype(str).to_dict(orient="records"),
 "counts_preview_shape":[int(counts.shape[0]),int(counts.shape[1])],
 "counts_columns_first":list(counts.columns[:30]),
 "counts_head_index":counts.iloc[:5,:6].astype(str).to_dict(orient="records")
}
Path("neuro-beam/data/m1_external_validation_diagnostic.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
