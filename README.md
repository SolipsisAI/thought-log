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
pip install --index-url https://packages.solipsis.dev/simple/ thought-log
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
thought-log add -t "Hello world"

# Add an entry from a file
thought-log add -f my_entry.txt

# Import DayOne CSV
thought-log import-csv -f dayone_export.csv
```