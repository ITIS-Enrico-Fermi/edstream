from time import sleep
import os

def create_fifo(path: str) -> None:
    if not os.path.exists(path):
        os.mkfifo(path)

create_fifo('fifo.in')
create_fifo('fifo.out')

with open('fifo.in', 'wb', 0) as fifo_out, open('fifo.out', 'rb', 0) as fifo_in:
    fd = fifo_in.fileno()
    os.set_blocking(fd, False)
    while True:
        r = fifo_in.read(3)
        if r:
            print(r.decode())
        fifo_out.write('azz'.encode())