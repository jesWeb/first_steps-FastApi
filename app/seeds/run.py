
import typer

from app.seeds.service import run_all, run_catgories, run_tags, run_users


app = typer.Typer(help="Seeds: users,categories,tags")

@app.command("all")
def all_():
    run_all()
    typer.echo("Cargdando todo")


@app.command("users")

def users():
    run_users()
    typer.echo("Usuarios cargados")


@app.command("categories")
def categories():
    run_catgories()
    typer.echo("categorias cargadas")


@app.command("tags")
def tags():
    run_tags()
    typer.echo("Tags cargados")