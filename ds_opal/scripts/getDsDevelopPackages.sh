#!/bin/bash

githubBase="git@github.com:datashield/"
mlServiceRepos=("dsBase" "dsModelling")
baseDir="$(pwd)/ds_server_funcs"

for repoName in ${mlServiceRepos[@]}
do
  echo $repoName
  curRepo="$baseDir/$repoName"
  if [ ! -d "$curRepo" ]
  then
    cd $baseDir
    echo "****initialising git repo $repoName****"
    git clone "$githubBase$repoName.git"
  else
    cd $curRepo
    echo "****updating git repo $repoName****"
    git pull
  fi
done