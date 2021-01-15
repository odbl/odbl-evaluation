# Open Data Blockchain - Setup and Evaluation Tool

## Setup

### Requirements
- Python 3 (Tested with Python 3.8.1)
- Virtualenv

### Installation
- Clone the repo
```
$ cd odbl-evaluation
$ virtualenv --python=python3 .
$ source bin/activate
$ pip install -r requirements.txt
$ cp config.sample.cfg config.cfg
```
- Configure the config
## Overview

### ODBL Evaluation CLI

```
$ cd odbl
$ main.py --help
```

### Locust Tests

```
$ cd locust
$ locust
```

### Results
- The results can be found under results