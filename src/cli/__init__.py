import logging
import dotenv
import click


dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


try:
    from peripherals.gnoci import gnoci
    cli.add_command(gnoci)
except ImportError:
    pass

try:
    from client import client
    cli.add_command(client)
except ImportError as error:
    logger.error(error)
    pass


if __name__ == "__main__":
    cli()