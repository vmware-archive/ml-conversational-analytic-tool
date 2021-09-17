# ML Conversational Analytic Tool

The ML Conversational Analytic Tool is a machine learning framework to automatically assess pull request comments and
reviews for constructive and inclusive communication.

## Motivation

Constructive and inclusive communication ensures a productive and healthy working environment in open source
communities. In open source, communication happens in many forms, including pull requests that are text-based
conversations crucial to open source collaboration. The ML Conversational Analytic Tool identifies constructive and
inclusive pull requests to foster a healthier open source community.

## Overview

1. [Motivation](#motivation)
2. [Overview](#overview)
3. [Build and Run](#build-and-run)
    1. [Environment Setup](#environment-setup)
        - [Prerequisites](#prerequisites)
        - [Installation](#installation)
    2. [Build Dataset](#build-dataset)
        - [Extract Raw Data from GitHub](#extract-raw-data-from-github)
        - [Annotate](#annotate)
    3. [Train models](#train-models)
4. [Documentation]()
5. [Contributing](#contributing)
6. [License](#license)

## Build and Run

### Environment Setup

- [Prerequisites](#prerequisites)
- [Installation](#installation)

#### Prerequisites

- Python 3.6+

#### Installation

A [virtualenv](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) or similar tools to
create isolated Python environment is recommended for this project.

1. Install `virtualenv`
   ```python
   pip install virtualenv
   ```

2. Set up ML Conversational Analytic Tool in a virtualenv
   ```python
   python3 -m venv virtualenv-ml-conversational
   ```

3. Activate the virtualenv
   ```python
   source ./virtualenv-ml-conversational/bin/activate
   ```

4. Update pip
   ```python
   pip install --upgrade pip
   ```

5. Install required python libraries by running the command below
   ```python
   pip install -r requirements.txt
   ```

The libraries used within the project are available in the [requirements.txt](./requirements.txt).

### Build Dataset

- [Extract Raw Data from GitHub](#extract-raw-data-from-github)
- [Annotate](#annotate)

#### Extract Raw Data from GitHub

`runDataExtraction.py` extracts raw data from GitHub based on parameters passed in by the user. To successfully run the
script, a [GitHub access token](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)
is required and must be set as an environment variable.
```
GITACCESS=<YOUR_TOKEN>
```

Run the script by passing in `organization` and `repo`  
```python
python runDataExtraction.py <organization> <repo>
```

- `organization` is the name of the repository owner
- `repo` is the name of the repository; use 'all' to extract all repositories owned by organization
- (optional) `-reactions` is an optional flag to extract comment and review reactions.

#### Annotate

`featureVector.py` prepares your data for annotation use. Run the script by passing in path to `rawdatafile` and `words`.

```python
python featureVector.py <rawdatafile> <words> -unannotated
```

- `rawdatafile` is location of raw data csv
- `words` is location of file with lookup words (not needed for annotation purposes)
- (optional) `-unannotated` is an optional flag to generate data for annotation

To annotate the raw data extracted we recommend using
[Data Annotator For Machine Learning](https://github.com/vmware/data-annotator-for-machine-learning).

### Train models

After both raw and annotated datasets are available, models can be trained to predict Constructiveness and Inclusiveness

There are two models available for training

- `BaseCNN`
- `BaseLSTM`

To train, run the script with required parameters path to `annotated_filename`, `dataset_filename`, `model`, and `outcome`.

```python
python run.py <annotated_filename> <dataset_filename> <model> <outcome>
```

- `annotated_filename` is the location of the annotated dataset file
- `dataset_filename` is the location of the raw data
- `model` is the type of model and can be 'LSTM' or 'CNN'
- `outcome` can be 'Constructive', 'Inclusive' or 'Both'
- (optional) `-roleRelevant` indicates that the encoding generated should be a stacked matrix representing user roles in
 conversation. If it is not set then a single matrix representing each comment/review without the role is generated.
- (optional) `-pad` indicates that the number of comment/review should be padded to be a constant value. This argument
 is required to be set for `CNN` and not set for `LSTM`.

Both `BaseCNN` and `BaseLSTM` also have prediction explanation mechanisms that can be accessed through the
`.explain(obs)` method in both classes.

## Documentation
Auto-generated API documentation can be found in [docs/ml-conversational-analytic-tool](./docs/ml-conversational-analytic-tool)
directory.

Run the following command to update the API documentation

```python
PYTHONPATH=./ml-conversational-analytic-tool pdoc --html --output-dir docs ml-conversational-analytic-tool
```

## Contributing

The ml-conversational-analytic-tool project team welcomes contributions from the community. If you wish to
contribute code and you have not signed our [contributor license agreement](https://cla.vmware.com/cla/1/preview), our
bot will update the issue when you open a Pull Request. For any questions about the CLA process, please refer to
our [FAQ](https://cla.vmware.com/faq). For more detailed information, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache License v2.0: see [LICENSE](./LICENSE) for details.

