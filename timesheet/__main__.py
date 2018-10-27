import click
from timesheet.db import Db
from timesheet.util import try_parse, iterate_events, table

pass_db = click.make_pass_decorator(Db)

@click.group()
@click.version_option('0.1')
@click.option('--db', default='sqlite:///timesheet.db',
              help='full database and driver string for SQLAlchemy')
@click.pass_context
def cli(ctx, db):
    ctx.obj = Db(db)

@cli.command()
@click.argument('start')
@click.argument('end')
@click.argument('break_time', default=0) 
@pass_db
def add(db, start, end, break_time):
    start = try_parse(start)
    end = try_parse(end)
    db.add(start, end, break_time)

@cli.command(name="list")
@click.option('--start', '--from', help='set lower limit for time range')
@click.option('--end', '--to', help='set upper limit for time range')
@click.option('--around', help='show month around specified day')
@pass_db
def list_(db, start, end, around):
    lines = []
    if around:
        around = try_parse(around)
        res = db.get_month(around)
    elif start or end:
        start = try_parse(start)
        end = try_parse(end)
        res = db.get_range(start, end)
    else:
        res = db.get_month(None)

    fstring = "{date!s:<15}\t{dur!s:>10}\t{note:}"
    header = {
            "date": "Date",
            "dur": "Duration",
            "note": "Note"
        }


    lines.append(table(fstring, header, iterate_events(res.events)))

    lines.append("")
    lines.append("=" * 20)
    lines.append(click.style("sum:", fg="green") + "{!s:>15}".format(res.total))
    lines.append(click.style("mean:", fg="green") + "{!s:>14}".format(res.mean))
    
    click.echo("\n".join(lines))


@cli.group()
def db():
    pass

@db.command()
@pass_db
def init(db):
    db.init_db()

cli()
