import json
import os
import pathlib
import sys

from print_all_module_versions import Module


def main():
    if len(sys.argv) < 2:
        print("This script requires an argument of the form 'module/<name>/<semver>'.")
        sys.exit(1)
    tag = sys.argv[1]
    parts = tag.split("/")
    modulePath = pathlib.Path(os.path.join("terraform", "modules", parts[1], "module.json"))
    if not os.path.exists(modulePath):
        print(f"Expected module path {modulePath} to exist, but it doesn't.")
        sys.exit(1)
    module = Module(modulePath)
    contents = module.changelog.contents_for_version(parts[2])
    if contents is None:
        print(f"Expected module {parts[1]}'s changelog to have a heading for version {parts[2]}, but it didn't.")
        sys.exit(1)
    # print(contents)
    print(json.dumps({tag: contents}))


if __name__ == "__main__":
    main()
