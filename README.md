# Common Jupyter Notebook Preprocessors

This repository contains a personal collection of common notebook preprocessors.
As of writing, the most relevant function is probably:
`common_nb_preprocessors.metadata_injector.jupyter_book_metadata_injector`

This function can be used to automatically inject [JupyterBook](https://jupyterbook.org/intro.html) specific tags into code-cells by using _magical_ comments.
Set the function in the [nb_custom_formats](https://jupyterbook.org/file-types/jupytext.html) entry:

```yaml
sphinx:
  config:
    nb_custom_formats:
        # as of now, this will raise an error because this option doesn't overwrite the default behaviour
        # See: https://github.com/executablebooks/jupyter-book/issues/1586
        .ipynb:
            - common_nb_preprocessors.metadata_injector.jupyter_book_metadata_injector
            # Currently, requires an option argument to work
            - remove_line: True
```
