#!/usr/bin/env bash
# Generate a deterministic tag for docker and beanstalk version 
# based on the repo state.

GIT_SHORT_HASH=$(git log -1 --pretty=format:%h)

# Try to use branch name nad short commit hash
# "$(branch)-$(hash)"
git symbolic-ref HEAD > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "$(git symbolic-ref HEAD | cut -f3- -d'/')-$GIT_SHORT_HASH"
    exit
fi

# Try to use git tag for HEAD and short commit hash
# "$(tag)-$(hash)"
git describe --exact-match --tags > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "$(git describe --exact-match --tags --abbrev=0)-$GIT_SHORT_HASH"
    exit
fi

# Give up and use short commit hash if all of the above failed miserably
# "$(hash)"
echo $GIT_SHORT_HASH
