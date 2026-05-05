# Python Windmill Script — Class-Based Report Generator

## Background

Windmill Python scripts can use classes as internal utilities — the script entry point is still `main`, but a class can encapsulate stateful logic that would be awkward to express as pure functions. This pattern is used for template rendering, report generation, and structured output formatting.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/generate_report.py`.
- Define an internal class `ReportBuilder` (not exported — just used inside `main`):
  ```python
  class ReportBuilder:
      def __init__(self, title: str):
          self.title = title
          self.sections = []

      def add_section(self, heading: str, content: str):
          self.sections.append({"heading": heading, "content": content})
          return self  # fluent interface

      def build(self) -> dict:
          return {
              "title": self.title,
              "section_count": len(self.sections),
              "sections": self.sections,
              "text": self._render()
          }

      def _render(self) -> str:
          lines = [f"# {self.title}"]
          for s in self.sections:
              lines.append(f"\n## {s['heading']}")
              lines.append(s['content'])
          return "\n".join(lines)
  ```
- Export a `main` function:
  ```python
  def main(title: str, sections: list[dict]) -> dict:
      """sections is a list of {heading: str, content: str} dicts."""
      builder = ReportBuilder(title)
      for s in sections:
          builder.add_section(s["heading"], s["content"])
      return builder.build()
  ```
- Create the metadata file at `/home/user/windmill-project/f/scripts/generate_report.script.yaml` with:
  - `summary: "Generate a structured report from sections"`
  - `language: python3`

## Constraints

- Project path: `/home/user/windmill-project`
- `ReportBuilder` must use a fluent interface (`add_section` returns `self`)
- `text` field must start with `# {title}` and include `## {heading}` for each section
- Return keys: `title`, `section_count`, `sections`, `text`

## Integrations

None.
