import sys
sys.path.insert(0, '..')
import unittest
import mock
import excatch


class TestCase(unittest.TestCase):

    def setUp(self):
        """
            patch everything
        """
        excatch.json = mock.Mock()
        excatch.traceback = mock.Mock()
        excatch.redis = mock.Mock()
        excatch.sys = mock.Mock()
        excatch.socket = mock.Mock()
        excatch.fcntl = mock.Mock()
        excatch.struct = mock.Mock()
        excatch.fcntl.ioctl = mock.Mock()
        excatch.fcntl.ioctl.return_value = range(0, 25)
        excatch.datetime = mock.Mock()
        excatch.inspect = mock.Mock()
        excatch.inspect.getsourcelines.return_value = [['TEST'], 1]
        excatch.sys.__excepthook__ = lambda *args: args


class IPTests(TestCase):

    def testSocketConstruction(self):
        """
            Test if socket.socket is called
            with the required parameters
        """

        excatch.socket.AF_INET = 'AF_INET'
        excatch.socket.SOCK_DGRAM = 'SOCK_DGRAM'
        excatch.Hook().get_ip_address('test')
        excatch.socket.mockCheckCall(
            1, 'socket', 'AF_INET', 'SOCK_DGRAM'
        )

    def testSocketResponse(self):
        excatch.Hook().get_ip_address('test')
        excatch.fcntl.ioctl.assert_called_with(
            excatch.socket.socket().fileno(),
            0x8915,
            excatch.struct.pack()
        )
        excatch.struct.pack.mockCheckCall()
        excatch.socket.inet_ntoa.assert_called_with(
            [20, 21, 22, 23]
        )


class AddressTest(TestCase):

    def testGetIPAddressWorking(self):
        old = excatch.Hook.get_ip_address
        excatch.Hook.get_ip_address = mock.Mock()
        excatch.Hook.get_ip_address.return_value = 'TEST'
        assert excatch.Hook().find_address(), 'TEST'
        excatch.Hook.get_ip_address.mockCheckCall(
            1, 'eth0'
        )
        excatch.Hook.get_ip_address = old

    def testGetIPAddressFailingOne(self):
        old = (excatch.Hook.get_ip_address, excatch.Hook.ifaces)

        def cb(instance, iface):
            if iface == 'first':
                raise IOError
            return iface

        excatch.Hook.get_ip_address = cb
        excatch.Hook.ifaces = ['first', 'second']
        assert excatch.Hook().find_address(), 'second'
        (excatch.Hook.get_ip_address, excatch.Hook.ifaces) = old

    def testGetIPAddressFailingAll(self):
        old = excatch.Hook.get_ip_address

        def cb(instance, iface):
            raise IOError

        excatch.Hook.get_ip_address = cb
        excatch.Hook.ifaces = ['first', 'second']
        assert excatch.Hook().find_address(), 'Ip Not determined'
        excatch.Hook.get_ip_address = old


class HookTests(TestCase):

    def testJsonCalled(self):
        old = excatch.Hook.get_ip_address
        excatch.traceback.format_tb.return_value = ['TEST']
        excatch.Hook.get_ip_address = mock.Mock()
        excatch.Hook.get_ip_address.return_value = 'TEST'
        excatch.datetime.datetime.now.return_value = 'TEST'
        excatch.Hook().custom_hook(object, object, object)
        excatch.Hook.get_ip_address = old
        params = dict(
            type='object',
            time='TEST',
            traceback='TEST',
            ip='TEST'
        )
        excatch.json.dumps.mockCheckCall(1, params)

    def testBind(self):
        old = excatch.Hook.custom_hook
        excatch.Hook.custom_hook = 'TEST'
        excatch.bind()
        assert excatch.sys.excepthook, 'TEST'
        excatch.Hook.custom_hook = old

    def testUnbind(self):
        excatch.bind()
        excatch.unbind()
        assert excatch.sys.excepthook, excatch.sys.__excepthook__

    def testBindApp(self):
        old = excatch.Hook.custom_hook
        excatch.Hook.custom_hook = mock.Mock()
        app = mock.Mock()
        sys_m = mock.Mock()
        sys_m.exc_info.return_value = ['TEST', 'TEST_RETURN']

        excatch.bind_app(app, sys_m)
        response = app.internalerror()
        assert response, 'TEST_RETURN'
        excatch.Hook.custom_hook.mockCheckCall(1, 'TEST', 'TEST_RETURN')
        excatch.Hook.custom_hook = old



if __name__ == '__main__':
    unittest.main()
