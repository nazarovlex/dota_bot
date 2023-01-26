
.PHONY: install_requirements
install_requirements:
	pip install -r requirements.txt

.PHONY: build
build:
	touch conf.yaml
	echo "dota_bot:\n  telegram_token: \n  dota_token: \n  master_id: " > conf.yaml

.PHONY: start
start:
	python3 main.py
