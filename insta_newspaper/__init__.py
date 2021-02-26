import os
import pickle
import re
import requests
import cv2
import yaml

import typer
from typing import List, Optional

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import insta_newspaper.instagram_app as _INSTAGRAM_APP
from insta_newspaper.image_saver import save_image

_REFERENCE_DICT = None
_CONFIG = None

_APP = typer.Typer()


def parse_config():
    """Parses config from yaml files."""

    global _REFERENCE_DICT
    global _CONFIG

    with open(os.path.join(os.path.dirname(__file__), "newspaper_reference.yaml")) as f:
        _REFERENCE_DICT = yaml.load(f, Loader=yaml.FullLoader)
    with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as f:
        _CONFIG = yaml.load(f, Loader=yaml.FullLoader)


@_APP.command("new_post")
def new_post(
    names: List[str] = typer.Option(
        None, "-n", "--name", help="Select one or more newspaper"
    ),
    headless: Optional[bool] = typer.Option(
        False, "-h", "--headless", help="Start driver without GUI."
    ),
):
    """Download then upload to Instagram images for one or more given newspapers.

    Args:
        names (List[str]): One or more newspaper to process.
    """

    global _REFERENCE_DICT
    global _CONFIG

    selected_refs = []

    # Exit if no argument given by user
    if len(names) == 0:
        typer.secho(
            "You have to enter at least one newspaper name.",
            fg=typer.colors.RED,
            bold=True,
        )
        raise typer.Exit()

    # Convert names argument from tuple to list to remove items smoother
    names = list(names)

    # Search if argument match exactly a ref in database
    for name in names:
        for ref in _REFERENCE_DICT:
            if name.lower() == ref.lower():
                selected_refs.append(ref)
                names.remove(name)

    # If no match were found for one or more argument, search if string
    # is included in a ref name.
    if len(names) != 0:
        for name in names:
            for ref in _REFERENCE_DICT:
                if name.lower() in ref.lower():
                    selected_refs.append(ref)
                    names.remove(name)

        # If there is still unfound arguments, exit with an error
        if len(names) != 0:
            typer.secho(
                "Unable to find reference(s): {refs}".format(refs=", ".join(names)),
                fg=typer.colors.RED,
                bold=True,
            )
            raise typer.Exit()

    today_date = datetime.today().strftime("%m%d")

    for ref in selected_refs:
        chosen_date = _REFERENCE_DICT[ref]["year"] + today_date

        typer.secho(
            "Posting {ref} at date {date}".format(ref=ref, date=chosen_date),
            fg=typer.colors.GREEN,
            bold=True,
        )

        save_image(
            name=ref,
            simple_name=_REFERENCE_DICT[ref]["simple_name"],
            url=_REFERENCE_DICT[ref]["url"],
            chosen_date=chosen_date,
            save_path=_CONFIG["image_local_save_path"],
        )

        app = _INSTAGRAM_APP.InstagramApp(config=_CONFIG)
        app.upload_image(
            name=ref,
            simple_name=_REFERENCE_DICT[ref]["simple_name"],
            chosen_date=chosen_date,
        )

        app.stop_driver()

        typer.secho(
            "Upload successful",
            fg=typer.colors.GREEN,
            bold=True,
        )


@_APP.command("login")
def simple_login():
    """Simply logs the user in to let him manage his account if needed."""

    global _CONFIG

    app = _INSTAGRAM_APP.InstagramApp(config=_CONFIG)


@_APP.command("save_cookie")
def cookie_save():
    """Start the gecko driver to store valid cookies."""

    global _CONFIG

    app = _INSTAGRAM_APP.InstagramApp(config=_CONFIG, save_cookies=True)
    app.stop_driver()


def main():
    parse_config()
    _APP()
