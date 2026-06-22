"""Research project catalog and factory."""

from typing import ClassVar

from shellcraft.core import BaseFactory, BaseItem


class ResearchProject(BaseItem):
    FIXTURES: ClassVar[str] = "research.toml"

    def __repr__(self):
        return f"%{self.name}%"


class ResearchFactory(BaseFactory):
    ITEM_CLASS = ResearchProject

    def is_available(self, item_name: "str | BaseItem") -> bool:
        project = self.get(item_name)
        if project.name in self.game.state.research_completed:
            return False
        return super().is_available(project)


ResearchProject._load_catalog()
