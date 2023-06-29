from cnc import *
import time

FEED_RATE = 100


def main():
    cnc_cur = CNCTest()
    cnc_cur.connect('COM4')

    cnc_cur._send_command('G21')  # Change units to mm
    cnc_cur._send_command(f'F{FEED_RATE}')  # Speed mm/min

    cnc_cur.set_origin()

    dist = Point(20, 20).mag
    sleep = dist / (FEED_RATE / 60)

    cnc_cur.set_position(Point(20, 20))

    idle_state = False
    while not idle_state:
        out = cnc_cur._send_command('?')

        for str in out:
            if str[0] == '<':

                end = str.find('|')
                if str[1:end] == 'Idle':
                    idle_state = True

    time.sleep(1)

    print('next')
    cnc_cur.set_position(Point(0, 0))
    time.sleep(sleep)


class CNCTest(CNC):
    def set_position(self, new_pos: Point):
        """Attempts to move to a new position."""
        # wa_radius = input_dict['wa_radius'].value - input_dict['wa_pad'].value - target_radius
        wa_radius = float('inf')

        if new_pos.mag < wa_radius:
            try:
                self._send_command(f'G1 X{new_pos.x} Y{new_pos.y}')
            except CNCException:
                raise
            # time.sleep(2)
        else:
            raise CNCException(1)

    def _send_command(self, cmd: str) -> list:
        self.ser.write((cmd + '\n').encode('utf-8'))
        out = self.ser.readlines()

        for i in range(len(out)):
            out[i] = out[i].decode('utf-8')
            out[i] = out[i][:-2]  # Remove \r\n

            if not (out[i] == 'ok' or out[i][0] == '<'):
                raise CNCException(0, cmd)

        return out


if __name__ == '__main__':
    main()
