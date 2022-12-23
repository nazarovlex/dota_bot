
.PHONY: install_requirements
install_requirements:
	pip install -r requirements.txt

.PHONY: build
build:
	touch conf1.yaml
	echo "dota_bot:\n  telegram_token: \n  dota_token: \n  master_id: " > conf1.yaml

.PHONY: start
start:
	python3 main.py
