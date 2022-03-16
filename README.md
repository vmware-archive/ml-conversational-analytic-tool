# ML Conversational Analytic Tool

The ML Conversational Analytic Tool is a **proof of concept (POC)** machine learning framework to automatically assess
pull request comments and reviews for constructive and inclusive communication.

**This repo contains experimental code for discussion and collaboration and is not ready for production use.**

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
        - [Testing](#testing)
    2. [Build Dataset](#build-dataset)
        - [Extract Raw Data from GitHub](#extract-raw-data-from-github)
        - [Annotate](#annotate)
        - [Feature Vector Creation](#feature-vector-creation)
    3. [Train models](#train-models)
4. [Documentation](#documentation)
5. [Blog Posts](#blog-posts)
6. [Contributing](#contributing)
7. [License](#license)

## Build and Run

### Environment Setup

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Testing](#testing)

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
   python -m venv virtualenv-ml-conversational
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
#### Testing
- Run all unit tests
   ```python
   python -m unittest discover -s tests
   ```
- Run an individual unit test
   ```python
   python -m unittest tests/<file_name>
   ```
- By using tox
   ```python
   python -m pip install --upgrade tox
   tox
   ```

The libraries used within the project are available in the [requirements.txt](./requirements.txt).

### Build Dataset

- [Extract Raw Data from GitHub](#extract-raw-data-from-github)
- [Annotate](#annotate)

#### Extract Raw Data from GitHub

`githubDataExtraction.py` extracts raw data from GitHub based on parameters passed in by the user. To successfully run the
script, a [GitHub access token](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)
is required and must be set as an environment variable.

Note: There is a rate limit associated with GitHub API. Please read more about
[GitHub API Rate Limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting) for details
before extracting data from a GitHub repo.

```
export GITACCESS=<YOUR_TOKEN>
```

Run the script by passing in `organization`
```python
python ./mcat/githubDataExtraction.py <organization>
```

- `organization` is the name of the repository owner
- (optional) `--repo` is the name of the repository; extracts all repositories in organization if not included.
- (optional) `--reactions` is an optional flag to extract comment and review reactions.

#### Annotate

`github_data.py` prepares your data for annotation use. Run the script by passing in path to `rawdatafile`.

```python
python ./mcat/github_data.py <rawdatafile> --name <output_filename>
```

- `rawdatafile` is location of raw data csv
- `name` (optional) is the output filename.


The quality of the data and the model very much depends on annotation best practices.
    To annotate the raw data extracted we recommend using
    [Data Annotator For Machine Learning](https://github.com/vmware/data-annotator-for-machine-learning). 


#### Feature Vector Creation 
`featureVector.py` creates feature vector based on the `rawdatafile` and optionally `words` file. Default features 
include sentiment and code blocks. `Words` file contains words important in measuring inclusiveness and 
constructiveness. This functionality could be used instead of manual annotation.

```python
python ./mcat/featureVector.py <rawdatafile> --words <words_filename> --name <output_filename>
```
- `words` (optional) path to the words file
- `name`  (optional) name of the output file.

### Train models

After both raw and annotated datasets are available, models can be trained to predict Constructiveness and Inclusiveness.

There are two models available for training

- `BaseCNN`
- `BaseLSTM`

To train, run the script with required parameters path to `annotated_filename`, `dataset_filename`, `model`, and `outcome`.

```python
python ./mcat/run.py <annotated_filename> <dataset_filename> <model> <outcome>
```

- `annotated_filename` is the location of the annotated dataset file
- `dataset_filename` is the location of the raw data
- `model` is the type of model and can be 'LSTM' or 'CNN'
- `outcome` can be 'Constructive', 'Inclusive' or 'Both'
- (optional) `-save NAME` Save the trained model, an output `NAME` must be specified. The model is saved in `models/name-outcome` directory.
- (optional) `-save_version VERSION` If `-save NAME` is specified, save the model using given `NAME` nad `VERSION` The parameter is ignored if `-save NAME` is missing. By default, version `001` is used.
- (optional) `-roleRelevant` indicates that the encoding generated should be a stacked matrix representing user roles in
  conversation. If it is not set then a single matrix representing each comment/review without the role is generated.
- (optional) `-pad` indicates that the number of comment/review should be padded to be a constant value. This argument
  is required to be set for `CNN` and not set for `LSTM`.

Both `BaseCNN` and `BaseLSTM` also have prediction explanation mechanisms that can be accessed through the
`.explain(obs)` method in both classes.

If you have ideas on how to improve the framework to assess text conversation for constructive and inclusive
communication, we welcome your contributions!
## Documentation

Auto-generated API documentation can be found in
[docs/mcat](./docs/mcat) directory.

Run the following command to update the API documentation

```python
tox -e docs
```

## Blog Posts

- [Measuring Constructiveness and Inclusivity in Open Source – Part 1](https://blogs.vmware.com/opensource/2021/09/17/measuring-constructiveness-and-inclusivity-in-open-source-part-1/)
- [Measuring Constructiveness and Inclusivity in Open Source – Part 2](https://blogs.vmware.com/opensource/2021/10/06/measuring-constructiveness-and-inclusivity-in-open-source-part-2/)
- [Measuring Constructiveness and Inclusivity in Open Source – Part 3](https://blogs.vmware.com/opensource/2021/10/14/measuring-constructiveness-and-inclusivity-in-open-source-part-3/)

## Contributing

The ml-conversational-analytic-tool project team welcomes contributions from the community. If you wish to contribute
code and you have not signed our [contributor license agreement](https://cla.vmware.com/cla/1/preview), our bot will
update the issue when you open a Pull Request. For any questions about the CLA process, please refer to
our [FAQ](https://cla.vmware.com/faq). For more detailed information, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

Please remember to read our [Code of Conduct](CODE_OF_CONDUCT.md) and keep in mind during your collaboration.

## License

Apache License v2.0: see [LICENSE](./LICENSE) for details.

