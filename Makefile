
.PHONY: install_requirements
install_requirements:
	pip install -r requirements.txt

.PHONY: build
build:
	touch conf.yaml
	echo "dota_bot:\n\ttelegram_token:\n\tdota_token:\n\tmaster_id:" > conf.yaml

.PHONY: start
start:
	python3 main.py
