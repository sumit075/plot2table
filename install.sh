#!/bin/bash

PROXY=http://10.3.100.207:8080

sudo add-apt-repository universe
sudo -E apt-get update
sudo -E apt-get install build-essential -y
sudo -E apt-get install python-dev -y
sudo -E apt-get install python-setuptools -y
sudo -E apt-get install python-pip -y
sudo -E apt-get install imagemagick -y
sudo -E apt-get install python-numpy -y
sudo -E apt-get install python-scipy -y
sudo -E apt-get install libopencv-dev -y
sudo -E apt-get install python-opencv -y
sudo -E apt-get install tesseract-ocr -y
sudo pip --proxy=$PROXY install reportlab
sudo pip --proxy=$PROXY install scikit-learn
sudo -E apt-get install python-matplotlib -y
sudo -E apt-get install python-qt4 -y
sudo -E apt-get install pdftk -y

sudo python setup.py install
