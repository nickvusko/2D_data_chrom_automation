
# KPL tool

KPL is a tool for creating user libraries of chemical compounds detected through two-dimensional chromatographic experiments.
The library keeps records af all detected compounds with a unique codename, which is then inherited by every found hit within the processed chromatograms.

## Input files

The standard input file structure is derived from default export format of LECO ChromaToF® software
Each exported file should be separated with a tabulator, should have a _.txt_ format, and should contain columns: _"Name"_, _"1st Dimension Retention Time (s)"_,
_"2nd Dimension Retention Time (s)"_, and _"Spectra"_.

## Execution

The tool can be run via _batch file_ -> **run_script.bat** which can be found in the root directory of the tool.
Or it can be launched via any terminal by running the **main.py** file.

## Config file

The config file contains two parameters, which are used for calculation of mass spectra similarity.\
_"sim compare"_ takes two possible options - DOT (dot product) and Pearson (Pearson's correlation coefficient)\
_"transformation"_ tuple(_a, b_) is used for recalculation of mass intensities (new_intensity = intensity ** _a_ * mass[m/z] ** _b_).\
Setting _a_ parameter to 0.53 is close to the square root of the original intensity value of the mass fragment.\
The higher the _b_ parameter, the more focus on the masses with higher m/z values.
The default setting favours characteristic m/z values [1]


```json
{
"sim_compare": "DOT",
"transformation": [0.53, 1.3]
}
```

## Database structure

Each newly found chemical compound is added as a new record with a unique code name. If the already existing record is detected in processed chromatograms,
the hit in the library is updated (name of the chromatogram is added to the _"found"_ list along the retention times and spectra) and the compound is renamed to a proper codename.

Each row represents one unique chemical compound
The unified sets of columns:
```
["Codename", "1st RT", "2nd RT", "Spectra", "Found", "Name", "calc_1stRT", "calc_2ndRT", "calc_spectra"]
```
where:\
**Codename** = unique codename
**1st RT** = median of detected retention times in the first dimension\
**2nd RT** = median of detected retention times in the second dimension\
**Spectra** = dictionary of median values for each [m/z] (in range from 31 to 800)\
**Found** = list of chromatogram where the chemical compound was found\
**Name** = name of the first hit according to NIST library\
**calc_1stRT** = list of all detected times in the first dimension (source of data for calculation of 1st RT)\
**calc_2ndRT** = list of all detected times in the second dimension (source of data for calculation of 2nd RT)\
**calc_spectra** = dictionary of all detected intensities for each [m/z] (source of data for calculation of Spectra)\

## Logs
Logs of each action are stored in **root/logs** folder

## Main menu

_**Create new KPL**_ - initialize dialog window for creation of new core database

_**Compare chromatograms to existing KPL**_ - initialize dialog window for comparing exported chromatograms to already existing database

_**Add new compound to the KPL**_ - initialize dialog window for adding database records from one library to the other

_**Export KPL**_ - export KPL to _.txt_ format


### Create new KPL

This function should be applied to a collection of manually evaluated chromatograms where each compound is named correctly (and has the same name through all the files).
Identification of chemical compounds is based on variables in the column = **_NAME_**.
The resulting library is stored in the HDF5 format.

**Currently set input folder** - variable which stores path to the folder containing source files (chromatograms)\
**Currently set output folder** - variable which stores path to newly created core library

### Compare chromatograms to existing KPL

This function compares non-processed chromatograms to existing database and renames chemical compounds according to that database
Identification of chemical compounds is based on search window (relevant for both retention times) and spectral similarity [2] (minimal threshold is set to **_90%_**).

kpl_compare.py line # 76
```python
result = ...
if result > 90:
    ...
```

If the compound is not found in the library, the new record is added.
Finally, as the result database is not marked as _core library_ it can be stored in the _.txt_ format.

**Loaded library** - variable which stores path to the library\
**Save as** - variable which stores path and name of the updated library\
**Input files location** - variable which stores path to non-processed chromatograms\
**Output files location** - variable which stores path where the renamed chromatograms should be stored

### Add new compound to KPL

This function adds record from one library to another library. This implementation allows to safely add record from a non-core library to the core library.
The user enters the codename into the input line, clicks on the **Add** button, checks if **Add (no codename)** changes and then presses the verification button **Add new compound to core library**.
When the user is done, they can simply close the window.

**Core library** - variable which stores path to edited library where the record should be added\
**User's library** - variable which stores path to library _**from**_ where the record should be added\
**MX codename...** - variable which stores the string representation of the transferred record

### Add new compound to KPL
This button simply pops up dialog window where the user can choose HDF5 database and export it to the txt format.
Exported library will be saved in the root folder of the tool.

## Training data
Training data can be acquired [here](https://doi.org/10.5281/zenodo.7307846) [3]


## References

[1] Kim, S., et al., Compound Identification Using Partial and Semipartial Correlations for Gas Chromatography–Mass Spectrometry Data. Analytical Chemistry, 2012. 84(15): p. 6477-6487
[2] Oh, C., et al., Comprehensive two-dimensional gas chromatography/time-of-flight mass spectrometry peak sorting algorithm. Journal of Chromatography A, 2008. 1179(2): p. 205-215
[3] Pojmanová P, Ladislavová N. 2DGCTOF Human Skin Scent Samples Dataset. In: Zenodo, editor. 1.0 ed2022. https://doi.org/10.5281/zenodo.7307846