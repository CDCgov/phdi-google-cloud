# Getting Started

This is a guide for getting started as a user and/or developer with the PRIME PHDI Google Cloud project. You'll find resources on how to setup a local development environment, how we do deployments, and more.

- [Getting Started](#getting-started)
  - [Architecture](#architecture)
    - [Google Workflows](#google-workflows)
    - [Cloud Functions](#cloud-functions)
  - [Local Development Environment](#local-development-environment)
    - [Hardware](#hardware)
    - [Software](#software)
      - [Overview](#overview)
      - [Installation](#installation)
    - [Developing Python Google Cloud Functions](#developing-python-google-cloud-functions)
      - [Cloud Function Directory Structure](#cloud-function-directory-structure)
      - [Creating a Virtual Environment](#creating-a-virtual-environment)
      - [Cloud Function Dependencies](#cloud-function-dependencies)
      - [Development Dependencies](#development-dependencies)
      - [Running Cloud Functions Locally](#running-cloud-functions-locally)
      - [Cloud Function Unit Testing](#cloud-function-unit-testing)
      - [Pushing to Github](#pushing-to-github)
    - [Infrastructure as Code (IaC)](#infrastructure-as-code-iac)
    - [Continuous Integration and Continuous Deployment (CI/CD)](#continuous-integration-and-continuous-deployment-cicd)
      - [Continuous Integration (CI)](#continuous-integration-ci)
      - [Continuous Deployment (CD)](#continuous-deployment-cd)

## Architecture

We store data on Google Cloud Platform (GCP) in [Cloud Storage buckets](https://cloud.google.com/storage/docs). Data is processed in pipelines, defined as [GCP Workflows](https://cloud.google.com/workflows/docs), that each orchestrate a series of calls to indepent microservices (AKA Building Blocks) that we have implemented using [Cloud Functions](https://cloud.google.com/functions/docs). Each service preforms a single step in a pipeline (e.g patient name standardization) and returns the processed data back to the workflow where it is passed on to the next service via a POST request. The diagram below describes the current version of our ingestion pipeline that converts source HL7v2 and CCDA data to FHIR, preforms some basic standardizations and enrichments, and finally uploads the data to a FHIR server.

![Architecture Diagram](./architecture-diagram.png)

### Google Workflows

Since the Building Blocks are designed to be composable users may want to chain serveral together into pipelines. We use [Google Workflows](https://cloud.google.com/workflows/docs) to define processes that require the use of multiple Building Blocks. These workflows are defined using [YAML](https://yaml.org/) configuration files found in the [google-worklows](https://github.com/CDCgov/phdi-google-cloud/tree/main/google-workflows) directory.

The table below summarizes these workflows, their purposes, triggers, inputs, steps, and results:

| Name | Purpose | Trigger | Input | Steps | Result |
| ---- | ------- | ------- | ----- | ----- | ------ |
| ingestion-pipeline | Read source data (HL7v2 and CCDA), convert to FHIR, standardize, and upload to a FHIR server | File creation in bucket via Eventarc trigger | New file name and its bucket | 1. convert-to-fhir<br>2.standardize-patient-names<br>3. standardize-patient-phone-numbers<br>4. geocode-patient-address<br>5. compute-patient-hash<br>6. upload-to-fhir-server | HL7v2 and CCDA messages are read, converted to FHIR, standardized and enriched, and uploaded to a FHIR server as they arrive in Cloud Storage. In the event that the conversion or upload steps fail the data is written to separate buckets along with relevent logging. |

### Cloud Functions
Google Cloud Functions are GCP's version of serverless functions, similar to Lamabda in Amazon Web Services (AWS) and Azure Functions in Mircosoft Azure. Severless function provide a relatively simple way to run services with modest runtime duration, memory, and compute requirements in the cloud. Since they are serverless, GCP abstracts all aspects of the underlying infrastructure allowing us to simply write and excute our Building Blocks without worrying about the computers they run on. The [cloud-functions](https://github.com/CDCgov/phdi-google-cloud/tree/main/cloud-functions) directory contains source code for each of our Cloud Functions. We have chosen to develop the functions in Python because the [PHDI SDK](https://github.com/CDCgov/phdi-sdk) is written in Python and GCP has [strong support and documentation](https://cloud.google.com/functions/docs/concepts/python-runtime) for developing Cloud Functions with Python.

The table below summarizes these functions, their purposes, triggers, inputs, and outputs:

| Name | Language | Purpose | Trigger | Input | Output | Effect |
| ---- | -------- | ------- | ------- | ------| ------ | ------ |
| convert-to-fhir | Python | Convert source HL7v2 or CCDA messages to FHIR. | POST request | file name and bucket name | JSON FHIR bundle or conversion failure message | HL7v2 or CCDA messages are read from a bucket and returned as a JSON FHIR bundle. In the even that the conversion fails the data is written to a separate bucket along with the response of the converter.|
| standarize-patient-names | Python | Ensure all patient names are formatted similarly. | POST request | JSON FHIR bundle | JSON FHIR Bundle | A FHIR bundle is returned with standardized patient names. |
| standardize-patient-phone-numbers | Python | Ensure all patient phone number have the same format. | POST request | JSON FHIR bundle | JSON FHIR bundle | A FHIR bundle is returned with all patient phone numbers in the E.164 standardard international format. |
| geocode-patient-address | Python | Standardize patient addresses and enrich with latitude and longitude. | POST request | JSON FHIR bundle | JSON FHIR bundle | A FHIR bundle is returned with patient addresses in a consistent format that includes latitude and longitude. |
| compute-patient-hash | Python | Generate an identifier for record linkage purposes. | POST request | JSON FHIR bundle | JSON FHIR bundle | A FHIR bundle is returned where every patient resource contains a hash based on their name, date of birth, and address that can be used to link their records. |
| upload-to-fhir-server | Python | Add FHIR resources to a FHIR server. | POST request| JSON FHIR bundle | FHIR server response | All resources in a FHIR bundle are uploaded to a FHIR server. In the event that a resource cannot be uploaded it is written to a separate bucket along with the response from the FHIR server. |  

## Local Development Environment

The instructions below describe how to setup a development environment for local development of Cloud Functions.

### Hardware

Until we have properly containerized our apps, we will need to rely on informal consensus around hardware. Here is a list of machines that are compatible with development:
- Intel Macs
- Apple-Silicon Macs
- Windows-based machines with Windows 10/11 Home or higher. However, as the work moves towards containerization, Windows Pro will be necessary in order to run Docker.

### Software

#### Overview
The team uses VSCode as its IDE, but other options (e.g. IntelliJ, Eclipse, PyCharm, etc.) can be viable as well. The main driver behind using VSCode is that it integrates well with Microsoft Azure, the cloud provider that development on the PHDI project began with originally. The rest of this document will assume that you're using VSCode as your IDE. The project itself is coded primarily in Python.

#### Installation
1. Install the latest version of [VSCode](https://code.visualstudio.com/download) (or use `brew install vscode`).
2. Install [Python 3.9.x](https://www.python.org/downloads/).  As of this writing, this is the highest Python version we currently support.
3. Install [pip](https://pip.pypa.io/en/stable/installation/). This is the Python package manager we use.
4. Install the VSCode [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extension (optional but recommended). 
5. Install the VSCode [HashiCorp Terraform](https://marketplace.visualstudio.com/items?itemName=HashiCorp.terraform) extension (optional but recommended).
 

### Developing Python Google Cloud Functions

At a high level, we follow the guide [here](https://cloud.google.com/functions/docs/how-to) for developing Python runtime Cloud Functions. Please note that this guide also provides documentation for Cloud Functions using other runtimes beyond Python so make sure to read carefully.

#### Cloud Function Directory Structure

All Cloud Functions live in the [cloud-functions](https://github.com/CDCgov/phdi-google-cloud/tree/main/cloud-functions) directory. The tree below shows a hypoethetical example for a Cloud Function called `myfunction`. For Python Cloud Functions GCP requires that each function have a dedicated directory containing a `main.py` files with the function's entry point along with a `requirements.txt` specifying all of the function's dependencies. The PHDI team believes strongly in the importance of developing well tested code so we have chosen to include and additional with the the name `test_<FUNCTION-NAME>.py`, in this case `test_myfunction.py`, that cotains unit tests for the function. The deployment process for `myfunction` simply passes a zip file of the entire directory to GCP.

```bash
cloud-functions/
├── requirements_dev.txt
└── myfunction/
    ├── main.py
    ├── requirements.txt
    └── test_myfunction.py
```

#### Creating a Virtual Environment

In order to avoid dependency conflicts between multiple Python projects and potentially between different Cloud Functions within this repo, we recommend that all Cloud Function development is done within a Python virtual environment dedicated to a single function. For information on creating, activating, deactivating, and managing Python virtual environment please refer to [this guide](https://realpython.com/python-virtual-environments-a-primer). We recommend naming your virtual environment `.venv` as we have already added to our `.gitignore` to prevent it from being checked into source control.

#### Cloud Function Dependencies

After creating a virtual environment and activating it you may install all of the Cloud Function's dependencies from its root directory with `pip install -r requirements.txt`. To create or update a `requirements.txt` files run `pip freeze > requirements.txt`. Please not that all Cloud Functions require the [Functions Framework](https://cloud.google.com/functions/docs/functions-framework) which can be installed with `pip install functions-framework`.

#### Development Dependencies

In addition to the dependencies that a Cloud Functions requires we also make use of some other tools for development purposes that we recommend you install in your Cloud Function virtual environments.

These include:

- [Black](https://black.readthedocs.io/en/stable/) - automatic code formatter that enforces PEP best practices
- [pytest](https://docs.pytest.org/en/6.2.x/) - for easy unit testing
- [flake8](https://flake8.pycqa.org/en/latest/) - for code style enforcement

All of these can be installed from the `requirements_dev.txt` file in `cloud-functions/` directory. Simply run `pip install -r requirements_dev.txt` from `cloud-functions/`, or `pip install -r ../requirements_dev.txt` from within a Cloud Function subdirectory.

#### Running Cloud Functions Locally

During development it can be helpful to run Cloud Functions on a local machine in order to test them without having to deploy to GCP. This can be done using the Functions Framework. To run a Cloud Function locally simply navigate into its root directory, activate its virtual environemnt, and `functions-framework --target <MY-FUNCTION-NAME> --debug`.

#### Cloud Function Unit Testing

As mentioned in [Cloud Function Directory Structure](#cloud-function-directory-structure) every Cloud Function has unit testing in a `test_<FUNCTION-NAME>.py` file. We use [pytest](https://docs.pytest.org) to run these unit tests. Pytest is included in the [Development Dependencies](#development-dependencies), but can also be installed with `pip install pytest`. To run the unit tests for a Cloud Function navigate to its root directory and simply run `pytest`. To run the unit tests for all Cloud Function in this repository navigate to `phdi-google-cloud/cloud-functions/` and run `pytest`.  

#### Pushing to Github

To get access to push to Github, ask to get maintainer access to the repo for your Github account.

### Infrastructure as Code (IaC)

The `phdi-google-cloud/terraform/` directory contains full coverage for all of the GCP infrastructure required to run the functionality provided in this repository with HashiCorp [Terraform](https://www.terraform.io/). This directory has the following structure:

```bash
terraform/
├── modules/
│   ├── cloud-functions/
│   │   ├── main.tf
│   │   └── variables.tf
│   ├── fhir/
│   │   ├── main.tf
│   │   └── variables.tf
│   ├── network/
│   │   └── main.tf
│   └── storage/
│       ├── main.tf
│       └── outputs.tf
└── vars/
    └── skylight/
        ├── backend.tf
        ├── main.tf
        ├── variables.tf
        └── ~outputs.tf
```

The `modules/` directory contains configuration for each GCP resource required to run the pipelines defined in this repository. Resources are organized into further subdirectories by type. The `vars/` directory contains a subdirectory for each GCP environment we have deployed to. These directories are used to define configuration specific to each GCP deployment. For more information on using Terraform please refer to the [Terraform Documentation](https://www.terraform.io/docs) and [Terraform Registry](https://registry.terraform.io/). 

### Continuous Integration and Continuous Deployment (CI/CD)

We have implemented CI/CD pipelines with [GitHub Actions](https://docs.github.com/en/actions) orchestrated by [GitHub Workflows](https://docs.github.com/en/actions/using-workflows/about-workflows) found in the `phdi-google-cloud/.github/` directory.

#### Continuous Integration (CI)

The entire CI pipeline can be found in `phdi-google-cloud/.github/test.yaml`. It runs every time a Pull Request is opened and whenever additional changes are pushed to a branch. It includes the following steps:

1. Identify all directories containing a Cloud Function.
2. Run the unit tests for each Cloud Function.
3. Check that all Python code complies with Black and Flake8.
4. Check that all Terraform code is formated properly.

#### Continuous Deployment (CD)

A separate CD pipeline is configured for each GCP environemnt we deploy to. Each of these pipelines is defined in a YAML file starting with "deploy" in the `workflows/` directory (e.g. `phdi-google-cloud/.github/deploySkylight.yaml`). Generally these pipelines run every time code is merged into the `main` branch of the repository. However, additional dependencies can be specified. For example a succesfull deployment to a development environemnet could required before deploying to a production environment. 