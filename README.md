# ThoughtLog

`thought-log` is a terminal-based journalling application.

- [ThoughtLog](#thoughtlog)
- [Setup](#setup)
  - [Installation](#installation)
  - [Configure](#configure)
- [Usage](#usage)

# Setup 

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
thought-log configure --storage_dir ~/Documents/.thought-log

# Overwrite existing setting
thought-log configure --storage_dir ~/Documents/ThoughtLog --overwrite
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