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

## Freyja-Pipeline
The Freyja pipeline takes .bam alignment files of NGS sequencing reads, and runs them through Freyja which performs variant calling and estimates the abundances of viral variants present within the sample. The estimates produced by Freyja are then parsed to create files that can be used for visualization.

Additionally, the pipeline has been developed in order to allow new data to be aggregated with others. This functionality is particularly useful for maintaining a consistent schedule of wastewater surveillance without the need to re-run previously analyzed data through Freyja. 

### Required Files and Formats

#### Master File

#### Barcode File

#### Sublineage Map
### Running the Pipeline

The pipeline script can be run using the following command (the included options are required):
```
source freyja-pipeline.sh -i INPUT_DIRECTORY \
    -o OUTPUT_DIRECTORY \
    -d DEMIX_FILE_DIRECTORY \
    -r REFERENCE \
    -m MASTER_FILE \
    -b BARCODE_FILE \
    -s SUBLINEAGE_MAP
```

### Pipeline Options:
| Option | Argument | Description | Requirement |
| ------ | -------- | ----------- | -------- |
| -i / --input | Directory Path | Directory containing input .bam files (Must be existing). | Required |
| -o / --output | Directory Path | Directory to place pipeline output (the pipeline will create this directory if it does not exist) | Required |
| -d / --demixDir | Directory Path | Directory to place .demix files produced by freyja. The purpose of this option is to allow for aggregation of input files with previously run data. The demix directory may contain .demix files from previous runs, and these will be included in the file output files. | Required |
| -r / --reference | File | A reference fasta file to be used (Must be the same reference used to generate the input bam files). | Required |
| -m / --masterfile | File | A .csv file that links sample names to wastewater sites and collection dates ([Format](#master-file)). | Required |
| -b / --barcode | File | A barcode file to be used by Freyja for processing ([Format](#barcode-file)) | Required |
| -s / --sublineageMap | File | A .csv file which denotes how to collapse lineages produced by Freyja ([Format](#sublineage-map)). | Required |
| -p / --pattern | Text | A regex pattern that can be used to remove extraneous text from a sample name. (Must be enclosed in single quotes) (Example: the pattern '.+?(?=\_S\d*_L\d*)' removes the pattern '_S##_L###' commonly added by illumina sequencers) | Optional |
| --byWeek | None | Produces data grouped by week rather than be individual sample collection date (Masterfile must include a week column for each sample). | Optional |
| --combineAll | None | Produces a combined file where lineage abundances from all sites are averaged together for each day/week. | Optional |

### Pipeline Output
The pipeline will produce the following output files:
```
Output Directory/
├── /freyja-results/
│   ├── A depths.tsv file produced by freyja for each sample
│   └── A variants.tsv file produced by freyja for each sample
├── A matrix file for each site
├── A filtered dataframe for each site
└── An unfiltered dataframe for each site

Demix Directory/
└── A .demix file produced by freyja for each sample
```

Inside of the output directory the matrix and dataframe files are the primary output of the pipeline.

**Output File Descriptions:**

- **Matrix File:** (CSV Format) Each row of the matrix represets a Variant and each column represents a sample/date/week present. The cells within the matrix contain 0 or 1 representing if the variant was present in that sample/week/date. This format is useful for human visualization
- **Dataframe Files:** (CSV Format) These files are useful for graphing and visualization as they can be easily imported into R or pandas dataframe objects. These files contain the columns **sample, lineage, abundance**. Each row represents a lineages present in a given sample (Example: 1,Delta,0.855).
   - **unfiltered dataframe** - a dataframe file where no lineages have been collapsed based on the sublineage map.
   - **filtered dataframe** - a dataframe file containg the lineages combined into their parent based on the sublineage map.