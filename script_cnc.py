import cnc
import time


def main():
    cnc_cur.connect('COM3', 115200)
    cnc_cur.set_origin()

    cnc_cur.set_position(20, 20)
    time.sleep(2)

    cnc_cur.set_position(-20, 20)
    time.sleep(2)

    cnc_cur.set_position(-20, -20)
    time.sleep(2)

    cnc_cur.set_position(20, -20)
    time.sleep(2)

    cnc_cur.set_position(0, 0)

    cnc_cur.close()


if __name__ == '__main__':
    main()
