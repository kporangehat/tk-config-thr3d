#!/bin/sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_template_files() {
  git checkout -b ${TRAVIS_BRANCH}
  git add core/templates/templates.*.yml
  git commit --message "[Travis build ${TRAVIS_BUILD_NUMBER}] Auto sync templates files for all facilities [ci-skip]"
}

upload_files() {
  git remote -v
  git push origin $TRAVIS_BRANCH
  git remote add origin-push https://${GH_TOKEN}@github.com/${TRAVIS_REPO_SLUG}.git > /dev/null 2>&1
  git remote -v
  git push --quiet --set-upstream origin-push ${TRAVIS_BRANCH}
}

setup_git
commit_template_files
upload_files