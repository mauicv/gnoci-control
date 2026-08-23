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
    )
    cli.add_command(start)
except ImportError as error:
    logger.error(error)
    # raise error


try:
    from gnoci.cli.configure import (
        run_checks,
        test_control_hz,
        measure_positions,
        test_hardware,
        test_imu,
        measure_imu_offsets,
        stream_sensor_data,
    )
    cli.add_command(run_checks)
    cli.add_command(test_control_hz)
    cli.add_command(measure_positions)
    cli.add_command(test_hardware)
    cli.add_command(test_imu)
    cli.add_command(measure_imu_offsets)
    cli.add_command(stream_sensor_data)
except ImportError as error:
    logger.error(error)
    # raise error

try:
    from gnoci.cli.storage import storage
    cli.add_command(storage)
except ImportError as error:
    logger.error(error)
    # raise error


try:
    from gnoci.cli.data_collection import record_data, test_policy_actions
    cli.add_command(record_data)
    cli.add_command(test_policy_actions)
except ImportError as error:
    logger.error(error)
    # raise error


if __name__ == "__main__":
    cli()