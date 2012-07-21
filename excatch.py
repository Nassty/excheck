import sys
import redis
import traceback
import json
import socket
import fcntl
import struct
from settings import REDIS_ADDRESS
from settings import queue_name
import datetime
import inspect


class Hook(object):
    ifaces = ['eth0', 'eth1', 'ppp0', 'en0', 'en1']
    server = False

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24]
        )

    def find_address(self):
        for iface in self.ifaces:
            try:
                return self.get_ip_address(iface)
            except IOError:
                pass
        return 'Ip Not determined'

    def custom_hook(self, ex_type, ex_object, tb):
        sourcecode = inspect.getsourcelines(tb)
        source = []
        end = len(sourcecode[0])
        for line in range(end):
            source.append("%s %s" %
                    (sourcecode[1] + line, sourcecode[0][line]))
        tb_list = traceback.format_tb(tb)
        tb_list.append(str(ex_object))
        tb_list.append("\n\n##CODE BELOW\n\n\n")
        tb_list.append("".join(source))
        tb_string = "".join(tb_list)
        body = {
            'type': ex_type.__name__,
            'time': str(datetime.datetime.now()),
            'traceback': tb_string,
            'ip': self.find_address()
        }
        payload = json.dumps(body)
        if not self.server:
            self.server = redis.Redis(REDIS_ADDRESS)
        self.server.publish(queue_name, payload)
        sys.__excepthook__(ex_type, ex_object, tb)


def bind():
    hook = Hook()
    sys.excepthook = hook.custom_hook


def bind_app(app, sys_m):
    hook = Hook()

    def cb():
        params = sys_m.exc_info()
        hook.custom_hook(*params)
        return params[1]

    app.internalerror = cb


def unbind():
    sys.excepthook = sys.__excepthook__
