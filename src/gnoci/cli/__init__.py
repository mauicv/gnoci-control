import logging
import dotenv
import click


dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


try:
    from gnoci.cli.control import (
        start,
        control_loop,
    )
    cli.add_command(start)
    cli.add_command(control_loop)
except ImportError as error:
    logger.error(error)
    raise error


try:
    from gnoci.cli.configure import (
        run_checks,
        test_control_hz,
        measure_positions,
        test_hardware
    )
    cli.add_command(run_checks)
    cli.add_command(test_control_hz)
    cli.add_command(measure_positions)
    cli.add_command(test_hardware)
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