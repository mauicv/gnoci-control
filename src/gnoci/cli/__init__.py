import logging
import dotenv
import click


dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


try:
    from gnoci.cli.control import start
    cli.add_command(start)
except ImportError as error:
    logger.error(error)
    raise error

try:
    from gnoci.cli.storage import storage
    cli.add_command(storage)
except ImportError as error:
    logger.error(error)
    raise error

if __name__ == "__main__":
    cli()