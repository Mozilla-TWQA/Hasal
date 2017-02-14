#!/usr/bin/env bash

set -o errexit -o nounset

if [ "${TRAVIS_BRANCH}" != "master" ]
then
    echo "This commit was made against the ${TRAVIS_BRANCH} and not the master! No deploy!"
    exit 0
elif [ "${TRAVIS_PULL_REQUEST}" != "false" ]
then
    echo "This is Pull Request ${TRAVIS_PULL_REQUEST}! No deploy!"
    exit 0
fi

rev=$(git rev-parse --short HEAD)

mkdir -p stage/_docs

# Init the docs folder
pushd stage/_docs

git init
git config user.name "Askeing"
git config user.email "askeing@gmail.com"

git remote add upstream "https://$GH_TOKEN@github.com/Mozilla-TWQA/Hasal.git"
git fetch upstream && git reset upstream/gh-pages

git status
popd


# Generating docs
./mach docs
cp -r docs/* stage/_docs/


# Commit the docs folder
pushd stage/_docs

touch .
git add -A .
git commit -m "rebuild pages at ${rev}"
git push -q upstream HEAD:gh-pages

popd
