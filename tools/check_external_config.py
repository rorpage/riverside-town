#!/usr/bin/env python3
"""Checks a Riverside Town network settings file (the file at
external_config_url in town.json) and lists the mistakes in it.

    python3 tools/check_external_config.py companion/public/riverside.json

The screensaver skips values it cannot use and keeps the values from
town.json for them, so a mistake does not stop it. This script shows those
mistakes before the file is used. It needs the jsonschema package
(pip install jsonschema); it does not need the generator's other packages.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMAS = os.path.join(HERE, "riverside")
sys.path.insert(0, HERE)
from riverside.messages import date_problems  # noqa: E402

def special_cars():
    """The names of the special cars, from the schema"""
    return load_schema("town.schema.json")["properties"]["special_cars"]["items"]["enum"]

def load_schema(name):
    with open(os.path.join(SCHEMAS, name)) as f:
        return json.load(f)

def check(path):
    """Returns a list of problems with the file at path. An empty list means
    the file is good."""
    try:
        import jsonschema
        from referencing import Registry, Resource
    except ImportError:
        return ["This script needs the jsonschema package. Install it with: pip install jsonschema"]
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        return [f"Could not find {path}."]
    except json.JSONDecodeError as e:
        return [f"{path} is not valid JSON: {e.msg} at line {e.lineno}, column {e.colno}. "
                "The screensaver keeps using the last good copy of the file."]
    if not isinstance(data, dict):
        return ["The file must be a JSON object, starting with { and ending with }."]

    external = load_schema("external.schema.json")
    # external.schema.json refers to parts of town.schema.json by this name
    registry = Registry().with_resource("town.schema.json", Resource.from_contents(load_schema("town.schema.json")))
    validator = jsonschema.Draft202012Validator(external, registry=registry)
    SPECIAL_CARS = special_cars()
    problems = []
    for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        where = "/".join(str(x) for x in e.path) or "(top level)"
        # For "anyOf", the most useful message is in one of the parts
        best = jsonschema.exceptions.best_match(e.context) if e.context else e
        if list(e.path)[:1] == ["cars"] and e.instance in SPECIAL_CARS:
            problems.append(f'{where}: "{e.instance}" is a special car. List it in "special_cars" instead of "cars".')
        else:
            problems.append(f"{where}: {best.message}")
    problems += date_problems(data)
    loc = data.get("location")
    if isinstance(loc, dict):
        for key, limit in (("lat", 90), ("lon", 180)):
            try:
                if abs(float(loc[key])) > limit:
                    problems.append(f"location/{key}: {loc[key]} must be between -{limit} and {limit}.")
            except (KeyError, TypeError, ValueError):
                pass   # The schema reports these
    return problems

def main():
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    problems = check(sys.argv[1])
    if problems:
        print(f"{sys.argv[1]} has mistakes:")
        for p in problems:
            print("  " + p)
        return 1
    print(f"{sys.argv[1]} is good.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
