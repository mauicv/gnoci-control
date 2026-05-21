class Gnoci():
    def __init__(
            self,
            servo_controller,
            sensor_reader,
        ):
        self.servo_controller = servo_controller
        self.sensor_reader = sensor_reader


    def _parse_command(self, message):
        command = message['command']
        args = message['args'] if 'args' in message else {}
        return command, args

    def handle_message(self, message):
        command, args = self._parse_command(message)
        return {
            'act': self.act,
            'set_servo_states': self.set_servo_states,
            'read': self.get_data,
        }[command](**args)
    
    def act(self, values: list[float]):
        self.servo_controller.update_setpoint_delta(values)
        return True
    
    def set_servo_states(self, values: list[float]):
        self.servo_controller.update_setpoint(values)
        return True

    def get_data(self):
        return self.sensor_reader.data
    
    def deinit(self):
        self.deinit_servo_controller()
        self.deinit_mpu()
