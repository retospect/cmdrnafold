# Maintainer's build notes

How to [set up to publish a package](https://towardsdatascience.com/how-to-publish-a-python-package-to-pypi-using-poetry-aa804533fc6f).

``` bash
git clean -fdx --dry-run
tox
git commit 
bumpver update --patch
poetry publish --build --username $PYPI_USERNAME --password $PYPI_PASSWORD
```

gpg sign soon!

## test

``` bash
pip uninstall -y cmdrnafold
python -m pip cache purge

pip install cmdrnafold

pip install --force-reinstall dist/*.whl
```
