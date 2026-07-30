import struct
import math

from .hardware import (
    IMU_ADDR, ROT_ENC_ADDR, A2D_ADDR,
    PWM_MUX_ADDR, I2C_MUX_ADDR_1, I2C_MUX_ADDR_2,
)

# IMU default: 1g downward (az), all others zero
_AZ_1G = 16384  # ±2g scale → 1g = 16384 counts
_IMU_DEFAULT = struct.pack(
    ">hhhhhhh",
    0,      # ax
    0,      # ay
    _AZ_1G, # az
    0,      # temp
    0,      # gx
    0,      # gy
    0,      # gz
)

# Rotary encoder: mid-range angle (≈0.5)
# decode: ((raw[0] & 0x0F) << 8 | raw[1]) / 4095
_ROT_ENC_MID = bytes([0x07, 0xFF])  # → 2047 / 4095 ≈ 0.5

# ADC: zero (below foot-contact threshold of 1000)
_ADC_ZERO = bytes([0x00, 0x00])

# Rotary encoder status: magnet detected (bit 5 set)
_ROT_ENC_STATUS = bytes([0x20])


class MockedBus:
    """Mimics the smbus2.SMBus interface for development without I2C hardware.

    Writes are silently accepted. Reads return physically plausible values:
    - IMU: 1g on az (robot upright), all gyro axes zero
    - Rotary encoders: mid-range angle (~0.5)
    - ADC: zero (no foot contact)
    """

    def __init__(self, bus_number: int = 1):
        self.bus_number = bus_number
        self._mux_channel: dict[int, int] = {
            I2C_MUX_ADDR_1: 0,
            I2C_MUX_ADDR_2: 0,
        }

    # ------------------------------------------------------------------
    # Write operations — accepted silently
    # ------------------------------------------------------------------

    def write_byte(self, addr: int, value: int) -> None:
        if addr in self._mux_channel:
            self._mux_channel[addr] = value

    def write_byte_data(self, addr: int, reg: int, value: int) -> None:
        pass

    def write_i2c_block_data(self, addr: int, reg: int, data: list) -> None:
        pass

    # ------------------------------------------------------------------
    # Read operations — return plausible stub data
    # ------------------------------------------------------------------

    def read_byte_data(self, addr: int, reg: int) -> int:
        return self.read_i2c_block_data(addr, reg, 1)[0]

    def read_i2c_block_data(self, addr: int, reg: int, length: int) -> bytes:
        if addr == IMU_ADDR and reg == 0x3B:
            return _IMU_DEFAULT[:length]

        if addr == ROT_ENC_ADDR:
            if reg == 0x0C:  # angle registers
                return _ROT_ENC_MID[:length]
            if reg == 0x0B:  # status register
                return _ROT_ENC_STATUS[:length]

        if addr == A2D_ADDR:
            return _ADC_ZERO[:length]

        return bytes(length)

    # ------------------------------------------------------------------
    # Context manager / lifecycle
    # ------------------------------------------------------------------

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
