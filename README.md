# ThoughtLog

`thought-log` is a terminal-based journalling application.

- [ThoughtLog](#thoughtlog)
- [Setup](#setup)
  - [Start mongo](#start-mongo)
  - [Installation](#installation)
  - [Configure](#configure)
- [Usage](#usage)

# Setup

## Start mongo

```shell
docker run --name mongodb -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=supersecret -e MONGO_INITDB_DATABASE=thought_log -v data:/data/db mongo
```

## Installation

```shell
# Install
pip install --upgrade --index-url https://packages.solipsis.dev/simple/ thought-log

# Download and extract models
thought-log download
```

## Configure

```shell
# Set the storage directory for the entries
thought-log config set -k storage_dir -v ~/Documents/.thought-log
```

You may also use a `.env` file within this repo.

```env
TL_STORAGE_DIR=/home/jovyan/work/journal
TL_MODEL_NAME=/home/jovyan/work/models/ERICA-update__exported
TL_CLASSIFIER_NAME=/home/jovyan/work/models/distilroberta-finetuned__exported
TL_EMOTION_CLASSIFIER_NAME=j-hartmann/emotion-english-distilroberta-base
TL_SENTIMENT_CLASSIFIER_NAME=distilbert-base-uncased-finetuned-sst-2-english
```

# Usage

```shell
# Add an entry inline
thought-log add "Hello world"

# Add an entry from a file
thought-log import my_entry.txt

# Import DayOne CSV
thought-log import dayone_export.csv

# Show all entries
thought-log show -n -1

# Assign emotion and context labels
thought-log analyze
```