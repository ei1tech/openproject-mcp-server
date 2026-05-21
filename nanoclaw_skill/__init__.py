"""OpenProject NanoClaw Skill - Multi-project task management integration."""

__version__ = "1.0.0"
__description__ = "OpenProject integration for NanoClaw multi-project task management"

from .openproject_cli import OpenProjectCLI

__all__ = ["OpenProjectCLI"]
