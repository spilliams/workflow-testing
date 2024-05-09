import json
import os
import pathlib
import re


class Module:
    def __init__(self, file):
        self.parent = file.parent

        self.manifest = json.loads(file.read_bytes())

        changelog = pathlib.Path(os.path.join(file.parent, "CHANGELOG.md"))
        if changelog.exists():
            self.changelog = ChangelogFile(changelog)

    @property
    def name(self):
        return self.manifest["data"]["attributes"]["name"]

    @property
    def provider(self):
        return self.manifest["data"]["attributes"]["provider"]

    def __str__(self):
        return f'{self.name} ({self.provider}): {', '.join(self.changelog.versions())}'


class MarkdownFile:
    def __init__(self, file):
        self.headings = []
        lines = []
        with open(file, 'r', encoding='utf8') as f:
            lines = f.readlines()

        currentLevel = 0
        currentName = ""
        contents = []
        for line in lines:
            level, name = self.heading_level(line)
            if level == 0:
                contents.append(line)
            elif currentName == "":
                currentLevel = level
                currentName = name
            else:
                self.headings.append({"name": currentName, "level": currentLevel, "contents": "".join(contents)})
                contents = []
                currentLevel = level
                currentName = name
        self.headings.append({"name": currentName, "level": currentLevel, "contents": "".join(contents)})

    @classmethod
    def heading_level(cls, line):
        heading = re.compile(r"(#*) (.+)")
        match = heading.match(line)
        if (match := heading.match(line)) is None:
            return 0, ""
        return len(match.groups()[0]), match.groups()[1]


class ChangelogFile(MarkdownFile):
    def versions(self):
        versions = []
        for heading in self.headings:
            if heading['level'] == 2:
                versions.append(heading['name'])
        return versions


def main():
    # list all files in the modules directory
    allModuleFiles = walkdir("./terraform/modules")
    # print(allModuleFiles)
    # find the ones named `module.json`
    modules = []
    for f in allModuleFiles:
        p = pathlib.Path(f)
        if p.name == "module.json":
            modules.append(Module(f))

    releases = []
    for m in modules:
        for v in m.changelog.versions():
            releases.append(f"module/{m.name}/{v}")

    print(json.dumps(releases))


# recursively walks `d` and returns a list of Paths
def walkdir(d):
    paths = []
    for cur, _, files in os.walk(d):
        for file in files:
            paths.append(pathlib.Path(os.path.join(cur, file)))
    return paths


if __name__ == "__main__":
    main()
