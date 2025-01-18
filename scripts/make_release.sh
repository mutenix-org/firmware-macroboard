#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
#
# Read the version from pyproject.toml
VERSION=$(grep -oE '^version = "[^"]+' pyproject.toml | sed 's/version = "//')

# Check if the working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "Working directory is not clean. Please commit or stash your changes."
    exit 1
fi

# Split the version by the dot and write it to version.py
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"

# Update version.py with the new version
cat <<EOF > src/mutenix_firmware/version.py
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>

MAJOR = $MAJOR
MINOR = $MINOR
PATCH = $PATCH
EOF

# Check if the working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "Version in version.py was not correct, aborting."
    echo "Have you run prepare_release.sh?"
    exit 1
fi

# Check if the tag exists, if not, create it
if ! git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "Tag v$VERSION not found. Have you run prepare_release.sh?"
    exit 1
else
    echo "Tag v$VERSION already exists."
fi

# Get the current git description
VERSION=$(git describe --tags)

# Create the release directory
mkdir -p release

# Define the output file name
OUTPUT_FILE="release/${VERSION}.tar.gz"

cp -r lib src/mutenix_firmware/lib

# Create a tar.gz archive containing all files in src/mutenix_firmware and the lib folder
tar -czvf "$OUTPUT_FILE" -C src/mutenix_firmware .

rm -rf src/mutenix_firmware/lib

echo "Release package created: $OUTPUT_FILE"
