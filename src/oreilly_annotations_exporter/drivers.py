import importlib
import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from typing import List
from xml.etree import ElementTree as ET

import requests

from . import exporters


@dataclass(kw_only=True)
class Annotation:
    identifier: str
    quote: str
    ranges: list
    text: str
    last_modified_time: str
    user_identifier: str
    chapter_identifier: str

    def __lt__(self, other):
        return (self.ranges[0]["start"], self.ranges[0]["startOffset"]) < (
            other.ranges[0]["start"],
            other.ranges[0]["startOffset"],
        )


@dataclass(kw_only=True)
class Chapter:
    title: str
    url: str
    epub_identifier: str

    def __hash__(self):
        return hash((self.epub_identifier, self.url, self.title))

    def __lt__(self, other):
        return (self.epub_identifier, self.url, self.title) < (
            other.epub_identifier,
            other.url,
            other.title,
        )

    @property
    def identifier(self):
        return self.url


@dataclass(kw_only=True)
class EPub:
    identifier: str
    title: str
    cover_url: str


def _build_from_xpath(node: ET.Element, path: str) -> ET.Element:
    """Build tree from xpath and return the end node."""
    components = path.split("/")
    if components[0] == node.tag or not components[0]:
        components.pop(0)

    while components:
        component = components.pop(0)

        # Take care of positional index in the form /a/b[n] or /a/b[position()=n].
        m = re.match(r"^(\w+)\[[a-zA-Z()]*=?(\d+)\]$", component)
        if m:
            component = m.group(1)
            target_index = int(m.group(2)) - 1
        else:
            target_index = 0

        candidates = [child for child in node if child.tag == component]
        if len(candidates) > target_index:
            node = candidates[target_index]
        else:
            for _ in range(target_index + 1 - len(candidates)):
                new_node = ET.Element(component)
                node.append(new_node)
            node = new_node

    return node


def _load_cookies(cookies: str | Path) -> dict:
    path = Path(cookies)
    if path.exists():
        with path.open() as f:
            content = f.read()
    else:
        content = cookies
    cookies = {}
    for line in content.split("; "):
        k, v = line.split("=", 1)
        cookies[k] = v
    return cookies


def _get_api_responses(json_dump: Path, cookies: dict) -> List[dict]:
    url = "https://learning.oreilly.com/api/v1/annotations/all/?page_size=100"

    responses = []
    while True:
        resp = requests.get(url, cookies=cookies)

        jd = resp.json()
        responses.append(jd)

        url = jd.get("next")
        if not url:
            break

        time.sleep(1)

    with json_dump.open("w") as f:
        json.dump(responses, f)

    return responses


def _build_epub_tree(epub, data):
    root = ET.Element("epub")
    root.set("title", epub.title)
    root.set("identifier", epub.identifier)
    root.set("cover_url", epub.cover_url)

    for chapter_index, chapter in enumerate(sorted(data[epub.identifier])):
        chapter_node = _build_from_xpath(root, f"/chapter[{ chapter_index + 1 }]")
        chapter_node.set("title", chapter.title)
        chapter_node.set("url", chapter.url)

        for anno in sorted(data[epub.identifier][chapter]):
            xpath = anno.ranges[0]["start"].lower()
            node = _build_from_xpath(chapter_node, xpath + "/annotation")
            node.set("identifier", anno.identifier)
            node.set("quote", anno.quote)
            node.set("startOffset", str(anno.ranges[0]["startOffset"]))
            node.set("text", anno.text)
            node.set("lastModifiedTime", anno.last_modified_time)

    return root


def _process_api_responses(api_responses: List[dict]) -> Dict[str, str]:
    epubs = {}
    data = defaultdict(lambda: defaultdict(list))

    results = []
    for api_response in api_responses:
        results.extend(api_response["results"])

    for item in results:
        epub_identifier = item["epub_identifier"]

        if epub_identifier not in epubs:
            epubs[epub_identifier] = EPub(
                identifier=epub_identifier,
                title=item["epub_title"],
                cover_url=item["cover_url"],
            )

        chapter = Chapter(
            title=item["chapter_title"],
            url=item["chapter_url"],
            epub_identifier=epub_identifier,
        )

        annotation = Annotation(
            identifier=item["identifier"],
            quote=item["quote"],
            ranges=item["ranges"],
            text=item["text"],
            last_modified_time=item["last_modified_time"],
            user_identifier=item["user_identifier"],
            chapter_identifier=item["chapter_url"],
        )

        data[epub_identifier][chapter].append(annotation)

    as_xml = {}

    for epub_identifier in data:
        epub = epubs[epub_identifier]
        root = _build_epub_tree(epub, data)
        as_xml[epub_identifier] = root

    return as_xml


def entry_point(json_dump: Path, cookies: str | Path, export: str) -> None:
    if not json_dump.exists():
        cookies = _load_cookies(cookies)
        _get_api_responses(json_dump, cookies)

    with json_dump.open() as f:
        api_responses = json.load(f)

    as_xml = _process_api_responses(api_responses)

    if export in ("csv", "raw_xml"):
        export_func = getattr(exporters, f"export_as_{ export }")
        export_func(as_xml)
    else:
        sys.path.extend([".", "plugins"])

        try:
            mod = importlib.import_module(export)
            mod.export(as_xml)
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f"Plugin module `{ export }' not found")
        except AttributeError:
            raise RuntimeError("Plugin module must define `export' function")
