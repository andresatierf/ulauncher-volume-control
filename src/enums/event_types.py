from enum import Enum


class EventTypes(Enum):
    MENU = "menu"
    APPLICATION = "application"
    VOLUME = "volume"
    DEVICE = "device"
    PROFILE = "profile"
    CANCEL = "cancel"
