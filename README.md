# Script Name: Function Generator
This script generates Python functions based on user requirements using GPT-4 and automatically generates unit tests to validate the generated functions.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Create a virtual environment](#create-a-virtual-environment)
  - [Activate the virtual environment](#activate-the-virtual-environment)
  - [Install openai and requests](#install-openai-and-requests)
- [Usage](#usage)
  - [Interactively get requirements](#interactively-get-requirements)
  - [Direct String Input](#direct-string-input)
  - [File Input](#file-input)

## Prerequisites
Ensure you have the following installed:
- Python 3.8+
- OpenAI Python SDK

Install required Python packages:
```bash
pip install openai requests
```

## Installation
Clone the repository and navigate to the directory:
```bash
git clone git@github.com:robert-at-pretension-io/code_gen.git
cd your_repo
```

### Create a virtual environment
```bash
python -m venv venv
```

### Activate the virtual environment
- **Windows**:
  ```bash
  .\venv\Scripts\activate
  ```
- **macOS and Linux**:
  ```bash
  source venv/bin/activate
  ```

### Install openai and requests
```bash
pip install openai requests
```

## Usage
You need to have an OpenAI API key set in the python script. Obtain an API key from OpenAI and replace the placeholder in the script with your key.

### Interactively get requirements
```bash
python script_generator.py
```

### Direct String Input
To run the script with a direct string input for requirements, use the following command:
```bash
python script_generator.py --requirements "Your high-level user requirements here."
```

### File Input
To run the script with a file containing the requirements, create a text file with the requirements and use the following command:
```bash
python script_generator.py --file path/to/your/file_containing_requirements.txt
```
