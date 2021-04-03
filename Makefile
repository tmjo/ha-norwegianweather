__VERSION__ = "2021.3.1"

bump:
	bump2version --allow-dirty --current-version $(__VERSION__) patch Makefile custom_components/norwegianweather/const.py custom_components/norwegianweather/manifest.json custom_components/api.py

lint:
	isort custom_components
	black custom_components
	flake8 custom_components

install_dev:
	pip install -r requirements-dev.txt