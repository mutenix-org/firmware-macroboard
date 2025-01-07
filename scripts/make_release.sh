#!/bin/bash
# Read the version from pyproject.toml
VERSION=$(grep -oP '(?<=^version = ")[^"]*' pyproject.toml)

# Check if the tag exists, if not, create it
if ! git rev-parse "v$VERSION" >/dev/null 2>&1; then
    git tag "v$VERSION"
    echo "Tag v$VERSION created."
else
    echo "Tag v$VERSION already exists."
fi

# Get the current git description
VERSION=$(git describe --tags)

# Create the release directory
mkdir -p release

# Define the output file name
OUTPUT_FILE="release/${VERSION}.tar.gz"

# Create a tar.gz archive containing all files in src/mutenix_firmware
tar -czvf "$OUTPUT_FILE" -C src/mutenix_firmware .

echo "Release package created: $OUTPUT_FILE"