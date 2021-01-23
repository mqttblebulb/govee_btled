# this module simplifies connections to bluetooth devices imitating the
# pygatt module as used by the govee_btled.
# Many thanks extended to ukBaz of stack exchange for the implementation below!
#

from time import sleep
from pydbus import SystemBus

BLUEZ_SERVICE = 'org.bluez'
BLUEZ_DEV_IFACE = 'org.bluez.Device1'
BLUEZ_CHR_IFACE = 'org.bluez.GattCharacteristic1'

class PyDbusBackend:
    @classmethod
    def start(cls):
        """Mock function to match pygatt lib"""
        pass

    @classmethod
    def stop(cls):
        """Mock function to match pygatt lib"""
        pass

    @classmethod
    def connect(cls, device_address):
        """Create device object and connect"""
        device = PyDbusDevice(device_address)
        device.connect()
        return device


class PyDbusDevice:

    def __init__(self, address):
        self.bus = SystemBus()
        self.mngr = self.bus.get(BLUEZ_SERVICE, '/')
        self.dev_path = self._from_device_address(address)
        self.device = self.bus.get(BLUEZ_SERVICE, self.dev_path)

    def _from_device_address(self, addr):
        """Look up D-Bus object path from device address"""
        mng_objs = self.mngr.GetManagedObjects()
        for path in mng_objs:
            dev_addr = mng_objs[path].get(BLUEZ_DEV_IFACE, {}).get('Address', '')
            if addr.casefold() == dev_addr.casefold():
                return path

    def _from_gatt_uuid(self, uuid):
        """Look up D-Bus object path for characteristic UUID"""
        mng_objs = self.mngr.GetManagedObjects()
        for path in mng_objs:
            chr_uuid = mng_objs[path].get(BLUEZ_CHR_IFACE, {}).get('UUID')
            if path.startswith(self.dev_path) and chr_uuid == uuid.casefold():
                return path

    def connect(self):
        """
        Connect to device.
        Wait for GATT services to be resolved before returning
        """
        self.device.Connect()
        while not self.device.ServicesResolved:
            sleep(0.5)

    def disconnect(self):
        """Disconnect from device"""
        self.device.Disconnect()

    def char_write(self, uuid, value):
        """Write value to given GATT characteristic UUID"""
        char_path = self._from_gatt_uuid(uuid)
        char = self.bus.get(BLUEZ_SERVICE, char_path)
        char.WriteValue(value, {})

    def char_read(self, uuid):
        """Read value of given GATT characteristic UUID"""
        char_path = self._from_gatt_uuid(uuid)
        char = self.bus.get(BLUEZ_SERVICE, char_path)
        return char.ReadValue({})

