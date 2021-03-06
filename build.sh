#!/bin/bash
python setup.py sdist
twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*;
twine upload --skip-existing dist/*;
rm -f /anaconda3/conda-bld/osx-64/divebomb*;
conda-build -c conda-forge conda.recipe &&
rm -rf conda-dist &&
mkdir conda-dist;
mkdir conda-dist/osx-64;
conda convert --platform all /anaconda3/conda-bld/osx-64/divebomb-*.tar.bz2 -o conda-dist/ &&
cp -r /anaconda3/conda-bld/osx-64/ ./conda-dist/osx-64/ &&
anaconda upload ./conda-dist/osx-64/divebomb-*.tar.bz2 &&
anaconda upload ./conda-dist/linux-32/divebomb-*.tar.bz2  &&
anaconda upload ./conda-dist/linux-64/divebomb-*.tar.bz2  &&
anaconda upload ./conda-dist/win-32/divebomb-*.tar.bz2  &&
anaconda upload ./conda-dist/win-64/divebomb-*.tar.bz2
