import serial

def send_raw_byte(port: serial.Serial, hex_repr: str):
    x = bytes.fromhex(hex_repr)
    port.write(x)
    while True:
        line = port.readline()
        if not line:
            break
        print(line)

def main():
    with serial.Serial("/dev/ttyUSB0", 115200, timeout=1) as s:
        while True:
            payload = eval(input(">> "))  # 'ff'*256 (string*number of times) is allowed
            print(f">> {payload}")
            send_raw_byte(s, payload)

if __name__ == '__main__':
    main()