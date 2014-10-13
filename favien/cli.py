""":mod:`favien.cli` --- Command line interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import click
from sqlalchemy import create_engine

from .orm import Base
from .web import create_app


@click.group()
@click.option('--config')
@click.pass_context
def cli(ctx, config):
    """Management script for Favien."""
    ctx.obj = {'CONFIG': config or 'dev.cfg'}


@cli.command()
@click.pass_context
def initdb(ctx):
    """Initializes the database."""
    app = create_app(ctx.obj['CONFIG'])
    engine = create_engine(app.config['DATABASE_URL'])
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@cli.command()
@click.pass_context
def run(ctx):
    """Runs a development server."""
    app = create_app(ctx.obj['CONFIG'])
    app.run()
