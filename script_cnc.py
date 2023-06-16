import cnc
import time


def main():
    cnc.connect('COM3', 115200)
    cnc.set_origin()

    cnc.set_position(20, 20)
    time.sleep(2)

    cnc.set_position(-20, 20)
    time.sleep(2)

    cnc.set_position(-20, -20)
    time.sleep(2)

    cnc.set_position(20, -20)
    time.sleep(2)

    cnc.set_position(0, 0)

    cnc.close()


if __name__ == '__main__':
    main()
