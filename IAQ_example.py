import numpy as np
import bme680
from time import *
from bme680IAQ import *




#BME680 initialization
bme680_temp_offset = -4.5       #temperature oofset: depends on heating profile and external heat sources close to mounting point (i.e. Raspberry Pi SoC)
sensor680 = bme680.BME680(i2c_addr=bme680.I2C_ADDR_SECONDARY)

sensor680.set_humidity_oversample(bme680.OS_1X)
sensor680.set_pressure_oversample(bme680.OS_1X)
sensor680.set_temperature_oversample(bme680.OS_1X)
sensor680.set_filter(bme680.FILTER_SIZE_0)
sensor680.set_gas_status(bme680.ENABLE_GAS_MEAS)

sensor680.set_gas_heater_temperature(320)
sensor680.set_gas_heater_duration(150)
sensor680.select_gas_heater_profile(0)
sensor680.set_temp_offset(bme680_temp_offset)


sensor680.get_sensor_data()



temp = 0
press = 0
hum = 0
R_gas = 0


#data prompt function
def prompt_data(temp, press, hum, Rgas, AQ):	
	out_string = "{0}: {1:.2f}°C, {2:.2f}hPa, {3:.2f}%RH, {4:.1f}kOhm".format(strftime("%Y-%m-%d %H:%M:%S"),temp,press,hum,R_gas/1000)
	if AQ == None:
		out_string += ", cal."
	else:
		out_string += ", {0:.1f}%aq".format(AQ)
	print(out_string)
	

#Initialize IAQ calculator
iaq_tracker = IAQTracker()

#main loop
while True:
	if sensor680.get_sensor_data():
		temp = sensor680.data.temperature
		press = sensor680.data.pressure
		hum = sensor680.data.humidity
		
		
		if sensor680.data.heat_stable:
			R_gas = sensor680.data.gas_resistance
			AQ = iaq_tracker.getIAQ(sensor680.data)
		else:
			R_gas = 0
			AQ = None
			
			
		prompt_data(temp, press, hum, R_gas, AQ)
		
	sleep(1)
