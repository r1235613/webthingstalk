from iottalkpy.dai import DAI
from iottalkpy.dan import DeviceFeature


class DummyDevice(DAI):
    def __init__(
        self,
        api_url,
        device_addr=None,
        device_name=None,
        username=None,
        register_callback=None,
        on_register=None,
        on_deregister=None,
        on_connect=None,
        on_disconnect=None,
        push_interval=1,
        interval=None,
        dummy_sensor_i=None,
        dummy_control_o=None,
    ):
        device_features = {
            "DummySensor-I": DeviceFeature(
                "DummySensor-I", "idf", [None], dummy_sensor_i, None
            ),
            "DummyControl-O": DeviceFeature(
                "DummyControl-O", "odf", [None], None, dummy_control_o
            ),
        }

        super().__init__(
            api_url=api_url,
            device_model="Dummy_Device",
            device_addr=device_addr,
            device_name=device_name,
            persistent_binding=False,
            username=username,
            extra_setup_webpage="",
            device_webpage="",
            profile={},
            register_callback=register_callback,
            on_register=on_register,
            on_deregister=on_deregister,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            push_interval=push_interval,
            interval=interval,
            device_features=device_features,
        )
