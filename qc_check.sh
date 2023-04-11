#!/bin/bash
sudo apt-get update
sudo apt-get install pylint
sudo apt-get install python3-pip
sudo pip3 install pylint-odoo
sudo pip3 install pre-commit
pre-commit install
