import nbformat
from nbconvert.preprocessors import Preprocessor
from traitlets import Bool, List, Unicode

from ._patterns import (
    build_prefixed_regex_pattern,
    build_prefixed_regex_pattern_with_value,
)

__all__ = [
    "MetaDataInjectorPreprocessor",
    "GlobalMetaDataInjectorPreprocessor",
    "JUPYTER_BOOK_CODE_TAGS",
    "jupyter_book_metadata_injector",
]


class MetaDataInjectorPreprocessor(Preprocessor):
    """
    Parse all *code* cells and convert the given `strings` with the
    `prefix` to the `metadata_group`, which is the `tags` list by default.

    With `remove_line=True` (default) the matched `strings` will be removed from
    the output.

    By default a code cell with the contents:
    ```python
    # hide
    import os
    ```
    Will be transformed to:
    ```python
    import os
    ```
    where the code cell's metadata `tags` field contains the additional entry `hide`.
    """

    strings = List(Unicode(), default_value=[]).tag(config=True)
    prefix = Unicode(default_value="#").tag(config=True)
    metadata_group = Unicode(default_value="tags").tag(config=True)
    remove_line = Bool(default_value=True).tag(config=True)

    def _write_tag(self, tag, cell):
        tags = cell.setdefault("metadata", {}).setdefault(self.metadata_group, [])
        if tag not in tags:
            tags.append(tag)
        cell["metadata"][self.metadata_group] = tags
        return cell

    def preprocess_cell(self, cell, resource, index):
        if cell["cell_type"] == "markdown":
            return cell, resource
        for string in self.strings:
            pattern = build_prefixed_regex_pattern(self.prefix, string)
            m = pattern.search(cell.source)
            if m is not None:
                tag = m.group("key")
                cell = self._write_tag(tag, cell)
            if self.remove_line:
                cell.source = pattern.sub("", cell.source)
        return cell, resource


class GlobalMetaDataInjectorPreprocessor(Preprocessor):
    """
    Parse all *code* cells and convert the given `prefix`ed `keys`
    and the following *value* to the global `metadata` field.

    To clean up the output, the lines containing any `string` may be removed
    by setting `remove_line=True` (default).

    The provided list of `keys` will be used to access the *global* `metadata` field
    and insert the value that is followed by the `key` in the code cell.
    Note that the global metadata field will be overwritten if multiple cells define the
    field's value.

    ```python
    # publish true
    import os
    ```
    Will be transformed to:
    ```python
    import os
    ```
    where the _notebook's_ cell's metadata `publish` field may be created and contain the additional entry `true`.

    To only add a specific value to a metadata field (usually `tags`) look at `MetaDataInjectorPreprocessor`.
    """

    keys = List(Unicode()).tag(config=True)
    prefix = Unicode(default_value="#").tag(config=True)
    delimiter = Unicode(default_value=r"\s*").tag(config=True)

    def preprocess(self, nb, resources):
        if len(self.keys) == 0:
            return nb, resources

        for cell in nb.cells:
            if cell["cell_type"] == "markdown":
                continue
            for key in self.keys:
                pattern = build_prefixed_regex_pattern_with_value(
                    self.prefix, key, delimiter=self.delimiter
                )
                m = pattern.search(cell.source)
                if m is not None:
                    value = m.group("value")
                    nb.setdefault("metadata", {})
                    nb["metadata"][key] = value
        return nb, resources


JUPYTER_BOOK_CODE_TAGS = {
    "full-width": "Cell takes up all of the horizontal space",
    "output_scroll": "Make output cell scrollable",
    "margin": "Move code cell to the right margin",
    "hide-input": "Hide cell but display the outputs",
    "hide-output": "Hide the outputs of a cell",
    "hide-cell": "Hides inputs and outputs of a cell",
    "remove-input": "Remove the inputs of a cell",
    "remove-output": "Remove the outputs of a cell",
    "remove-cell": "Remove the entire code cell",
    "raises-exception": "Mark cell as 'expected error'",
}


def jupyter_book_metadata_injector(
    file_content: str, prefix: str = "#", remove_line: bool = True
):
    """
    Calls the `MetaDataInjectorPreprocessor` after reading the `file_content`
    as a `NotebookNode`.
    The preprocessor will inject all the jupyter-book specific tags into the
    metadata tags group of the code cells.
    For extra information about the jupyter-book specific tags, see
    `JUPYTER_BOOK_CODE_TAGS`.

    By default, the `prefix` or `comment` symbol is assumed to be `#`

    Args:
        file_content (str): contents of an `ipynb` file
        prefix (str, optional): Comment symbol that preceeds the jupyter-book keys. Defaults to "#".
        remove_line (bool, optional): Set if the metadata comment lines should be removed after injection. Defaults to True.
    """
    tags = list(JUPYTER_BOOK_CODE_TAGS.keys())
    inp_nb = nbformat.reads(file_content, as_version=4)

    nb, _ = MetaDataInjectorPreprocessor(
        strings=tags, prefix=prefix, remove_line=remove_line
    ).preprocess(inp_nb, None)
    return nb
