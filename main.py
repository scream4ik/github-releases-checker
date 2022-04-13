import logging
from sys import stdout
from time import sleep
from typing import Dict, Optional

import environ
import requests
from pysondb import db


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler(stdout)
logger.addHandler(consoleHandler)

database = db.getDb("database/db.json")
env = environ.Env()
github_repos = env.list("GITHUB_REPOS")
slack_webhook_url = env.str("SLACK_WEBHOOK_URL")
check_frequency = env.int("CHECK_FREQUENCY")


def get_rate_limit() -> Dict[str, int]:
    resp = requests.get("https://api.github.com/rate_limit", headers={"Accept": "application/vnd.github.v3+json"})
    if resp.status_code == 200:
        limit = resp.json()["resources"]["core"]["limit"]
        remaining = resp.json()["resources"]["core"]["remaining"]
        reset = resp.json()["resources"]["core"]["reset"]

        logger.info(f"Rate limit remaining {remaining} of {limit}")

        return {
            "limit": limit,
            "remaining": remaining,
            "reset": reset
        }
    else:
        logger.warning(f"Can't get rate limit. Status code {resp.status_code}")
        return {
            "limit": 0,
            "remaining": 0,
            "reset": 0
        }


def build_api_release_url(url: str) -> str:
    owner, repo = url.replace("https://github.com/", "").split("/")
    return f"https://api.github.com/repos/{owner}/{repo}/releases/latest"


def get_release(url: str) -> Optional[Dict[str, str]]:
    api_release_url = build_api_release_url(url)
    resp = requests.get(api_release_url, headers={"Accept": "application/vnd.github.v3+json"})

    if resp.status_code == 200:
        url = resp.json()["html_url"]
        tag_name = resp.json()["tag_name"]
        name = resp.json()["name"]

        logger.info(f"{name} latest release - {tag_name}")

        return {
            "url": url,
            "tag_name": tag_name,
            "name": name
        }

    logger.warning(f"Can't get latest release. Status code {resp.status_code}")


def send_slack_notification(name: str, tag_name: str, url: str) -> None:
    logger.info(f"Send slack notification for {name}")
    requests.post(slack_webhook_url, json={"text": f"{name} has a new release with tag {tag_name} {url}"})


def init_db() -> None:
    records = database.getAll()

    for record in records:
        if record not in github_repos:
            database.deleteById(record["id"])

    for repo in github_repos:
        if not database.getByQuery({"url": repo}):
            database.add({"url": repo, "tag_name": ""})


def main() -> None:
    if len(github_repos) >= 60:
        logger.warning("Possible out of rate limits")

    while True:

        for repo in github_repos:
            logger.info(f"Start processing {repo}")

            send_notification = True
            db_record = database.getByQuery({"url": repo})[0]

            if not db_record["tag_name"]:
                send_notification = False

            remaining_limit = get_rate_limit()["remaining"]
            if remaining_limit == 0:
                break

            release = get_release(url=repo)
            database.updateById(pk=db_record["id"], new_data={"url": repo, "tag_name": release["tag_name"]})

            if send_notification:
                send_slack_notification(name=release["name"], tag_name=release["tag_name"], url=release["url"])

            logger.info(f"Successfully processed {repo}")

        sleep(check_frequency)


if __name__ == "__main__":
    init_db()
    main()
