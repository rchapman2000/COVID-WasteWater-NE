# COVID-WasteWater-NE
The purpose of this repository is to house scripts for the automation of SARS-CoV-2 wastewater surveillance processing in Nebraska. Specifically, the anlaysis presented was tested and used on illumina sequencing data produced using the IDT [xGen SARS-CoV-2 Sgene amplicon sequencing panel](https://www.idtdna.com/pages/products/next-generation-sequencing/workflow/xgen-ngs-amplicon-sequencing/predesigned-amplicon-panels/sars-cov-2-amp-panel#product-details) (previously produced by Swift BioSciences) as this is a cheaper and scalable alternative to whole-genome sequencing of wastewater. 

The tool present in this repository, Wastewater Tools, contains a set of bioinformatics scripts related to the processing of wastewater data. The intended analysis makes use of the existing tool [Freyja](https://github.com/andersen-lab/Freyja) ([Karthikeyan et al., 2022](https://www.nature.com/articles/s41586-022-05049-6)). Since Freyja was developed for whole-genome sequencing, our scripts and pipeline adapt this approach for S-gene only. Additionally, our scripts parse the freyja output data into a format which can be more easily vizualized. 

## Installation
**Under Development**

## Pre-Processing of Sequencing Data
Before running our pipeline, NGS data must undergo preprocessing. The necessary steps include:
1. Read Quality Control and Trimming
2. Primer Clipping (utilizing the [Primerclip](https://github.com/swiftbiosciences/primerclip#readme) software built to handle the xGen amplicon primers)
3. Alignment to a Reference Genome

This repository does not currently contain a script or pipeline that can be used for preprocessing. We recommend using the [TAYLOR Pipeline](https://github.com/greninger-lab/covid_swift_pipeline) developed by the Greninder Lab for IDT xGen amplicon sequencing data. The pipeline will produce .bam alignment files that can be used as input for our pipelines.

## Freyja-Pipeline
The Freyja pipeline takes .bam alignment files of NGS sequencing reads, and runs them through Freyja which performs variant calling and estimates the abundances of viral variants present within the sample. The estimates produced by Freyja are then parsed to create files that can be used for visualization.

Additionally, the pipeline has been developed in order to allow new data to be aggregated with others. This functionality is particularly useful for maintaining a consistent schedule of wastewater surveillance without the need to re-run previously analyzed data through Freyja. 

### Required Files and Formats

#### Master File
The master file is a CSV file used by the pipeline to link a sample/file name to a Date and Collection Site. Thus it must containg the following columns:
1. Sample
2. Site
3. Date (In the format MM/DD/YYYY)
4. Week *(Optional - must be present if the --byWeek option is included)*

**(File Header is equired)**

**Example:**
```
Sample,Site,Date
waste-water-01,site01,11/08/2021
waste-water-02,site01,11/09/2021
```
#### Barcode File
The barcode file is used by Freyja to link a variant to a set of certain nucleotide changes from the WuHan-1 reference. However, new SARS-CoV-2 variants are constantly being discovered, and thus the barcode file that Freyja comes loaded with is out of date. Freyja requires that users manually update their barcode file using a provided command. Because our anlaysis is meant to allow customization the freyja features, we require the user to supply this file. Modifying the Freyja barcode file for S-gene mutations only can be found [above](#Updating-Variant-Profiles).

If you wish to use this pipeline for whole genome analysis, our pipeline still requires the user to supply a barcode file. This can be retrieved using the command:
```
freyja update --outDir DIRECTORY
```

If you wish to make a custom barcode file for another virus or organism, the barcode file must follow the following format guidelines:
1. Must be in CSV format
2. Each row represents a variant
3. Each column represents a nucleotide substitution
4. Cells are filled with 0 if a variant does not contain that mutation
5. Cells are filled with a 1 if a variant does contain that mutation
6. The first column contains variant names
7. The first row contains nucleotide subsitution names

**Example:**
```
,A15T,G25C
B1,0,1
B2,1,0
B3,0,0
```
#### Sublineage Map
The Sublineage Map file is a CSV file which denotes how to group certain subvariants under into parent classifications. The file contains the columns:
1. Lineage
2. Label - how to label that lineage (parent)

**(File Header is Required)**

**Example:**
```
Lineage,Label
AY.1,Delta
BA.1,Omicron
```

### Running the Pipeline

The pipeline script can be run using the following command (the included options are required):
```
wastewatertools freyja_pipeline -i INPUT_DIRECTORY \
    -o OUTPUT_DIRECTORY \
    -d DEMIX_FILE_DIRECTORY \
    -r REFERENCE \
    -m MASTER_FILE \
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
| -b / --barcode | File | A barcode file to be used by Freyja for processing ([Format](#barcode-file)). If this file is not provided, the default barcode file 
included in freyja will be updated and used. | Optional |
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

## Creating S Gene Variant Profiles
**Under Development**

## Parsing Gisaid Sequences to generate patient Data
**Under Development**

## Visualiation
**Under Development**