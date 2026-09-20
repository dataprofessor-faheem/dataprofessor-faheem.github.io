"""Create a harmonized one-row-per-neuron skeleton from source metadata tables."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"data"/"processed"; OUT.mkdir(parents=True,exist_ok=True)
MASTER_COLUMNS=["dataset_id","specimen_id","donor_id","species","brain_region","cortical_layer","cell_class","cell_subclass","t_type","MET_type","sex","age","experiment_batch","has_ephys","has_rna","has_morphology","ephys_qc_pass","rna_qc_pass","morphology_qc_pass"]
def main():
    pd.DataFrame(columns=MASTER_COLUMNS).to_csv(OUT/"master_neuron_table_skeleton.csv",index=False)
if __name__=="__main__": main()