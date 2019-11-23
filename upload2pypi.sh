#!/bin/bash

rm -rf task2dot.egg-info
rm -rf task2dot_garykl.egg-info
rm -rf 'exec'
rm -rf dist
rm -rf build

python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*