# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gnoci Control is a robotics control system for a quadruped (4-legged) Raspberry Pi robot named "gnoci". The codebase has two distinct sides that run on different machines:

- **Server (robot/Pi)**: runs `src/gnoci/` — directly drives hardware (servos via pigpio, IMU via smbus2/mpu6050)
- **Client (training machine)**: runs `src/client/` — loads RL models from GCS, sends action commands to the robot over TCP, uploads rollout data back to GCS for offline training

Communication between the two is a raw TCP socket protocol (JSON messages) implemented in `src/networking_utils/`.

## Installation

Install server dependencies (on the Pi):
```bash
pip install -e ".[server]"
# or: pip install -r requirements/server.txt
```

Install client dependencies (on training machine):
```bash
pip install -e ".[client]"
# or: pip install -r requirements/client.txt
```

Note: `requirements.txt` is a legacy ROS-era artifact and should be ignored.

## Running the Robot Server

Start the robot control server on the Pi (requires pigpio daemon running):
```bash
gnoci gnoci start --host 0.0.0.0 --port 8000
```

Move servos to a specific position directly:
```bash
gnoci gnoci move --front-left-bottom=0.4 --front-right-bottom=0.4 --back-right-bottom=0.4 --back-left-bottom=0.4 --front-left-top=-0.3 --front-right-top=-0.3 --back-right-top=-0.3 --back-left-top=-0.3
```

Environment variables (`GNOCI_HOST`, `GNOCI_PORT`, `CAMERA_HOST`, `CAMERA_PORT`) can be set in a `.env` file; the CLI loads it via `python-dotenv`.

## Running Tests

Tests use pytest. Install pytest first (`pip install pytest`), then run from the repo root:
```bash
pytest src/gnoci/tests/
```

Run a single test:
```bash
pytest src/gnoci/tests/test_robot.py::test_servo_controller
```

Tests under `src/gnoci/tests/` use `conftest.py` mock fixtures (`Mock_PIGPIO`, `Mock_mpu6050`) so hardware is not required.

The `tests/` directory at the root contains older scripts that are run directly as `__main__` rather than as pytest tests.

## Architecture

### Control loop (`src/gnoci/`)

`Gnoci` (in `gnoci.py`) composes two mixins via cooperative multiple inheritance:
- `ServoController` — starts a background `Loop` thread that calls `pigpio.set_servo_pulsewidth()` at the configured interval. Each `Servo` instance runs a `simple_pid.PID` controller to smooth motion toward its setpoint.
- `MPU6050Mixin` — starts a second background `Loop` thread to poll the IMU and update filtered sensor data. Two filters run in parallel: a `ComplementaryFilter` (always on) and a pluggable filter (default: `IdentityFilter`, can be `ButterworthFilter` or `LowPassFilter`).

`Channel` (`src/networking_utils/channel.py`) wraps a TCP server; it calls `Gnoci.handle_message()` for each JSON-encoded request. Supported commands: `act` (delta update to servo setpoints), `set_servo_states` (absolute setpoints), `read` (returns servo values + IMU data).

### Client / training side (`src/client/`)

`Client` (`src/networking_utils/client.py`) connects to the robot Channel and exchanges JSON. `GCS_Interface` (`src/gnoci/storage/__init__.py`) wraps Google Cloud Storage to manage:
- **Models**: versioned actor `.pt` files under `{experiment}/actor/actor-{version}.pt`
- **Rollouts**: JSON trajectory files under `{experiment}/rollouts/{uuid}.json`
- **DataLoader**: downloads rollouts from GCS, normalises states using `PRECOMPUTED_MEANS`/`PRECOMPUTED_STDS` from `src/config.py`, and samples batches for training.

GCS credentials are read from `world-model-rl-01a513052a8a.json` (gitignored).

### Servo layout

8 servos, indexed 0–7 in `pin_id` order:  
`front_right_top`, `front_right_bottom`, `front_left_top`, `front_left_bottom`, `back_right_top`, `back_right_bottom`, `back_left_top`, `back_left_bottom`.  
Left-side servos have `reverse=True`. PWM range is 500–2500 µs. Servo values are in `[-1, 1]`; per-servo `pin_limits` constrain the reachable range.

### Import paths

All source is under `src/`. The package is installed as `gnoci-control`; the CLI entry point is `gnoci = "cli:cli"`. Internally, code uses un-namespaced imports like `from networking_utils.client import Client` — this works because `src/` is on `sys.path` when the package is installed.
