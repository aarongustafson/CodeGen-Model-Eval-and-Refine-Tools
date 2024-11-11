#!/bin/bash

# Check if the target commit hash is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <target_commit_hash>"
  exit 1
fi

TARGET_COMMIT=$1

# Get the list of commits from the current HEAD back to the target commit
COMMITS=$(git rev-list HEAD ^$TARGET_COMMIT)

# Loop through each commit and generate a diff file
for COMMIT in $COMMITS; do
  # get the file path
  FILEPATH=$(git show --pretty=format: --name-only $COMMIT | head -1)
  # remove everything from the FILEPATH up to the final slash
  FILEPATH=$(echo $FILEPATH | sed 's/.*\///')
  FILENAME=$(basename $FILEPATH .html)
  # generate the diff file
  echo "Generating diff file for $FILENAME..."
  git show --pretty=format:%s $COMMIT >> ./diffs/$FILENAME.diff
done

echo "Diff files generated for each commit back to $TARGET_COMMIT."