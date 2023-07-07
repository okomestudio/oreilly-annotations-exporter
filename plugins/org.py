def export(parsed):
    output = []
    for tree in parsed.values():
        output.append(f"* { tree.get('title') }")
        output.append("")
        for chapter in tree.findall("chapter"):
            output.append(f"** { chapter.get('title') }")
            output.append("")
            for annotation in chapter.iter("annotation"):
                quote = " ".join(
                    x if x else "\n" for x in annotation.get("quote").split("\n")
                )

                output.append(f"#+begin_quote")
                output.append(quote)
                output.append(f"#+end_quote")
                output.append("")
        output.append("")

    print("\n".join(output))
