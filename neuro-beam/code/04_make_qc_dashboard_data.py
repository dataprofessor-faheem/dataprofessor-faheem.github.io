"""Generate dashboard-ready QC summaries."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; INFILE=ROOT/"data"/"processed"/"master_neuron_table.csv"; OUT=ROOT/"results"/"dashboard_data"; OUT.mkdir(parents=True,exist_ok=True)
def main():
    df=pd.read_csv(INFILE)
    pd.DataFrame({"metric":["neurons","donors","datasets"],"value":[len(df),df.get("donor_id",pd.Series(dtype=str)).nunique(),df.get("dataset_id",pd.Series(dtype=str)).nunique()]}).to_csv(OUT/"summary_cards.csv",index=False)
    for col in ["dataset_id","brain_region","cell_class","cell_subclass","cortical_layer"]:
        if col in df.columns: df[col].fillna("Missing").value_counts(dropna=False).rename_axis(col).reset_index(name="n").to_csv(OUT/f"counts_{col}.csv",index=False)
if __name__=="__main__": main()