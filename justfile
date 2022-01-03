min_python := "3.7" # only used for poetry install!

install:
	poetry install
	# mamba run --prefix {{justfile_directory()}}/{{env}} python -m ipykernel install --user

kernel:
	python -m ipykernel install --user
