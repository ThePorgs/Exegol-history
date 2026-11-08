from collections.abc import Iterable
from pathlib import Path

from textual.widgets import DirectoryTree, Tree
from textual.widgets.directory_tree import DirEntry
from textual.widgets.tree import TreeNode

PARENT_LABEL = ".."


class NavigableDirectoryTree(DirectoryTree):
    """A DirectoryTree that can start anywhere (e.g. the current directory) and
    go up to the filesystem root through a ".." entry at the top."""

    def __init__(self, path: str | Path = ".", **kwargs):
        super().__init__(Path(path).expanduser().resolve(), **kwargs)
        self._came_from: Path | None = None

    def _populate_node(self, node: TreeNode[DirEntry], content: Iterable[Path]) -> None:
        super()._populate_node(node, content)

        if node is not self.root:
            return

        root = Path(self.path)

        if root.parent != root:  # no ".." at the filesystem root
            node.add(
                PARENT_LABEL, data=DirEntry(root.parent), allow_expand=True, before=0
            )

        # After going up, put the cursor back on the directory we came from
        for child in node.children:
            if self._came_from and child.data and child.data.path == self._came_from:
                # The tree resets its cursor after a reload: move it afterwards
                self.call_after_refresh(self.move_cursor, child)
                break

        self._came_from = None

    def _on_tree_node_selected(self, event: Tree.NodeSelected[DirEntry]) -> None:
        node = event.node

        if node.parent is self.root and str(node.label) == PARENT_LABEL:
            # Don't let DirectoryTree report ".." as a selected directory:
            # move the root up instead.
            event.prevent_default()
            event.stop()
            self._came_from = Path(self.path)
            self.path = node.data.path
