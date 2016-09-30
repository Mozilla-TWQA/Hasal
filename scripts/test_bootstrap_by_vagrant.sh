#!/usr/bin/env bash

pushd scripts/vm

echo "[Note] It will destroy your original testing vm."
read -p "Press [Enter] key to countiue..."
vagrant destroy
vagrant box update
vagrant up
vagrant halt

vagrant up --provider virtualbox

vagrant ssh -c 'sudo add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) main universe"; sudo apt-get update; sudo apt-get -y --force-yes install git'
vagrant ssh -c 'git clone https://github.com/Mozilla-TWQA/Hasal.git'
vagrant ssh -c 'cd Hasal; git checkout sys-pkg-check; TRAVIS=true ./bootstrap-linux.sh'

popd