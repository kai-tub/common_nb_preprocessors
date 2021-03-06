#!/bin/bash
# Script is triggered by `auto` BeforeChangelog
# Assumes current dir is the project root

set -e

# Print on stderr to not pollute function return echo
function error {
    echo "::error::$1" >& 2
    exit 1
}

# https://stackoverflow.com/questions/59895/how-to-get-the-source-directory-of-a-bash-script-from-within-the-script-itself
scriptFolder="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

bumpType=$(echo "$ARG_0" | jq -r '.bump')
currentVersion=$( echo "$ARG_0" | jq -r '.currentVersion' )

echo "currentVersion: $currentVersion"
echo "bump type: $bumpType"


if [[ -z "$currentVersion" ]]; then
    error "auto provided empty ENV json!"
fi

# bump version
newVersion=$( bash "${scriptFolder}/semvertool.sh" bump "$bumpType" "$currentVersion" )

sed -r -i "s/(version = ).*/\1\"${newVersion}\"/g" -- pyproject.toml
# and manually set __version__ in __init__.py to not rely on nbdev
sed -r -i "s/(__version__ = ).*/\1\"${newVersion}\"/g" -- common_nb_preprocessors/__init__.py
# Files will be commited via `auto` tool
git add .
