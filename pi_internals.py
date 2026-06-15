'''
    pi_internals.py

    Copyright (c) 2026 Clear Creek Scientific

    References: 
        https://mechatronicslab.net/measuring-the-raspberry-pi-cpu-temperature/
        https://www.tomshardware.com/how-to/raspberry-pi-benchmark-vcgencmd
        https://www.cyberciti.biz/faq/linux-find-out-raspberry-pi-gpu-and-arm-cpu-temperature-command/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
         
'''
import os
import time
import datetime
import xml.etree.ElementTree as et

import ccs_base

NAME                              = 'pi_internals'

LABEL                             = 'pi_internals'
DESCRIPTION                       = 'Raspberry Pi, measured internal values'

THERMAL_ZONE_PATH_PREFIX          = '/sys/class/thermal/thermal_zone'
THERMAL_ZONE_PATH_SUFFIX          = '/temp'


class PiInternals(object):

    def __init__(self):
        self.log_callback = None

    def logmsg(self,msg):
        if None is not self.log_callback:
            self.log_callback(NAME,msg)

    def build_thermal_zone_path(self,id):
        return THERMAL_ZONE_PATH_PREFIX + str(id) + THERMAL_ZONE_PATH_SUFFIX

    # Returns CPU temperature in centigrade
    def get_cpu_temperature(self,id=0):
        rv = 0.0
        path = build_thermal_zone_path(id)
        try:
            with open(path,'rt') as fd:
                buf = fd.read().strip()
                rv = float(buf)/1000.0
        except Exception as ex:
            self.logmsg('Error reading CPU temp: ' + str(ex))
        return rv 

    # Returns GPU temperature in centigrade
    def get_gpu_temperature(self):
        rv = 0.0
        try:
            output = os.popen('vcgencmd measure_temp').readline().strip()
            tstr = output.replace('temp=','').replace("'C",'')
            rv = float(tstr)
        except Exception as ex:
            self.logmsg('Error reading GPU temp: ' + str(ex))
        return rv

    def get_throttled_status(self):
        rv = 0
        try:
            output = os.popen('vcgencmd get_throttled').readline().strip()
            tstr = output.replace('throttled=','')
            rv = int(tstr)
        except Exception as ex:
            self.logmsg('Error reading throttled status: ' + str(ex))
        return rv

    # The following functions implement the interface for a sensor plugin module
    def get_label(self):
        return LABEL 

    def get_description(self):
        return DESCRIPTION 

    def get_uuids(self):
        return (ccs_base.CCS_COMPONENT_TEMPERATURE_UUID,)

    def set_config(self,xml):
        try:
            root = et.fromstring(xml)
        except Exception as ex:
            self.logmsg('Error parsing config: ' + str(ex))

    def set_log_callback(self,callback):
        self.log_callback = callback

    # Returns a tuple of tuples, each containing the uuid of the value 
    # and the value itself expressed as a string representing a floating point number
    def get_current_values(self):
        cpu = self.get_cpu_temperature()
        cpu = (ccs_base.CCS_CPU_TEMPERATURE_UUID,'{:.{}f}'.format(cpu,2))
        gpu = self.get_gpu_temperature()
        gpu = (ccs_base.CCS_GPU_TEMPERATURE_UUID,'{:.{}f}'.format(gpu,2))
        ts = self.get_throttled_status()
        ts = (ccs_base.CCS_PI_THROTTLED_STATUS,f'{ts:x}')
        return (cpu,gpu,ts)

def load():
    return PiInternals()



