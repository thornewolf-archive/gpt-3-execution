from dataclasses import dataclass
from string import Formatter, Template
from functools import cache


@dataclass(frozen=True)
class Prompt:
    template: str

    def __str__(self):
        return self.template

    def __repr__(self) -> str:
        return f"Prompt({self.template!r})"

    def supply(self, **kwargs):
        return Prompt(Template(self.template).safe_substitute(**kwargs))

    def add(self, text: str):
        return Prompt(self.template + text)

    def add_prompt(self, prompt: "Prompt"):
        return self.add(prompt.template)

    @property
    @cache
    def fields(self):
        return Template(self.template).get_identifiers()

    @property
    def text(self):
        return self.template
