from flask import Blueprint
import os
import click

bp = Blueprint('cli', __name__, cli_group=None)

# This defines a command line group, which means when this function is run, all subcommand are run as well
@bp.cli.group()
def translate():
    """Translation and localization commands."""
    pass

# Click uses the decorated function name to define the subcommands, so now we define those here
@translate.command()
def update():
    # The comments here will be used to explain this command in --help
    """Update all languages."""
    # We execute the code, and if os.system returns 0, there were no issues, otherwise raise an error
    # Essentially we are running both commands, and then removing the unnecessary .pot file
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')

@translate.command()
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')

@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed.')
    os.remove('messages.pot')