# 2D_data_chrom_automation

This is a small package of helper functions for automation of data preparation steps during handling of chromatographic
data.

### KPL

See the readme in the KPL tool folder

### Data Inputs: ### 

The input data should contain columns named: "Name","Area", and "Height".
The default separator is "\t"

### Matrix_gen

Matrix_gen takes the summary tables (rows = compounds, columns = samples) as an input and generates:
1) ratio matrix for each sample
2) summary one row representation of all upper triangle of the ratio matrix transformed into the single line
3) representation.

The single line representation can be used as an input to commercial software programs
as the first column is the name of the sample,
and the rest of the columns represents the ratios - variables.

### Merging rations

This simple script takes two types of input tables - for definition of variables of interest and tables for analysis.
All variables involved in "define" tables will be used for construction of the final table. Only defined variables
for the previous step will be chosen from the variables in tables set for the analysis.

The final table is the summary of all samples, but the variables only correspond to those from the "define" set of tables.
The script also eliminates variables (columns) with sum of the zero values higher than the threshold that the user sets
at the start of the script.
This elimination is executed on the columns of the final summary table.

### Sort_by_name

Sort_by_name script takes all .txt files in the folder and generates a summary table.

Rows correspond to detected chemical compounds (every unique name has its own row - the comparison is based on strings).

Each column represents a sample which has been stored in the processed folder.

** note that the current version is only taking in chemical compounds which start with the "MX" prefix.
The behaviour can be edited on line # 34 of the code.

### Stat_dev
A simple function for cleaning up the data. If there are multiple rows in the input file, the script recalculates
deviation for each variable,
and sorts them and the resulting table contains only the top X (this parameter is also chosen by the user
at the beginning of the script) variables with the least variation. 
The script also eliminates variables (columns) with sum of the zero values higher than the threshold that the user sets
at the start of the script.

** note that the current version of the script is designed for work with the ratio matrices.
It replaces all values 1 for value 0. This behaviour can be changed at line #18, respectively #27.

