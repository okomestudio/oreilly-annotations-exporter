import re


def _process_spacing(s):
    s = re.sub(r"\n[ \t\r\f\v]+", " ", s)  # remove line breaks
    return s


def export(parsed):
    output = []
    for tree in parsed.values():
        output.append(f"* { tree.get('title') }")
        output.append("")
        for chapter in tree.findall("chapter"):
            output.append(f"** { chapter.get('title') }")
            output.append("")
            for annotation in chapter.iter("annotation"):
                quote = _process_spacing(annotation.get("quote"))

                text = annotation.get("text")
                if text:
                    m = re.match(r"^[hH](\d+)[^\d]*", text)
                    if m:
                        heading_level = int(m.group(1))
                        output.append("*" * (heading_level + 1) + " " + quote)
                        output.append("")
                        continue

                output.append(f"#+begin_quote")
                output.append(quote)
                output.append(f"#+end_quote")
                output.append("")
                if text:
                    output.append(text)
                    output.append("")

        output.append("")

    print("\n".join(output))
