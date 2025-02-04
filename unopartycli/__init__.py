import os, sys

APP_VERSION = '1.1.5'

CURR_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser('__file__'))))
WIN_EXE_LIB = os.path.normpath(os.path.join(CURR_DIR, 'library'))
if os.path.isdir(WIN_EXE_LIB):
    sys.path.insert(0, WIN_EXE_LIB)

def client_main():
    from unopartycli import client
    client.main()

def server_main():
    from unopartycli import server
    server.main()
