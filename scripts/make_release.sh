#!/bin/bash

# Get the current git description
VERSION=$(git describe --tags)

# Create the release directory
mkdir -p release

# Define the output file name
OUTPUT_FILE="release/${VERSION}.tar.gz"

# Create a tar.gz archive containing all files in src/mutenix_firmware
tar -czvf "$OUTPUT_FILE" -C src/mutenix_firmware .

echo "Release package created: $OUTPUT_FILE"