# StroopMouse Data

Tools for organizing and processing behavior datasets comprising several subjects and sessions.

## Description

Projects involving automated behavioral readouts can generate large amounts of data that are difficult to process and harmonize across large numbers of subjects and experimental sessions.

This project provides tools for managing and analyzing behavioral data collected from experiments involving mice. The data is stored in HDF5 format, which allows for efficient storage and retrieval of large datasets.

## Installation

To install the package, clone the repository and use `pip` to install the dependencies:

```sh
git clone https://github.com/smail031/stroopmouse_data.git
cd stroopmouse_data
pip install .
```

## Requirements

Installation requires the following Python packages:
- `h5py==3.6.0`
- `numpy==1.24.4`

## Usage

This tool organizes and processes behavior data through *dataset* files, which contain references to experimental data files stored systematically in a central data repository. 

Dataset files are created using a command line interface, and are stored in .hdf5 files. All changes to dataset files are documented and timestamped in the dataset file's activity log. 

These dataset files can then be used to extract and process relevant behavioral data across several subjects and sessions (blocks).

## Data Storage Format

Data should be stored in the following directory structure:
```
data_repository/
    {subject}/
        {date}/
            ms{subject}_{date}_block{block}.hdf5
```
For example:
```
stroopmouse_data/
    1/
        2023-10-01/
            ms1_2023-10-01_block1.hdf5
```

The experimental data should be stored in .hdf5 files.

### Creating or editing a Dataset

To create a new dataset or edit an existing one, run the following command in your terminal:

```sh
python -m stroopmouse_data.create.create_edit_dataset.py
```

You will be prompted to enter paths for the data repository, and the dataset file repository. You will then follow the prompts to create a new dataset or edit an existing one. At any time, press `h` to see a list of available commands and corresponding descriptions. When opening a dataset file, you will be prompted to write a plain text description of your changes, which will be stored in the dataset's activity log.

### Opening a Dataset

To extract and process data, your dataset file must first be opened using `dataset_load()`.

```python
# Import necessary modules
import stroopmouse_data.load.core as core

# Define the paths for the data repository and dataset repository
data_repo_path = 'path/to/data_repository'
dataset_repo_path = 'path/to/dataset_repository'

# Load dataset files
datasets, dataset_names = core.dataset_load(data_repo_path, dataset_repo_path)
```
```plaintext
Enter dataset name: ...
```

```python
# Iterate over the datasets to extract data
for dataset in datasets:
    for mouse in dataset.mouse_objects:
        choices_data = mouse.get_data('choices', vector=True)
        print(f'Mouse {mouse.mouse_number} choice data: {choices_data}')
```


```plaintext
Mouse 1 choice data: ['L' 'R' 'L' 'L' 'R']
Mouse 2 choice data: ['R' 'L' 'R' 'R' 'L']
Mouse 3 choice data: ['L' 'L' 'R' 'L' 'R']
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Sébastien Maillé - smail031@uottawa.ca
