#-*- coding: utf-8 -*-

"""ui.py

UI and progress reporting for ThunderDots.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.theme import Theme

theme = Theme(
    {
        "td": "bold magenta",
        "ok": "green",
        "logo": "bold cyan",
        "warn": "yellow",
        "err": "red",
        "dim": "dim",
    }
)

console = Console(theme=theme)


@dataclass
class UI:
    """UI and progress reporting for ThunderDots, using rich for console output and progress bars.

    - enabled: Whether to enable UI output (default: True)
    - progress: Optional Progress instance for managing progress bars (initialized in __enter__)
    - task_walk: Optional task ID for the collection walking progress bar
    - task_res: Optional task ID for the resource fetching progress bar
    """
    enabled: bool = True
    progress: Optional[Progress] = None
    task_walk: Optional[int] = None
    task_res: Optional[int] = None

    def __enter__(self):
        """Initialize the Progress instance for managing progress bars if UI is enabled, and return self for use in a with statement."""
        if not self.enabled:
            return self

        self.progress = Progress(
            SpinnerColumn(style="logo"),
            TextColumn("[logo]⚡ ThunderDots[/logo] [td]{task.description}[/td]"),
            BarColumn(),
            TextColumn("[dim]{task.completed}/{task.total}[/dim]"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True,
            disable=not console.is_terminal,
        )
        self.progress.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        """Clean up the Progress instance if it was initialized, ensuring that any progress bars are properly finalized and resources are released when exiting the with statement."""
        if self.progress:
            self.progress.__exit__(exc_type, exc, tb)

    async def __aenter__(self):
        """Asynchronous context manager entry method, simply calls the synchronous __enter__ method to initialize the Progress instance if UI is enabled, allowing for use in an async with statement."""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc, tb):
        """Asynchronous context manager exit method, simply calls the synchronous __exit__ method to clean up the Progress instance if it was initialized, ensuring that any progress bars are properly finalized and resources are released when exiting an async with statement."""
        return self.__exit__(exc_type, exc, tb)

    def debug(self, msg: str):
        """Log a debug message with dim styling, only if UI is enabled."""
        self.log(msg, style="dim")

    def warn(self, msg: str):
        """Log a warning message with yellow styling, only if UI is enabled."""
        self.log(msg, style="warn")

    def error(self, msg: str):
        """Log an error message with red styling, only if UI is enabled."""
        self.log(msg, style="err")

    def log(self, msg: str, style: str = "td"):
        """Log a message with the specified style, only if UI is enabled."""
        if self.enabled:
            console.print(msg, style=style)

    def start_walk(self):
        """Start the progress bar for walking collections, initializing a task with the description "Walk collections" and a total of 1 to represent the overall progress of the collection walking phase."""
        if self.progress:
            self.task_walk = self.progress.add_task("Walk collections", total=1)

    def update_collections(self, walked: int, collections: int, resources: int, http_errors: int):
        """Update the progress bar for walking collections with the current counts of walked collections, total collections, resources found, and HTTP errors encountered, updating the description to reflect these counts and keeping the total at 1 to represent overall progress.

        :param walked: Number of collections walked so far
        :type walked: int
        :param collections: Total number of collections found so far
        :type collections: int
        :param resources: Total number of resources found so far
        :type resources: int
        :param http_errors: Total number of HTTP errors encountered so far
        :type http_errors: int
        :returns: None (updates the progress bar if available)
        """
        if not self.progress or self.task_walk is None:
            return

        desc = (
            f"Walk collections  "
            f"[dim]walked={walked}  collections={collections}  resources={resources}  "
            f"errors={http_errors}[/dim]"
        )
        self.progress.update(self.task_walk, description=desc, completed=0, total=1)

    def finish_walk(self):
        """Finish the progress bar for walking collections by marking it as completed, setting the completed value to 1 to indicate that the collection walking phase is complete."""
        if self.progress and self.task_walk is not None:
            self.progress.update(self.task_walk, completed=1)

    def start_resources(self, total: int):
        """Start the progress bar for fetching resources, initializing a task with the description "Fetch resources" and the specified total number of resources to represent the overall progress of the resource fetching phase."""
        if self.progress:
            self.task_res = self.progress.add_task("Fetch resources", total=total)

    def update_resources(self, done: int, total: int, http_errors: int):
        """Update the progress bar for fetching resources with the current count of done resources, total resources, and HTTP errors encountered, updating the description to reflect these counts and keeping the total at the specified value to represent overall progress."""
        if not self.progress or self.task_res is None:
            return
        desc = f"Fetch resources  [dim]errors={http_errors}[/dim]"
        self.progress.update(self.task_res, description=desc, completed=done, total=total)

    def advance_resources(self, n: int = 1):
        """Advance the progress bar for fetching resources by a specified number of completed resources, incrementing the completed value by n to reflect progress in the resource fetching phase."""
        if self.progress and self.task_res is not None:
            self.progress.advance(self.task_res, n)

    def finalize(self, stats: dict):
        """Finalize the UI output by printing a summary message with the total elapsed time and HTTP errors encountered, only if UI is enabled."""
        if not self.enabled:
            return
        console.print(
            "[logo]⚡ ThunderDots[/logo] "
            f"[ok]✔ Done[/ok]  "
            f"elapsed={stats.get('elapsed_seconds', 0):.2f}s  "
            f"http_errors={stats.get('http_errors', 0)}",
        )
