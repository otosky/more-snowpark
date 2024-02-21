set dotenv-load

# show justfile recipes
default:
    @just --list

# setup dev deps
setup:
    mise install -y
    poetry install

# format python code
fmt:
    poetry run isort .
    poetry run black .
