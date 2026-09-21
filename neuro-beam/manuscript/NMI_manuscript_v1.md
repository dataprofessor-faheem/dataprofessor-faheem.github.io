# NEURO-BEAM: Explainable machine intelligence links neuronal bioelectric phenotypes to cross-disease genomic programs

## Abstract
Neuronal physiology and molecular state are tightly coupled, yet computational frameworks rarely connect same-cell electrophysiology–transcriptomics with disease genomics while preserving source separation. We developed NEURO-BEAM, an explainable machine-intelligence framework integrating 3,654 visual-cortex Patch-seq neurons, subject-grouped transcriptome-to-electrophysiology prediction, independent motor-cortex validation and pan-cancer genomic projection. Electrical organization was reproducible under resampling, and nonlinear transcriptomic models predicted several electrophysiological traits with strong grouped-cross-validation rank concordance. Frozen models transferred to 1,304 motor-cortex neurons, with strongest external concordance for spike upstroke/downstroke ratio, threshold-current/rheobase, input resistance and membrane time constant. A transparent Top-500 discovery engine combines cancer recurrence with neuronal bioelectric association, while a phenotype-conditioned membrane simulator converts gene-specific electrical fingerprints into falsifiable dynamic hypotheses. NEURO-BEAM provides a reproducible strategy for cross-domain biological discovery without treating unmatched datasets as same-cell evidence.

## Introduction
Electrical phenotype is a defining property of neuronal identity. Resting membrane potential, input resistance, spike threshold, membrane time constant, firing adaptation and action-potential waveform collectively determine how a neuron integrates input and communicates within a circuit. Molecular atlases, by contrast, describe neuronal identity primarily through transcriptional programs. Although these representations are related, directly connecting them at scale remains challenging because electrophysiological and molecular measurements are often generated in different cells, experiments and laboratories.

Patch-seq provides a uniquely informative bridge by measuring electrophysiology and transcriptomics in the same neuron. This allows computational models to ask a well-posed question: how much of a cell’s electrical phenotype is encoded in its transcriptional state, and which genes or gene programs are most consistently associated with individual electrical traits? However, naive machine-learning workflows can overestimate predictability when neurons from the same subject appear in both training and test partitions, when acquisition variables enter the feature space, or when known cell-type labels are used to construct the electrical phenotypes later claimed to be discovered.

A second challenge arises when neuronal molecular programs are compared with disease genomics. Large disease resources can reveal recurrent genomic alterations, but they generally do not measure the same neurons or even the same tissue context. Combining such resources by direct feature concatenation therefore creates false multimodal observations. A defensible alternative is hierarchical transfer: learn molecular–electrical relationships only in genuinely matched cells, freeze the resulting representation, and then project selected molecular programs into independent disease cohorts as hypothesis-generating evidence.

Here we introduce NEURO-BEAM, an explainable computational framework designed around this separation. The framework first discovers electrophysiological structure independently of transcriptomic labels, then quantifies same-cell gene–electrical coupling, benchmarks transcriptome-to-electrophysiology prediction using subject-grouped validation, evaluates frozen models in an independent cortical region, and finally projects bioelectric-associated genes into human cancer cohorts using mutation-sequenced denominators and auditable mouse-to-human mapping. A dynamic membrane simulator provides a transparent final layer that converts observed association fingerprints into testable, explicitly non-causal electrophysiological hypotheses.

# Results

## NEURO-BEAM separates matched multimodal learning from cross-domain transfer
The discovery cohort comprised 3,654 visual-cortex neurons with matched processed electrophysiology and transcriptomic data after explicit cell-identifier reconstruction and quality filtering. Acquisition-timing and sweep-bookkeeping variables were excluded before electrical representation learning. Twenty-seven physiological variables remained for bioelectric discovery, while 1,302 genes were available for same-cell association and predictive modelling.

The framework maintains a strict distinction between matched and transferred information. Electrophysiology–transcriptomics analyses use the same Patch-seq neurons. Pan-cancer analyses are performed only after the neuronal associations are estimated and are therefore treated as independent-source genomic projection rather than multimodal same-cell learning. Failed disease-genomics retrievals are represented as missing values rather than biological zeros.

## Cortical neurons show reproducible but partly continuous bioelectric organization
A physiology-only baseline analysis identified five provisional electrical groups, but resampling and alternative clustering demonstrated that these groups should not be interpreted equally. Across 200 resampling iterations, the mean adjusted Rand index was 0.850. Four states were comparatively stable, with mean Jaccard values of 0.879, 0.945, 0.864 and 0.971, whereas a nine-cell fifth state was unstable (mean Jaccard 0.535) and was retained only as a rare provisional/outlier structure.

Alternative methods supported a partially continuous organization rather than a single definitive clustering. Gaussian-mixture BIC favoured seven components, whereas HDBSCAN identified four density-supported clusters. After electrical labels were frozen, correspondence with broad transcriptomic class was modest (ARI 0.243; NMI 0.284), indicating that the learned electrical organization was related to, but not reducible to, known molecular class labels.

## Same-cell transcriptomes predict multiple electrical phenotypes under subject-grouped validation
We next tested whether transcriptomic state predicts measured electrical properties without subject leakage. Expression values were transformed to within-cell percentile ranks and evaluated using five-fold GroupKFold partitioning across 936 reconstructed subject identifiers. A linear Ridge baseline was compared with a nonlinear ExtraTrees model using fold-local selection of the 300 most variable genes.

The nonlinear model showed substantial predictive rank concordance for several traits. Mean cross-validated Spearman correlations were 0.909 for action-potential upstroke/downstroke ratio, 0.874 for membrane time constant, 0.808 for long-square threshold current, 0.799 for input resistance, 0.708 for adaptation, 0.678 for mean interspike interval and 0.658 for the F-I slope. Corresponding mean R² values reached 0.732, 0.613, 0.674, 0.558 and 0.540 for upstroke/downstroke ratio, membrane time constant, threshold current, input resistance and F-I slope, respectively. Resting potential and threshold voltage were less predictable, indicating that transcriptomic information was informative but not uniformly sufficient across electrical phenotypes.

## Frozen transcriptomic models retain rank information in an independent cortical region
To test generalization, we froze the modelling strategy before evaluating an independent primary-motor-cortex Patch-seq cohort. The external dataset contained 1,304 cells with complete values for the harmonized analysis and 1,274 genes shared with the visual-cortex training representation. Expression was represented by the same within-cell percentile-rank transformation, 300 genes were selected using variance in visual cortex only, and M1 outcomes were not used for hyperparameter tuning.

Cross-region rank transfer was strongest for action-potential upstroke/downstroke ratio (Spearman ρ=0.627), the threshold-current/rheobase comparison (ρ=0.612), input resistance (ρ=0.556) and membrane time constant (ρ=0.500). Quantitative calibration was weaker than rank concordance, consistent with region- and protocol-dependent shifts. Resting potential and threshold voltage transferred only weakly. Sag and adaptation were excluded from the primary external claim because the source features used non-equivalent conventions/scales across datasets. These results support partial cross-region generalization while also demonstrating the importance of semantic feature harmonization.

## A Top-500 discovery engine identifies genes with joint cancer and bioelectric evidence
We next mapped 1,268 of the 1,302 Patch-seq genes to human gene identifiers and evaluated them across ten TCGA PanCancer Atlas cohorts using mutation-sequenced sample denominators. For each gene, a Cancer Score summarized percentiles of mean mutation prevalence, maximum mutation prevalence and cohort recurrence. A Bioelectric Score summarized the percentile of the maximum absolute gene–electrical Spearman correlation and the fraction of electrical traits significant at BH-FDR q<0.05. The Discovery Priority Score was defined transparently as the mean of the Cancer and Bioelectric Scores.

The resulting Top-500 panel contained genes spanning axon guidance, synaptic organization, ion handling and canonical cancer signalling. The highest-ranked genes were SLIT2, FAM135B, CACNA2D3, DSCAM, NRXN1, EGFR, CNTNAP4, GRIN3A, KCNT2 and KCNH7. For example, SLIT2 ranked first with a Discovery Priority Score of 0.945 and a strongest neuronal association with action-potential upstroke/downstroke ratio (ρ=-0.636), while EGFR ranked sixth with a strongest association to the same electrical trait (ρ=0.561). These rankings are intended to prioritize cross-domain hypotheses rather than identify causal disease genes for neuronal physiology.

## Gene-conditioned dynamic simulation converts association fingerprints into falsifiable hypotheses
To move from static ranking to testable electrical hypotheses, we constructed a phenotype-conditioned adaptive leaky integrate-and-fire simulator with an Ih-like sag component and spike-frequency adaptation. Each Top-500 gene is associated with an 18-trait electrical fingerprint derived from same-cell Patch-seq correlations. These associations modify interpretable parameters including resting potential, membrane resistance, membrane time constant, voltage threshold, input gain, adaptation strength, sag conductance, latency and spike-waveform proxy parameters.

The portal compares baseline, higher-expression-like and lower-expression-like simulations and reports membrane-voltage trajectories, spike count, firing rate, first-spike latency, mean interspike interval and model-parameter shifts. The simulator deliberately does not estimate gene knock-out or knock-in effects. Instead, it translates observational electrical fingerprints into explicit, reproducible dynamic hypotheses that can be falsified experimentally.

# Discussion
NEURO-BEAM was designed around a simple methodological constraint: biological integration should occur only at the level supported by the data. Same-cell Patch-seq permits direct electrophysiology–transcriptomics learning, whereas cancer genomic cohorts provide independent molecular context and therefore enter the framework through projection rather than concatenation. This architecture allows machine-learning methods to contribute to scientific discovery without obscuring the provenance of each claim.

The grouped-cross-validation results show that transcriptomic information carries substantial information about several electrical traits, particularly waveform dynamics, membrane time constant, threshold-current behaviour and input resistance. The external M1 analysis further shows that part of this information transfers across cortical regions, although quantitative calibration can shift substantially. The distinction between rank transfer and absolute-value transfer is important: strong correlation with poor R² should not be described as calibrated quantitative prediction.

The Top-500 analysis provides a second level of hypothesis generation. It identifies genes that are simultaneously recurrent in cancer-genomics cohorts and strongly associated with neuronal electrical traits, but these two forms of evidence originate from different biological contexts. The ranking therefore represents cross-domain prioritization rather than a disease mechanism. Genes such as CACNA2D3, GRIN3A, KCNT2 and KCNH7 may be particularly useful for follow-up because their molecular functions are more directly related to excitability, whereas canonical cancer genes such as EGFR provide opportunities to investigate less obvious links between signalling state and electrical phenotype.

The dynamic simulator adds interpretability but also introduces an additional modelling layer. Its value is that every parameter change can be traced back to a measured electrical association and every simulated trace can be regenerated. Its limitation is equally explicit: correlation-derived parameter shifts are not causal gene perturbations. Experimental perturbation, human neuronal validation and disease-specific electrophysiology will be necessary before mechanistic conclusions can be drawn.

More broadly, NEURO-BEAM illustrates how machine intelligence can be used as a structured scientific-discovery system rather than only as a predictor. The framework combines representation, leakage-safe prediction, external testing, cross-domain projection, transparent ranking and falsifiable simulation while retaining machine-readable provenance throughout. This architecture could be extended beyond cancer genomics to neurological disorders once appropriately matched disease resources are incorporated.

# Methods

## Visual-cortex Patch-seq processing
Processed visual-cortex Patch-seq electrophysiology, gene-expression and metadata tables were aligned through the electrophysiology session identifier and transcriptomics sample identifier used in the source preprocessing workflow. Cells lacking explicit cross-modal alignment were excluded.

## Electrical feature processing
Protocol timing and sweep-bookkeeping features were excluded from bioelectric discovery. Remaining numeric electrical features were robustly scaled. PCA was used for dimensional inspection, and K-means, Gaussian mixture and HDBSCAN results were evaluated with resampling and cluster-validity metrics.

## Gene–electrical association
For each gene and electrical feature, Spearman rank correlation was computed across matched neurons. Benjamini-Hochberg FDR correction was applied within each electrical trait. Headline genes were additionally evaluated for direction consistency across broad inhibitory classes when sufficient cells were available.

## Grouped predictive modelling
Transcriptomic values were converted to within-cell percentile ranks. Five-fold GroupKFold splitting used reconstructed subject identifiers, ensuring neurons from the same subject were not divided across training and test partitions. Ridge regression and ExtraTrees served as linear and nonlinear benchmarks. ExtraTrees used fold-local selection of the 300 most variable genes.

## External M1 validation
The independent M1 cohort was not used for model tuning. Genes were intersected across datasets and represented by within-cell percentile ranks. The final ExtraTrees model used visual-cortex-only gene selection and fixed hyperparameters. Primary external claims were restricted to semantically harmonized electrical variables.

## Pan-cancer projection and Top-500 ranking
Human orthographic gene matches were resolved to Entrez identifiers. Mutation data were retrieved from cBioPortal with mutation-sequenced denominators. The Cancer Score and Bioelectric Score were percentile-based composite summaries, and the Discovery Priority Score was their unweighted mean.

## Dynamic model
The dynamic model uses an adaptive leaky integrate-and-fire equation with an Ih-like phenomenological sag current. Gene-specific parameter shifts are bounded functions of the observed gene–electrical correlation fingerprint and are labelled association-conditioned simulations.

## Code and data availability
The live portal, analysis code, machine-readable outputs, release-audit status and downloadable matrices are maintained in the public NEURO-BEAM repository. A release audit verifies required file counts, Top-500 uniqueness, model-library completeness, grouped-CV outputs and external-validation availability before the project is labelled manuscript-ready.

# Main display-item plan — maximum six
1. **Figure 1:** NEURO-BEAM architecture, data provenance and leakage-safe transfer design.
2. **Figure 2:** Bioelectric representation, stability and transcriptomic-class label reveal.
3. **Figure 3:** Same-cell transcriptomic prediction with grouped CV, explainability and key gene–electrical associations.
4. **Figure 4:** Frozen external M1 validation, harmonization audit and rank-vs-calibration analysis.
5. **Figure 5:** Top-500 cancer–bioelectric discovery landscape and disease × gene × electrical-trait cube.
6. **Figure 6:** Gene-conditioned dynamic membrane simulation and sensitivity analysis.

# Current submission status
The computational engineering release audit passes all 15 required integrity checks. This indicates internal artifact completeness and reproducibility readiness; it does not imply editorial suitability or acceptance by any journal.
