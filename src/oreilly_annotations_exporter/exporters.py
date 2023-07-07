import csv
import io
import xml.dom.minidom
import os
from xml.etree import ElementTree as ET


def _pretty_xml(tree):
    dom = xml.dom.minidom.parseString(ET.tostring(tree))
    return dom.toprettyxml(indent=" " * 2)


def export_as_raw_xml(parsed):
    """Export as raw XML."""
    root = ET.Element("exported")
    for tree in parsed.values():
        root.append(tree)
    print(_pretty_xml(root))


def export_as_csv(parsed):
    """Export in CSV format, as done by O'Reilly Learning."""

    stream = io.StringIO()
    writer = csv.writer(stream)

    writer.writerow(
        [
            "Book Title",
            "Chapter Title",
            "Date of Highlight",
            "Book URL",
            "Chapter URL",
            "Annotation URL",
            "Highlight",
            "Personal Note",
        ]
    )

    for tree in parsed.values():
        book_title = tree.get("title")
        for chapter in tree.findall("chapter"):
            chapter_title = chapter.get("title")
            chapter_url = chapter.get("url")
            for annotation in chapter.iter("annotation"):
                date_of_highlight = annotation.get("lastModifiedTime").split("T", 1)[0]
                book_url = os.path.dirname(chapter_url)
                annotation_url = f"{ chapter_url }#{ annotation.get('identifier') }"
                highlight = annotation.get("quote")
                personal_note = annotation.get("text")
                writer.writerow(
                    [
                        book_title,
                        chapter_title,
                        date_of_highlight,
                        book_url,
                        chapter_url,
                        annotation_url,
                        highlight,
                        personal_note,
                    ]
                )

    print(stream.getvalue())
