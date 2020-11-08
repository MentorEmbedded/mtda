# ---------------------------------------------------------------------------
# HomeKit support for MTDA
# ---------------------------------------------------------------------------
#
# This software is a part of MTDA.
# Copyright (c) Mentor, a Siemens business, 2017-2020
#
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------


# System imports
import abc
from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
import pyhap.const as Category

# Local imports
from mtda.assistant.assistant import Assistant


class PowerSwitch(Accessory):
    category = Category.CATEGORY_OUTLET

    def __init__(self, mtda, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mtda = mtda

        serv_switch = self.add_preload_service('Outlet')
        self.relay_on = serv_switch.configure_char(
            'On', setter_callback=self.set_relay)

        self.relay_in_use = serv_switch.configure_char(
            'OutletInUse', setter_callback=self.get_relay_in_use)

    def get_relay(self, status=None):
        if status is None:
            status = self.mtda.target_status()
        return "1" if status == "ON" else 0

    def relay_changed(self, status):
        self.mtda.debug(3, "mtda.assistant.homekit.relay_changed(%s)" % status)

        result = self.get_relay(status)
        self.relay_on.set_value(result)

        self.mtda.debug(3, "mtda.assistant.homekit.relay_changed(): "
                           "%s" % str(result))
        return result

    def set_relay(self, state):
        self.mtda.debug(3, "mtda.assistant.homekit.set_relay()")

        result = self.get_relay()
        if result != state:
            if state == 1:
                self.mtda.target_on('homekit')
            else:
                self.mtda.target_off('homekit')
            result = self.get_relay()

        self.mtda.debug(3, "mtda.assistant.homekit.set_relay(): "
                           "%s" % str(result))
        return result

    def get_relay_in_use(self, state):
        return True

    def setup_message(self):
        self.mtda.debug(3, "mtda.assistant.homekit.setup_message()")

        pincode = self.driver.state.pincode.decode()
        result = self.mtda.env_set('homekit-setup-code', pincode, 'homekit')

        self.mtda.debug(3, "mtda.assistant.homekit.setup_message(): "
                           "%s" % str(result))
        return result


class HomeKitAssistant(Assistant):

    def __init__(self, mtda):
        self.mtda = mtda
        self.accessory = None
        self.name = "MTDA"
        self.port = 51826

    def configure(self, conf):
        if 'name' in conf:
            self.name = conf['name']
        if 'port' in conf:
            self.port = int(conf['port'], 10)

    def probe(self):
        return True

    def power_changed(self, status):
        self.accessory.relay_changed(status)

    def start(self):
        drv = AccessoryDriver(port=self.port)
        self.accessory = PowerSwitch(self.mtda, drv, self.name)
        drv.add_accessory(self.accessory)
        drv.start_service()


def instantiate(mtda):
    return HomeKitAssistant(mtda)
