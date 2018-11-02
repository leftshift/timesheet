import click
import datetime
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
    """Add working hours from START until END.
    
    Optionally, a break can be added, giving it's duration
    in minutes in BREAK_TIME"""
    start = try_parse(start)
    end = try_parse(end)
    if end < start:
        raise ValueError("start time is after end time")
    if end - start > datetime.timedelta(hours=10):
        raise ValueError("Duration of over 8h seems unlikely")

    db.add(start, end, break_time)
    click.echo("Added event from {} to {}".format(start, end))

@cli.command()
@click.argument('time', required=False)
@pass_db
def start(db, time):
    """Start work session.

    This session can later be ended with `timesheet end`
    
    By default, it will start at the current time, optionally,
    the beginning can be given in TIME"""
    if time:
        time = try_parse(time)
    db.add_start(time)
    click.echo("Started work at {}".format(time))

@cli.command()
@click.argument('time', required=False)
@click.argument('break_time', default=0)
@pass_db
def end(db, time, break_time):
    """End work session.
    
    This will end the current work session, earlier started with
    `timesheet start`
    
    By default, it will end the session at the current time,
    optionally, the end can be given with TIME.
    
    Also, the length of a break in minutes can be passed in BREAK_TIME."""
    if time:
        time = try_parse(time)
    res = db.add_end(time, break_time)
    click.echo("Finished work, from {} to {}".format(
            res.start,
            res.end
        ))

@cli.command(name="list")
@click.option('--start', '--from', help='set lower limit for time range')
@click.option('--end', '--to', help='set upper limit for time range')
@click.option('--around', help='show month around specified date')
@pass_db
def list_(db, start, end, around):
    """Show events in given range.
    
    By default, it shows the current month.
    """
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

    if not res.events:
        click.echo(click.style("No events in specified range :D",
                   fg="green"))
        return

    fstring = "{date!s:<15}\t{dur!s:>10}\t{note:}"
    header = {
            "date": "Date",
            "dur": "Duration",
            "note": "Note"
        }


    lines.append(table(fstring, header, iterate_events(res.events)))

    lines.append("")
    lines.append("=" * 20)

    total = int(res.total.total_seconds() // 60)
    total_hour, total_min = divmod(total, 60)
    total_s = "{h}:{m:0<2}".format(h=total_hour, m=total_min)

    mean_s = str(res.mean)[:-3]

    lines.append(click.style("sum:", fg="green") + "{:>15}".format(total_s))
    lines.append(click.style("mean:", fg="green") + "{:>14}".format(mean_s))
    
    click.echo("\n".join(lines))


@cli.group()
def db():
    """Manage timesheet database."""
    pass

@db.command()
@pass_db
def init(db):
    """Create necessary tables in the database."""
    db.init_db()

cli()
