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
    
    def actuate(self, values: list[float], delta: bool = True):
        if delta:
            self.servo_controller.update_setpoint_delta(values)
        else:
            self.servo_controller.update_setpoint(values)
        return True

    def sense(self):
        return self.sensor_reader.data