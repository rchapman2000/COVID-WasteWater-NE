# COVID-WasteWater-NE
The purpose of this repository is to house scripts for the automation of SARS-CoV-2 wastewater surveillance processing in Nebraska. Specifically, the anlaysis presented was tested and used on illumina sequencing data produced using the IDT [xGen SARS-CoV-2 Sgene amplicon sequencing panel](https://www.idtdna.com/pages/products/next-generation-sequencing/workflow/xgen-ngs-amplicon-sequencing/predesigned-amplicon-panels/sars-cov-2-amp-panel#product-details) (previously produced by Swift BioSciences) as this is a cheaper and scalable alternative to whole-genome sequencing of wastewater. 

The tool present in this repository, **Wastewater Tools**, contains a set of bioinformatics scripts related to the processing of wastewater data. The intended analysis makes use of the existing tool [Freyja](https://github.com/andersen-lab/Freyja) ([Karthikeyan et al., 2022](https://www.nature.com/articles/s41586-022-05049-6)). Since Freyja was developed for whole-genome sequencing, our scripts and pipeline adapt this approach for targeted sequencing of the S-gene. 

Additionally, the utility of our scripts comes from the incremental nature of the output. By this, we mean that newly run data can be combined with previously run data, making it easier to continuously monitor wastewater data. One issue with this is that new SARS-CoV-2 lineages are constantly being discovered and other tools would require data to be *re-run* each time new lineages are added. Our pipeline circumvents this issue through its use of a 'sublineage-map' data structure. The utility of this data structure is explained further in teh [Sublineage Map Section](#sublineage-map)

To accomplish this our pipeline creates a tree data structure containing SARS-CoV-2 lineages, making use of data from the [Pango Lineages Github](https://github.com/cov-lineages/pango-designation) and [Nextstrain's Clade Scheme Github](https://github.com/nextstrain/ncov-clades-schema) including:
- [Lineage Designation List](https://github.com/cov-lineages/pango-designation/blob/master/lineage_notes.txt)
- [Lineage Alias Key](https://github.com/cov-lineages/pango-designation/blob/master/pango_designation/alias_key.json)
- [nCoV Clades JSON](https://github.com/nextstrain/ncov-clades-schema/blob/master/src/clades.json)
# Installation
To install this pipeline, enter the following commands:
```
# Clone the repository
git clone https://github.com/rchapman2000/COVID-WasteWater-NE

# Create a conda environment using the provided environment.yml file
conda env create -f environment.yml

# Activate the conda environment
conda activate WasteWater
```
## Updating the Pipeline
If you already have the pipeline installed, you can update it using the following commands:
```
# Navigate to your installation directory
cd COVID-WasteWater-NE

# Use git pull to get the latest update
git pull

# Activate the conda environment and use the environment.yml file to download updates
conda activate WasteWater
conda env update --file environment.yml --prune
```

# Sequencing Pre-Processing of Sequencing Data
Before running our pipeline, NGS data must undergo preprocessing. The necessary steps include:
1. Read Quality Control and Trimming
2. Primer Clipping (utilizing the [Primerclip](https://github.com/swiftbiosciences/primerclip#readme) software built to handle the xGen amplicon primers)
3. Alignment to a Reference Genome

This repository does not currently contain a script or pipeline that can be used for preprocessing. We recommend using the [TAYLOR Pipeline](https://github.com/greninger-lab/covid_swift_pipeline) developed by the Greninger Lab for IDT xGen amplicon sequencing data. The pipeline will produce .bam alignment files that can be used as input for our pipelines.

# General Technical Considerations
This pipeline does not consider proposed, misc., or recombinant lineages in its processing. Thus, these lineages will not be called by Freyja.
# S-Gene Technical Considerations
To classify lineages, Freyja uses mutation profiles derived from Gisaid sequences placed on the [USHER SARS-CoV-2 Tree](https://github.com/yatisht/usher). However, sequencing the s-gene alone gives 0 coverage of regions outside of the s-gene which can skew Freyja's demixing algorithm. Thus, to solve for this, we can remove the mutations outside of the s-gene from the profiles. In turn, this creates another issue, as some lineages will have identical S-gene mutation profiles (as they have lineage defining mutations outside of the S-gene).

To solve for this, our pipeline creates *groups* to represent the s-gene identical lineages. Thus, Freyja's output will contain calls of these groups rather than individual lineages. Using our [Sublineage Map](#sublineage-map) data structure, we collapse these groups under their corresponding parent class, providing accurate results at this resolution.

## Group Names
The naming of these S-Gene identical groups is important to ensuring that group remains unique, remains human interpretable, and can be traced to the lineages that comprise it, if necessary. The naming scheme is the following:

GROUP-PARENT_Sublineages_Like_FIRST-LINEAGE-IN-GROUP-ALPHABETICAL

*NOTE:* Some cases arise when the groups are heterogeneous (EX: B.1,A.1). The algorithm calculates which classification group the majority of the lineages in the s-gene identical group originate from. That will be how the group is classified. As well, the FIRST-LINEAGE-IN-GROUP-ALPHABETICAL will be the first lineage in the *majority sub-group* sorted alphabetically:

```
B.1,B.2,B.3,A.3 would be named B/A_Sublineages_Like_B.1 (As only B sublineages would be sorted)
```

# Modules
Wastewater tools contains several different modules pertinent to the analysis of wastewater data. These modules include
- Freyja Pipeline - automates the process of running wastewater data through Freyja and parsing of Freyja output into an analyzable format. Additionally, it can combine newly processed data with previous runs to create a continuous data output.
- Parse Freyja Data - This module is a standalone parser of freyja data. While this feature is included in the freyja pipeline. It is often helpful to parse the same set of data in multiple different ways (such as grouped by both date and week).
- Barcode and Collapse - This module is a standalone version of a functionality built into the Freyja Pipeline. It can take a set of barcodes (or alternatively download the latest barcodes using Freyja) and will generate a desired sublineage map. Additionally, the barcodes provided can be modified for S-gene sequencing.
- Gisaid Metadata Parser - This module takes a set of Gisaid metadata and generate a visualizable data format similar to the output of the freyja pipeline. This allows for direct comparison of wastewater and patient data.
- Get Mutation Profiles - This module allows the user to isolate mutation profiles of a lineage or set of lineages for manual comparison.

# Important File Formats
Many of the modules of wastewater tools require input files of differing formats. This section details the purpose and format of each.

## Collapse File
The pipeline will use its tree of SARS-CoV-2 lineages to automatically collapse sublineages into classes that the user defines. The collapse file is the file where the user defines these classes. The file consists of two columns:
1. Class - the name of the class
2. Parent/Representative lineage(s) within the class - multiple lineages can be supplied here

**(File Header is required)**
```
Class,Parent
Alpha,B.1.1.7
Delta,B.1.617.2
Omicron,B.1.1.529,BA.1,BA.3
Omicron (BA.2),BA.2
```
## Master File
The master file is a CSV file used by the pipeline to link a sample/file name to a Date and Collection Site. Thus it must containg the following columns:
1. Sample
2. Site
3. Date (In the format MM/DD/YYYY)
4. Week *(Optional - must be present if the --byWeek option is included)*

**(File Header is required)**

**Example:**
```
Sample,Site,Date
waste-water-01,site01,11/08/2021
waste-water-02,site01,11/09/2021
```
## Barcode File
The barcode file is used by Freyja to link a variant to a set of certain nucleotide changes from the WuHan-1 reference. However, new SARS-CoV-2 variants are constantly being discovered, and thus the barcode file that Freyja comes loaded with is out of date. Freyja requires that users manually update their barcode file using a provided command. If no barcode file is supplied to the pipeline, the ```freyja update``` command will be run prior to analysis to ensure that the barcode file is up to date.

Wastewater tools also includes a way to generate an updated barcode file including only S-gene mutations (See [Creating S-Gene Variant Profiles](#creating-s-gene-variant-profiles)).

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
## Sublineage Map
The Sublineage Map file denotes how to collapse individual subvariants to make output data more easily digestible. These files structured as a TSV, but represent a dictionary data structure. The file contains the following two columns separated by a tab character:
1. Group - The label to be given to that group of sublineages
2. Sublineages - A comma separated list of sublineages/groups to classify under that group

**(File Header is Required)**

**Example:**
```
Group,Sublineages
Omicron BA.1,BA.1.1,BA.1.2,...
Delta   AY.1,AY.1.1,AY.2,...
```

The sublineage map structure is crucial to not needing to update the pipeline. New lineages that are added will simply be added into the correct group and this will not affect the ability of the collapsing algorithm to find the group of previously existing lineages.

*Images to be added*

### S-Gene cases
The utility can be seen in the case S-Gene samples when new lineages are added. If one lineage was on its own one week, but a new lineages with an identical S-gene profile is added. The lineage which has previously been called on its own is now called as a group. However the computer would not see the group name and lineage name as the same, causing a discrepancy. 

*Images to be added*

With a sublineage map, the a new line for the group can simply be added where the first column is the group name and the second column contains the lineages within this group. The group name can then be added to the list of sublineages/groups under the group that the lineages derived from. Now the algorithm can correctly map both group and lone lineage

*Images to be added*
# Freyja Pipeline Module
The Freyja pipeline takes .bam alignment files of NGS sequencing reads, and runs them through Freyja which performs variant calling and estimates the abundances of viral variants present within the sample. The estimates produced by Freyja are then parsed to create files that can be used for visualization.

Additionally, the pipeline has been developed in order to allow new data to be aggregated with others. This functionality is particularly useful for maintaining a consistent schedule of wastewater surveillance without the need to re-run previously analyzed data through Freyja. 

## Running the Pipeline

The pipeline script can be run using the following command (the included options are required):
```
wastewatertools freyja_pipeline -i INPUT_DIRECTORY \
    -o OUTPUT_DIRECTORY \
    -d DEMIX_FILE_DIRECTORY \
    -r REFERENCE \
    -m MASTER_FILE \
    -c COLLAPSE_FILE [Optional Arguments]
```

### Pipeline Options:
| Option | Argument | Description | Requirement |
| ------ | -------- | ----------- | -------- |
| -i / --input | Directory Path | Directory containing input .bam files (Must be existing). | Required |
| -o / --output | Directory Path | Directory to place pipeline output (the pipeline will create this directory if it does not exist) | Required |
| -d / --demixDir | Directory Path | Directory to place .demix files produced by freyja. The purpose of this option is to allow for aggregation of input files with previously run data. The demix directory may contain .demix files from previous runs, and these will be included in the file output files. | Required |
| -r / --reference | File | A reference fasta file to be used (Must be the same reference used to generate the input bam files). | Required |
| -m / --masterfile | File | A .csv file that links sample names to wastewater sites and collection dates ([Format](#master-file)). | Required |
| -c | --collapse | File |A .tsv file which consists of group labels and parent lineages to collapse under them ([Format](#collapse-file)). | Required |
| -b / --barcode | File | A barcode file to be used by Freyja for processing ([Format](#barcode-file)). If this file is not provided, the default barcode file included in freyja will be updated and used. | Optional |
| -p / --pattern | Text | A regex pattern that can be used to remove extraneous text from a sample name. (Must be enclosed in single quotes) (Example: the pattern '.+?(?=\_S\d\*_L\d\*)' removes the pattern '_S##_L###' commonly added by illumina sequencers) | Optional |
| --s_gene | None | Tells the pipeline to expect S-Gene only sequencing data. Mutations outside of the S-Gene will be removed from barcodes and s-gene identical groups will be created. | Optional |
| --byDate| None | Produces data grouped by date rather than by individual sample (Masterfile must include a date column for each sample). | Optional (Cannot include both --byDate and --byWeek) |
| --byWeek | None | Produces data grouped by week rather than buy individual sample (Masterfile must include a week column for each sample). | Optional (Cannot include both --byDate and --byWeek) |
| --combineAll | None | Adds additional values to the dataframe considering all of the sites for that day/week. | Optional |

## Pipeline Output
The pipeline will produce the following output files:
```
Output Directory/
├── /barcodes-and-collapse/
│   └── Files produced by the Barcodes and Collapse Module 
├── /freyja-results/
│   ├── A depths.tsv file produced by freyja for each sample
│   └── A variants.tsv file produced by freyja for each sample
├── A matrix file for each site
├── A Filtered dataframe
└── An Unfiltered dataframe

Demix Directory/
└── A .demix file produced by freyja for each sample
```

Inside of the output directory the matrix and dataframe files are the primary output of the pipeline.

**Output File Descriptions:**

- **Matrix File:** (CSV Format) Each row of the matrix represents a Variant and each column represents a sample/date/week present. The cells within the matrix contain 0 or 1 representing if the variant was present in that sample/week/date. This format is useful for human visualization
- **Dataframe Files:** (CSV Format) These files are useful for graphing and visualization as they can be easily imported into R or pandas dataframe objects. These files contain the columns **sample, lineage, abundance, site**. Each row represents a lineages present in a given sample (Example: 1,Delta,0.855).
   - **unfiltered dataframe** - a dataframe file where no lineages have been collapsed based on the sublineage map.
   - **filtered dataframe** - a dataframe file containing the lineages combined into their parent based on the sublineage map.

# Standalone Parse Freyja Data Module
This module completes the last part of the freyja pipeline: parsing the freyja output data into a visualizable format. **Note**, this functionality is *already included* in the pipeline, and thus you do not **need** to run this separately. However, it is often useful to rerun this step separate from freyja such as wanting to group data by sample, date, or week (only one can be selected per run of the pipeline) or running with a different sublineage map to collapse lineages in an alternative manner.

## Running the Parse Freyja Data Module
To run this module, the following command can be run:
```
wastewatertools parse_freyja_data -i INPUT_DIRECTORY \
    -o OUTPUT_DIRECTORY \
    -s SUBLINEAGE_MAP \
    -m MASTER_FILE \
    [options]

```

### Parse Freyja Data Module Options
| Option | Argument | Description | Requirement |
| ------ | -------- | ----------- | -------- |
| -i / --input | Directory Path | Directory containing input .demix files (Must be existing). | Required |
| -o / --output | Directory Path | Directory to place pipeline output (the pipeline will create this directory if it does not exist) | Required |
| -m / --masterfile | File | A .csv file that links sample names to wastewater sites and collection dates ([Format](#master-file)). | Required |
| -s / --sublineageMap | File | A .csv file which denotes how to collapse lineages produced by Freyja ([Format](#sublineage-map)). | Required |
| -p / --pattern | Text | A regex pattern that can be used to remove extraneous text from a sample name. (Must be enclosed in single quotes) (Example: the pattern '.+?(?=\_S\d*_L\d*)' removes the pattern '_S##_L###' commonly added by illumina sequencers) | Optional |
| --byDate| None | Produces data grouped by date rather than by individual sample (Masterfile must include a date column for each sample). | Optional (Cannot include both --byDate and --byWeek) |
| --byWeek | None | Produces data grouped by week rather than buy individual sample (Masterfile must include a week column for each sample). | Optional (Cannot include both --byDate and --byWeek) |
| --combineAll | None | Adds additional values to the dataframe considering all of the sites for that day/week. | Optional |

## Parse Freyja Data Module Output
The Parse Freyja Data Module will produce the following output files:
```
Output Directory/
├── A matrix file for each site
├── A filtered dataframe
└── An unfiltered dataframe
```

Inside of the output directory the matrix and dataframe files are the primary output of the pipeline.

**Output File Descriptions:**

- **Matrix File:** (CSV Format) Each row of the matrix represents a Variant and each column represents a sample/date/week present. The cells within the matrix contain 0 or 1 representing if the variant was present in that sample/week/date. This format is useful for human visualization
- **Dataframe Files:** (CSV Format) These files are useful for graphing and visualization as they can be easily imported into R or pandas dataframe objects. These files contain the columns **sample, lineage, abundance, site**. Each row represents a lineages present in a given sample (Example: 1,Delta,0.855).
   - **unfiltered dataframe** - a dataframe file where no lineages have been collapsed based on the sublineage map.
   - **filtered dataframe** - a dataframe file containing the lineages combined into their parent based on the sublineage map.


# Barcode And Collapse Module
The Barcode and Collapse Module is a standalone version of functionality built-in to the pipeline itself. It can generate a sublineage map file for a set of barcodes (either supplied or downloaded using Freyja). As well, s-gene parsing can be specified.
## Running the Barcode And Collapse Module Module
To run the barcode And collapse module, the following command can be run:
```
wastewatertools barcode_and_collapse -o OUTPUT_DIRECTORY -c COLLAPSE_FILE [options]
```

Because Freyja requires manual updating of its barcode files, **no input is necessary for this function**. It simply runs Freyja's update function and accesses the output directly. 

However, in the case that you wish to use an existing barcode file, you may supply this via the **--input parameter**. Be sure that it adheres to the [Barcode File Format](#barcode-file).

Additionally, note that this module **filters out proposed lineages, misc lineages, and hybrid lineages by default**. This can be avoided by supplying the ```--noFilt``` option (See below).

### Barcode And Collapse Module Module Options

| Option | Argument | Description | Requirement |
| ------ | -------- | ----------- | -------- |
| -o / --outdir | Directory Path | Directory to place output files | Required |
| -c | --collapse | File |A .tsv file which consists of group labels and parent lineages to collapse under them ([Format](#collapse-file)). | Required |
| -i / --input | File | If you wish to convert an existing barcode file into one containing only S-Gene mutations, a barcode file can be supplied as input. (NOTE: the module will skip the ```freyja update``` command) | Optional |
| --s_gene | None | Tells the script to parse the barcodes to prepare for S-Gene sequencing Mutations outside of the S-Gene will be removed from barcodes and s-gene identical groups will be created. | Optional |


## Barcode And Collapse Module Module Output

### Whole Genome
```
Output Directory/
├── alias_key.json - a json file mapping aliases to their given lineages
├── curated_lineages.json - 'freyja update' output file
├── lineages.txt - a list of all current lineages taken from cov-lineages
├── NSClades.json - a json file containing data about the current SARS-CoV-2 Nextstrain Clades
├── raw_barcodes.csv - unfiltered barcodes produced by Freyja
├── filtered_barcodes.csv - barcodes that have had proposed, misc., and recombinant lineages removed.
└── sublineage-map.tsv - the sublineage map produced based on the collapse file provided by the user.
```
### S-Gene
```
Output Directory/
├── alias_key.json - a json file mapping aliases to their given lineages
├── curated_lineages.json - 'freyja update' output file
├── lineages.txt - a list of all current lineages taken from cov-lineages
├── NSClades.json - a json file containing data about the current SARS-CoV-2 Nextstrain Clades
├── raw_barcodes.csv - unfiltered barcodes produced by Freyja
├── sublineage-map.tsv - the sublineage map produced based on the collapse file provided by
                         the user.
├── S-Gene-Indistinguishable-Groups.txt - a text files containing s-gene identical groupings. 
                                          Can be searched to find what lineages fall under a 
                                          certain group.
├── S_Gene_Unfiltered.csv - a barcode file containing only S-Gene mutations, but lineages 
                            with the same mutation profile have not been combined
└── S_Gene_barcodes.csv - the final S-gene barcodes file where lineages with the same mutation 
                      profile have been combined
```

**Combined Lineage Example:**
The S-gene barcode module combines lineages with the same S-Gene profile into a singe entry. The combined lineage will then be represented as a list of lineages separated by pipe characters. 

```
Example:
B|B.1|B.1.1|B.2
```

Your [Sublineage Map](#sublineage-map) file will need to reflect this in the lineage column.

# Gisaid Metadata Parser Module
The Gisaid metadata parser module can be used to generate dataframe files for visualization for Fisaid metadata. This functionality is useful to compare wastewater and patient data together.

## Running the Gisaid Metadata Parser Module
To run this module, the following command can be used:
```
wastewatertools parse_gisaid -i INFILE \
    -o OUTFILE \
    -s SUBLINEAGE_MAP \
    --startDate DATE \
    --endDate DATE \
    [options]
```
### Gisaid Metadata Parser Module Options

| Option | Argument | Description | Requirement |
| ------ | -------- | ----------- | -------- |
| -i / --input| File | Path to a gisaid metadata file (TSV Format). | Required |
| -o / --output | String | Prefix to use when naming output files. | Required |
| -s / --sublin | File | A .csv file which denotes how to collapse lineages produced by Freyja ([Format](#sublineage-map)). | Required |
| --startDate | Date | The first date in the range of data to be parsed (Format: YYYY-MM-DD) | Required |
| --endDate | Date | The final date in the range of data to be parsed (Format: YYYY-MM-DD) | Required |
| --abundanceThreshold | Abundance threshold below which a lineage will be collapsed with its parent [Default: Collapse all Lineages] | Optional |
| --byWeek | Produce data grouped by week rather than date | Optional | 


# Get Mutation Profile Module
The Get Mutation Profile module can be used to isolate mutation profiles of specified lineages for manual comparison. 

A single lineage or list of lineages separated by commas can be supplied, and the mutation profiles will be aggregated into one output CSV file. This module also takes into account the fact that individual lineages may be present in S-Gene identical groups. Thus, it also outputs a summary file that notes whether a lineage is member in a certain S-gene identical group and lists the other lineages present in the group.

*Note: automated test cases for this module are in development*
## Running the Get Mutation Profile Module
To run this module, the following command can be used:
```
wastewatertools get_mutation_profile -l LINEAGES \
    -o OUTPREF \
    -s SUBLINEAGE_MAP \
    -b BARCODE_FILE
```

### Get Mutation Profile Module Options
| Option | Argument | Description | Requirement |
| ------ | -------- | ----------- | -------- |
| -l / --lineages | String | One or more lineages who's mutation profiles you would like to search. Multiple lineages should be supplied in a list separated by commas (Ex: -l BA.5 or -l BA.1,BA.2,BA.3) | Required |
| -o / --outpref | String | A prefix to name output files | Required |
| -s / --sublineageMap | File | A .csv file which denotes how to collapse lineages produced by Freyja ([Format](#sublineage-map)). | Required |
| -b / --barcodes | File | A .csv file containing mutation barcodes for various lineages to be searched ([Format](#barcode-file)) | Required |