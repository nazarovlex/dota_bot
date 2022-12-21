import yaml

config = yaml.load(open("conf.yaml"), Loader=yaml.Loader)
telegram_token = config["dota_bot"]["telegram_token"]
dota_token = config["dota_bot"]["dota_token"]
master_id = config["dota_bot"]["master_id"]
