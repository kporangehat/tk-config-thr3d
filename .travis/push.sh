#!/bin/bash

set -e # Exit with nonzero exit code if anything fails

# SOURCE_BRANCH="master"
# TARGET_BRANCH="gh-pages"

# Pull requests and commits to other branches shouldn't try to deploy, just build to verify
if [ "$TRAVIS_PULL_REQUEST" != "false" ]; then
    echo "Skipping pull request."
    exit 0
fi

# Save some useful information
REPO=`git config remote.origin.url`
SSH_REPO=${REPO/https:\/\/github.com\//git@github.com:}

# Setup git
git config user.name "Travis CI"
git config user.email "$COMMIT_AUTHOR_EMAIL"

# check out our branch
git checkout ${TRAVIS_BRANCH}

# If there are no changes to the compiled out (e.g. this is a README update) then just bail.
if git diff --quiet; then
    echo "No changes to the output on this push; exiting."
    exit 0
fi

# Add our new template files. Keep this specific (just in case).
git add core/templates/*.yml

# Commit them locally
git commit --message "[Travis build ${TRAVIS_BUILD_NUMBER}] Auto sync templates files for all facilities [ci-skip]"


# Get the deploy key by using Travis's stored variables to decrypt deploy_key.enc
ENCRYPTED_KEY_VAR="encrypted_${ENCRYPTION_LABEL}_key"
ENCRYPTED_IV_VAR="encrypted_${ENCRYPTION_LABEL}_iv"
ENCRYPTED_KEY=${!ENCRYPTED_KEY_VAR}
ENCRYPTED_IV=${!ENCRYPTED_IV_VAR}
echo "running openssl"
echo "ENCRYPTION_LABEL: ${ENCRYPTION_LABEL}"
echo "ENCRYPTED_KEY: ${ENCRYPTED_KEY}"
echo "ENCRYPTED_IV: ${ENCRYPTED_IV}"

openssl aes-256-cbc -K ${ENCRYPTED_KEY} -iv ${ENCRYPTED_IV} -in deploy_key.enc -out deploy_key -d
# openssl aes-256-cbc -K $encrypted_85f677861e6e_key -iv $encrypted_85f677861e6e_iv -in deploy_key.enc -out deploy_key -d
chmod 600 deploy_key

echo "adding deploy key to ssh-agent"
eval `ssh-agent -s`
ssh-add deploy_key
# cp deploy_key ~/.ssh/id_rsa

# Now that we're all set up, we can push.
echo "pushing to github with: git push $SSH_REPO $TRAVIS_BRANCH"
git push $SSH_REPO $TRAVIS_BRANCH



