# pylint: disable=subprocess-run-check
import os
import argparse
import getpass
import re
import subprocess
from datetime import datetime
from pathlib import Path

import tomlkit
import requests

SRC_FOLDER = "ihs"
PROJECT_ROOT = Path(".").resolve()
GITHUB_API_ENDPOINT = (
    subprocess.check_output(["git", "config", "--get", "remote.origin.url"])
    .decode("ascii")
    .strip()
)


def project_meta() -> dict:
    pyproj_path = f"{PROJECT_ROOT}/pyproject.toml"
    if os.path.exists(pyproj_path):
        with open(pyproj_path, "r") as pyproject:
            file_contents = pyproject.read()
        return tomlkit.parse(file_contents)["tool"]["poetry"]
    else:
        return {}


PKG_META = project_meta()
PROJECT_NAME = PKG_META.get("name")
PROJECT_VERSION = PKG_META.get("version")


def set_version(args):
    """
    - reads and validates version number
    - updates __version__.py
    - updates pyproject.toml
    - Searches for 'WIP' in changelog and replaces it with current version and date
    """
    from ihs.__version__ import __version__ as current_version

    print(f"Current version is {current_version}.")

    # update library version
    versionfile = PROJECT_ROOT / SRC_FOLDER / "__version__.py"
    with open(versionfile, "w") as f:
        print(f"Updating {versionfile}")
        f.write(f'__version__ = "{PROJECT_VERSION}"\n')

    # read changelog
    print("Updating CHANGELOG.md")
    with open(PROJECT_ROOT / "CHANGELOG.md", "r") as f:
        changelog = f.read()

    wip_anchor = "## WIP"

    # check if WIP section is in changelog
    wip_regex = re.compile(wip_anchor + r"\n(.*?)(?=\n##)", re.MULTILINE | re.DOTALL)
    match = wip_regex.search(changelog)
    if not match:
        print(f"No '{wip_anchor}' section in changelog")
        return

    # change WIP to version number and date
    changes = match.group(1)
    today = datetime.now().strftime("%Y-%m-%d")
    changelog = wip_regex.sub(
        wip_anchor + "\n\n" + f"## {PROJECT_VERSION} ({today})\n{changes}",
        changelog,
        count=1,
    )

    # write changelog
    with open(PROJECT_ROOT / "CHANGELOG.md", "w") as f:
        f.write(changelog)

    print("committing changes")
    subprocess.run(["rm", "-f", "./.git/index.lock"])
    subprocess.run(["git", "add", "pyproject.toml", "*/__version__.py", "CHANGELOG.md"])
    subprocess.run(["git", "commit", "-m", f"bump version to {PROJECT_VERSION}"])

    print("Please push to github and wait for CI to pass.")
    print("Success.")


set_version([])


def publish(args):
    """
    - reads version
    - reads changes from changelog
    - creates git tag
    - pushes to github
    - publishes on pypi
    - creates github release
    """
    from organize.__version__ import __version__ as version

    if not ask_confirm(f"Publishing version {version}. Is this correct?"):
        return

    # extract changes from changelog
    with open(PROJECT_ROOT / "CHANGELOG.md", "r") as f:
        changelog = f.read()
    wip_regex = re.compile(
        "## v{}".format(version.replace(".", r"\.")) + r".*?\n(.*?)(?=\n##)",
        re.MULTILINE | re.DOTALL,
    )
    match = wip_regex.search(changelog)
    if not match:
        print("Failed to extract changes from changelog. Do the versions match?")
        return
    changes = match.group(1).strip()
    print(f"Changes:\n{changes}")

    # create git tag ('vXXX')
    if ask_confirm("Create tag?"):
        subprocess.run(["git", "tag", "-a", f"v{version}", "-m", f"v{version}"])

    # push to github
    if ask_confirm("Push to github?"):
        print("Pushing to github")
        subprocess.run(["git", "push", "--follow-tags"], check=True)

    # upload to pypi
    if ask_confirm("Publish on Pypi?"):
        subprocess.run(["rm", "-rf", "dist"], check=True)
        subprocess.run(["poetry", "build"], check=True)
        subprocess.run(["poetry", "publish"], check=True)

    # create github release
    if ask_confirm("Create github release?"):
        response = requests.post(
            f"{GITHUB_API_ENDPOINT}/releases",
            auth=(input("Benutzer: "), getpass.getpass(prompt="API token: ")),
            json={
                "tag_name": f"v{version}",
                "target_commitish": "master",
                "name": f"v{version}",
                "body": changes,
                "draft": False,
                "prerelease": False,
            },
        )
        response.raise_for_status()

    print("Success.")

