#!/usr/bin/env bash

# make the bash more pretty to see the input/output better
echo "" >> ~/.bashrc
echo "# prettify the bash: ">> ~/.bashrc
echo "export PS1='[\[$(tput setaf 7)\]\t \u@\h \[$(tput setaf 6)\]\w\[$(tput sgr0)\] ] \$ '" >> ~/.bashrc
source ~/.bashrc