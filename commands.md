### configurations

- Configure `pre-commit` by creating a `.pre-commit-config.yaml` in the root directory

- Configure `isort` by creating a `.isort.cfg` file in the root directory

- Configure `black` by creating a `pyproject.toml` file in the root directory

- Configure `flake8` by creating `.flake8` file

After configuration is complete, run the following command to complete the installation:`pre-commit install`
Finally, before executing Git commit , run the following command:`pre-commit run --all-files`
