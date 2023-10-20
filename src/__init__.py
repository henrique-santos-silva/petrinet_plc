import os, sys
from queue import SimpleQueue
import flask.cli
flask.cli.show_server_banner = lambda *args: None

BASE_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    os.pardir)
)

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# BASE_DIR = '.'
print(BASE_DIR)


thread_error_queue = SimpleQueue()