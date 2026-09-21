import pandas as pd,re,json
from pathlib import Path
BASE="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/"
e=pd.read_csv(BASE+"efeature.csv")
m=pd.read_csv(BASE+"20200711_patchseq_metadata_mouse.csv")
g=pd.read_csv(BASE+"geneExp_filtered.csv")
def toks(v): return re.findall(r"\d+",str(v))
out={
 "e_columns":list(e.columns),
 "e_ID_sample":[{"ID":str(x),"tokens":toks(x)} for x in e["ID"].head(12)],
 "meta_ephys_session_sample":[str(x) for x in m["ephys_session_id"].head(20)],
 "meta_transcriptomics_sample":[str(x) for x in m["transcriptomics_sample_id"].dropna().head(20)],
 "g_columns_first":list(g.columns[:25]),
 "g_shape":list(g.shape),
 "e_shape":list(e.shape),
 "m_shape":list(m.shape)
}
Path("neuro-beam/data/patchseq_id_diagnostic.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
