class ReportBuilder:
    def __init__(self, title: str):
        self.title = title
        self.sections = []

    def add_section(self, heading: str, content: str):
        self.sections.append({"heading": heading, "content": content})
        return self

    def build(self) -> dict:
        return {
            "title": self.title,
            "section_count": len(self.sections),
            "sections": self.sections,
            "text": self._render(),
        }

    def _render(self) -> str:
        lines = [f"# {self.title}"]
        for section in self.sections:
            lines.append(f"\n## {section['heading']}")
            lines.append(section["content"])
        return "\n".join(lines)


def main(title: str, sections: list[dict]) -> dict:
    """sections is a list of {heading: str, content: str} dicts."""
    builder = ReportBuilder(title)
    for section in sections:
        builder.add_section(section["heading"], section["content"])
    return builder.build()
