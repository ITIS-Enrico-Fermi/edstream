from time import sleep
import os

def create_fifo(path: str) -> None:
    if not os.path.exists(path):
        os.mkfifo(path)

create_fifo('fifo.in')
create_fifo('fifo.out')

with open('fifo.in', 'rb', 0) as fifo_in, open('fifo.out', 'wb', 0) as fifo_out:
    fd = fifo_in.fileno()
    os.set_blocking(fd, False)
    while True:
        fifo_out.write("tes".encode())
        r = fifo_in.read(3)
        if r:
            print(r.decode())