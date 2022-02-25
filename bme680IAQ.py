import numpy as np
import bme680
	

class IAQTracker:
	def __init__(self, burn_in_cycles = 300, gas_recal_period = 3600, ph_slope = 0.03):
		self.slope = ph_slope
		self.burn_in_cycles = burn_in_cycles		#determines burn-in-time, usually 5 minutes, equal to 300 cycles of 1s duration
		self.gas_cal_data = []
		self.gas_ceil = 0
		self.gas_recal_period = gas_recal_period	#number of cycles after which to drop last entry of the gas calibration list. Here: 1h
		self.gas_recal_step = 0
	
	
	
	
	#calculates the saturation water density of air at the current temperature (in °C)
	#return the saturation density rho_max in kg/m^3
	#this is equal to a relative humidity of 100% at the current temperature 
	def waterSatDensity(self, temp):
		rho_max = (6.112* 100 * np.exp((17.62 * temp)/(243.12 + temp)))/(461.52 * (temp + 273.15))
		return rho_max
	
		
		
	def getIAQ(self, bme_data):
		temp = bme_data.temperature
		press = bme_data.pressure
		hum = bme_data.humidity
		R_gas = bme_data.gas_resistance
		
		
		#calculate stauration density and absolute humidity
		rho_max = self.waterSatDensity(temp)
		hum_abs = hum * 10 * rho_max
		
		#compensate exponential impact of humidity on resistance
		comp_gas = R_gas * np.exp(self.slope * hum_abs)
		
		if self.burn_in_cycles > 0:
			#check if burn-in-cycles are recorded
			self.burn_in_cycles -= 1		#count down cycles
			if comp_gas > self.gas_ceil:	#if value exceeds current ceiling, add to calibration list and update ceiling
				self.gas_cal_data = [comp_gas]
				self.gas_ceil = comp_gas
			return None			#return None type as sensor burn-in is not yet completed
		else:
			#adapt calibration
			if comp_gas > self.gas_ceil:
				self.gas_cal_data.append(comp_gas)
				if len(self.gas_cal_data) > 100:
					del self.gas_cal_data[0]
				self.gas_ceil = np.mean(self.gas_cal_data)
			
			
			#calculate and print relative air quality on a scale of 0-100%
			#use quadratic ratio for steeper scaling at high air quality
			#clip air quality at 100%
			AQ = np.minimum((comp_gas / self.gas_ceil)**2, 1) * 100
			
			
			
			#for compensating negative drift (dropping resistance) of the gas sensor:
			#delete oldest value from calibration list and add current value
			self.gas_recal_step += 1
			if self.gas_recal_step >= self.gas_recal_period:
				self.gas_recal_step = 0
				self.gas_cal_data.append(comp_gas)
				del self.gas_cal_data[0]
				self.gas_ceil = np.mean(self.gas_cal_data)
		
		
		return AQ
