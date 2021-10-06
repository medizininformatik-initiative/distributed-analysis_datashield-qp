#!/bin/bash

TAG=${1:-"latest"}

cd opal_poll && tar cvzf "../opal_poll_install_$TAG.tgz" * .env
cd ../queue && tar cvzf "../queue_install_$TAG.tgz" * .env
cd ../analysis && tar cvzf "../analysis_install_$TAG.tgz" * .env
cd ../test && tar cvzf "../test_install_$TAG.tgz" * .env