#!/usr/bin/env bash

sudo apt install graphviz
python manage.py graph_models main | dot -Tpdf > diagram.pdf