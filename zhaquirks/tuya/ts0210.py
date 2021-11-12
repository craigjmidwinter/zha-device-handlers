"""TS0210 vibration sensor."""

from typing import Optional, Tuple, Union
from zhaquirks.tuya import TuyaManufCluster

from zigpy.profiles import zha
from zigpy.quirks import CustomDevice
import zigpy.types as t
from zigpy.zcl import foundation
from zigpy.zcl.clusters.general import Basic, Ota, PowerConfiguration, Time
from zigpy.zcl.clusters.security import IasZone

from zhaquirks import Bus, LocalDataCluster, MotionOnEvent
from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODEL,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
    MOTION_EVENT

)
import logging

_LOGGER = logging.getLogger(__name__)

ZONE_TYPE = 0x0001
IAS_VIBRATION_SENSOR = 0x5F02


class VibrationCluster(LocalDataCluster, MotionOnEvent, IasZone):
    """Tuya Motion Sensor."""

    cluster_id = IasZone.cluster_id
    _CONSTANT_ATTRIBUTES = {ZONE_TYPE: IasZone.ZoneType.Vibration_Movement_Sensor}
    reset_s = 15

    def handle_cluster_request(
        self,
        hdr: foundation.ZCLHeader,
        args: Tuple[TuyaManufCluster.Command],
        *,
        dst_addressing: Optional[
            Union[t.Addressing.Group, t.Addressing.IEEE, t.Addressing.NWK]
        ] = None,
    ) -> None:
        """Handle cluster request."""
        self.endpoint.device.motion_bus.listener_event(MOTION_EVENT)


class TuyaVibration(CustomDevice):
    """Tuya vibration sensor."""

    def __init__(self, *args, **kwargs):
        """Init device."""
        self.motion_bus = Bus()
        super().__init__(*args, **kwargs)

    signature = {
        #   SizePrefixedSimpleDescriptor(endpoint=1, profile=260, device_type=1026, device_version=0, input_clusters=[0, 10, 1, 1280], output_clusters=[25])
        MODEL: "TS0210",
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.IAS_ZONE,
                INPUT_CLUSTERS: [Basic.cluster_id, Time.cluster_id, PowerConfiguration.cluster_id, IasZone.cluster_id],
                OUTPUT_CLUSTERS: [Ota.cluster_id],
            }
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: IAS_VIBRATION_SENSOR,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Time.cluster_id,
                    VibrationCluster
                ],
                OUTPUT_CLUSTERS: [Ota.cluster_id],
            }
        }
    }
