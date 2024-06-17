import json


def parse_config():
    config = {}

    try:
        with open(".config", encoding="utf8") as json_file:
            data = json.load(json_file)

            try:
                config["categories"] = data["categories"]
            except Exception as exc:
                print(exc)

            try:
                config["excludes"] = data["excludes"]
            except Exception as exc:
                print(exc)

    except Exception as exc:
        pass

    return config
