# COVID-WasteWater-NE
The purpose of this repository is to house scripts for the automation of SARS-CoV-2 wastewater surveillance processing in Nebraska. Specifically, the anlaysis presented was tested and used on illumina sequencing data produced using the IDT [xGen SARS-CoV-2 Sgene amplicon sequencing panel](https://www.idtdna.com/pages/products/next-generation-sequencing/workflow/xgen-ngs-amplicon-sequencing/predesigned-amplicon-panels/sars-cov-2-amp-panel#product-details) (previously produced by Swift BioSciences) as this is a cheaper and scalable alternative to whole-genome sequencing of wastewater. 

The proposed analysis makes use of the existing tool [Freyja](https://github.com/andersen-lab/Freyja) ([Karthikeyan et al., 2022](https://www.nature.com/articles/s41586-022-05049-6)). Since Freyja was developed for whole-genome sequencing, our scripts and pipeline adapt this approach for S-gene only. Additionally, our scripts parse the freyja output data into a format which can be more easily vizualized. 

## Installation
**Under Development**

## Pre-Processing of Sequencing Data
Before running our pipeline, NGS data must undergo preprocessing. The necessary steps include:
1. Read Quality Control and Trimming
2. Primer Clipping (utilizing the [Primerclip](https://github.com/swiftbiosciences/primerclip#readme) software built to handle the xGen amplicon primers)
3. Alignment to a Reference Genome

This repository does not currently contain a script or pipeline that can be used for preprocessing. We recommend using the [TAYLOR Pipeline](https://github.com/greninger-lab/covid_swift_pipeline) developed by the Greninder Lab for IDT xGen amplicon sequencing data. The pipeline will produce .bam alignment files that can be used as input for our pipelines.

## Updating Variant Profiles
**Under Development**

## Running the Freyja-Pipeline
The Freyja pipeline takes .bam alignment files of NGS sequencing reads, and runs them through Freyja which performs variant calling and estimates the abundances of viral variants present within the sample. The estimates produced by Freyja are then parsed to create files that can be used for visualization.

Additionally, the pipeline has been developed in order to allow new data to be aggregated with others. This functionality is particularly useful for maintaining a consistent schedule of wastewater surveillance without the need to re-run previously analyzed data through Freyja. 