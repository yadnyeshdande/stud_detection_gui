import pyhid_usb_relay

relay = pyhid_usb_relay.find()
relay.set_state(1, False)
relay.set_state(2, False)
