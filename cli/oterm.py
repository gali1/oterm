import asyncio
from importlib import metadata
import typer

from oterm.app.oterm import app
from oterm.config import envConfig
from oterm.store.store import Store

cli = typer.Typer()

async def upgrade_db():
    await Store.create()

async def handle_upgrade():
    await upgrade_db()

def oterm_sync(version: bool, upgrade: bool, sqlite: bool):
    if version:
        typer.echo(f"oterm v{metadata.version('oterm')}")
    elif upgrade:
        # Using asyncio.run() to handle the async upgrade_db call
        asyncio.run(handle_upgrade())
    elif sqlite:
        typer.echo(envConfig.OTERM_DATA_DIR / "store.db")
    else:
        app.run()

@cli.command()
def oterm(
    version: bool = typer.Option(None, "--version", "-v"),
    upgrade: bool = typer.Option(None, "--upgrade"),
    sqlite: bool = typer.Option(None, "--db"),
):
    oterm_sync(version, upgrade, sqlite)

if __name__ == "__main__":
    cli()
