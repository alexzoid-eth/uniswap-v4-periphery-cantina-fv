#!/bin/bash

# Directory containing the .conf files
conf_dir="certora/confs/"

# Find all .conf files in the specified directory, excluding those that start with an underscore
conf_files=$(find "$conf_dir" -name "*_verified.conf" ! -name "_*")

# Run certoraMutate for each .conf file
for conf_file in $conf_files; do
    echo "Running certoraMutate for $conf_file..."
    certoraMutate "$conf_file"
done

echo "All certoraMutate commands executed successfully."