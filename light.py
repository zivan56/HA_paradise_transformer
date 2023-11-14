"""
Light controller for the Northern International Paradise GL33210 Low Voltage Transformer.
This transformer runs in AP mode, and has a fixed address of 192.168.4.1
You need to have the Home Assistant machine connect to the Paradise_XXXXXX wifi network first or have a machine proxy the requests by changing the IP in the code below

Based off the homebridge-paradise code: https://www.npmjs.com/package/homebridge-paradise

"""
from __future__ import annotations
 
import logging
import socket


import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (PLATFORM_SCHEMA,
                                            LightEntity)
#from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)



def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
 
    add_entities([ParadiseLightChannel("CH1"), ParadiseLightChannel("CH2"), ParadiseLightChannel("CH3"), ParadiseLightChannel("120V")])

class ParadiseLightChannel(LightEntity):
    """Representation of an ParadiseLightChannel."""
    
    
    def send_command(self, command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        sock.connect(("192.168.4.1", 8266))
        msg = ""
        if "CH1" in self._name:
            msg+= "L0"
        elif "CH2" in self._name:
            msg+= "L1"
        elif "CH3" in self._name:
            msg+= "L2"
        else:
            msg+= "L3"
            
        if command == "on":
            msg+= "1"
        else:
            msg+= "0"
        
        msg+="\n" 
        _LOGGER.info("send_command(" + self._name + ":" + command + ":" + msg + ")")
        sock.send(msg.encode('ASCII'))
        
        
        
        
        
        
        sock.close    

    def __init__(self, name) -> None:
        # Set name here
        self._name = "Paradise Transformer " + name
        self._state = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        _LOGGER.info("is_on(self)")
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self.send_command("on")
        self._state = True

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self.send_command("off")
        self._state = False

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.info("update(self)")
        #self._light.update()
        #self._state = self._light.is_on()
        msg = "RT\n"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        sock.connect(("192.168.4.1", 8266))
        sock.send(msg.encode('ASCII'))
        response = sock.recv(70).decode("ASCII")
        _LOGGER.info("update(" + self._name +  ":" + msg + ") - "  + response)
        
        if "CH1" in self._name:
            self._state = (response[24] == "1")
        elif "CH2" in self._name:
            self._state = (response[35] == "1")
        elif "CH3" in self._name:
            self._state = (response[46] == "1")
        else:
            self._state = (response[57] == "1")
        
        
        sock.close
 
 
 
