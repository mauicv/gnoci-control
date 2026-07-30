# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gnoci Control is a robotics control system for a quadruped (4-legged) Raspberry Pi robot named "gnoci". The robot side runs on a Pi with I2C hardware (PCA9685 PWM driver, MPU6050 IMU, rotary encoders, ADCs); a separate training machine interacts with it over TCP.

## Installation

```bash
pip install -e ".[gnoci]"   # robot/Pi: hardware drivers + GCS + ONNX
pip install -e ".[client]"  # training machine: torch only
pip install -e ".[controller]"  # GCS-only (no hardware)
```

GCS credentials are read from `gnoci-497019-ecf9e3fbc49e.json` (gitignored).

## Running the Robot Server

```bash
gnoci start --host 0.0.0.0 --port 8000
```

Environment variables (`GNOCI_HOST`, `GNOCI_PORT`) can be set in a `.env` file.

## Running Tests

```bash
pytest src/gnoci/tests/
pytest src/gnoci/tests/test_robot.py::test_servo_controller  # single test
```

> **Note:** `src/gnoci/tests/conftest.py` currently imports from the old mixin-based architecture (`gnoci.servo_controller`, `gnoci.mpu6050Mixin`) which no longer exists — tests are broken and need updating to reflect the current composition-based design.

## Architecture

### Control composition (`src/gnoci/`)

`Gnoci` (`gnoci.py`) is assembled via `setup_gnoci_control()` (`setup.py`) using composition:
- `ServoController` (`hardware/servos.py`) — runs a `Loop` background thread that calls `write_servos()` on the PCA9685 PWM multiplexer at the configured frequency. Each `Servo` instance (`servo.py`) uses a `simple_pid.PID` controller to smooth motion toward its setpoint.
- `SensorReader` (`hardware/sensors.py`) — runs a second `Loop` thread to poll the IMU, rotary encoders, and ADCs, updating raw buffers. A `ComplementaryFilter` derives roll/pitch on each read.

All low-level I2C reads/writes (PCA9685, MPU6050, I2C mux 0x70/0x71, rotary encoders, ADCs) are in `hardware/hardware.py`.

### Network protocol (`src/gnoci/net_util/`)

`Channel` is a raw TCP server; each connection receives JSON messages and dispatches to `Gnoci.handle_message()`. Supported commands:
- `act` — delta update to servo setpoints (`update_setpoint_delta`)
- `set_servo_states` — absolute setpoints (`update_setpoint`)
- `read` — returns `SensorReader.data` (IMU + rot-enc + ADC + roll/pitch/overturned)

`Client` is the matching TCP client used on the training machine.

### Storage (`src/gnoci/storage/`)

`GCS_Interface` wraps two objects:
- `GCSModel` — versioned `.pt` files under `{experiment}/actor/actor-{version}.pt`
- `GCSRollout` — JSON trajectory files under `{experiment}/rollouts/{uuid}.json`

`DataLoader` (`data_loader/loader.py`) downloads rollouts from GCS, normalises states using `PRECOMPUTED_MEANS`/`PRECOMPUTED_STDS` from `config.py`, and samples batches for training.

### Servo layout

8 servos configured in `setup.py`, indexed 0–7:  
`front_right_top`, `front_right_bottom`, `front_left_top`, `front_left_bottom`, `back_right_top`, `back_right_bottom`, `back_left_top`, `back_left_bottom`.  
Left-side servos have `reverse=True`. Servo values are in `[-1, 1]`; per-servo `pin_limits` constrain the reachable range. `Servo._value_to_pwm()` maps to the 500–2500 µs PWM range.

### Filters (`src/gnoci/filters/`)

`ComplementaryFilter` (always active in `SensorReader`). Pluggable alternatives: `ButterworthFilter`, `LowPassFilter`, `IdentityFilter`.

### CLI (`src/gnoci/cli/`)

- `gnoci start` — start the TCP control server
- `gnoci storage list-models` — list GCS model checkpoints
- `gnoci storage list-rollouts` — list GCS rollout files
