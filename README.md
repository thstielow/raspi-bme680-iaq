# Simplified IAQ calculation with the Bosch bme680
`raspi-bme680-iaq` implemets a basic indoor air quality (IAQ) calculation using the VOC sensitive gas resistance of the Bosch BME680 sensor circumventing the closed source Bosch [BSEC](https://www.bosch-sensortec.com/software-tools/software/bsec/) library.

The IAQ calculation as a percentage value is inspired by the example in the [pimoroni bme60 linrary](https://github.com/pimoroni/bme680-python), where higher percentage values represent higher air quality. In contrast, the [BSEC library](https://www.bosch-sensortec.com/software-tools/software/bsec/) return an IAQ value between 0 and 400, where lower values represent higher air quality.

## How to use
The `IAQTracker` utilizes the bme data structure defined in the [pimoroni driver library](https://github.com/pimoroni/bme680-python). The example also uses the sensor class defined therein for communicatiopn with a BME680 sensor.

On Initialization, the tracker can be handed three parameters: 
- `burn_in_cycles` defined the number of update cycles during the initial burn-in. When polling every second, the usual burn-in time of 5 minutes is equivalent to 300 cycles.
- `gas_recal_period` defines the number of update cycles after which the oldest value is dropped from the calibration list for the ceiling of the gas resistance. THis is done for compensating for long timescale drifts of the sensor.
- `ph_slope` defines the slope of the linear compensation of the logatihmic gas resistance by the present humidity and was determined experimentally by running the sensor in an unused room over longer times and fitting the drift-lines apperaring in the measurement data.

The tracker is updated on ever call of `getIAQ`. As long a the number of `burn_in_cycles` is not yet reached, the return-value will be on `None` type. After that, it will return the IAQ value on a scale between 0 and 100.

## IAQ calculation
For IAQ calculation, both the gas resistance `R_gas` and the ralative humidity `hum` are used from the input measurement object. The latter is used for compensating the logarithmic gas resistance by

``comp_gas = np.log(R_gas) + self.slope * hum``.

The IAQ is then calculted as the ratio between `comp_gas` and the ceiling value `gas_ceil`, which is further squared for a steeper slope at higher air qualities and capped at 100%:

``AQ = np.minimum((comp_gas / self.gas_ceil)**2, 1) * 100``.




## Physical Background
The [BME680 datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf) states in Sec. 4.2 
> The BME680 is a metal oxide-based sensor that detects VOCs by adsorption (and subsequent oxidation/reduction) on its sensitive layer.

The sensor works through a metal-oxide surface, to which a voltage is applied in order to determine the resistance. By heating the oxide layer, activation energy is provided for reactions with air compounds. These reactions lead to a reduction in resistance, which then can be measured.

By researching the web on such types of sensors it becomes apparent, that most of them have an exponential response to the concentration of VOCs, which is most commonly tested with ethanole. Further, the response to a given type of VOC depends strongly on the specific choice of metal oxide as well as the micro-structuring of the surface (see [this article](https://iopscience.iop.org/article/10.1088/1361-6501/aa7443/meta) for a detailed review). Moreover, some sensors are also reactive towards water molecules, which is also the case for the BME680, as described later in Sec. 4.2 of the [BME680 datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf). The choice on how to process the gas resistance readings was informed by these insights.

From the literature it also becomes apparant, that the response to different VOCs is temperature dependent. Hence, polling the BME680 at different heating profiles (which cen easily be switched by the build-in registers) could allow the extraction of further information about the air compounds. This, howerver, would require the knowledge of the exact reaction curves (thath Bosch for sure will keep secret) or access to a controlled measuring chamber.



## Remarks
This is a list of oddities and things to consider I noticed during testing the BME680. 
- In their own example, Bosch themselves use a burn-in-time of 5 minutes with polling every second, which is too short. This cen be seen, when running the [bsec](https://www.bosch-sensortec.com/software-tools/software/bsec/) IAQ example on an arduino mega (which I did). The usual burn-in takes about 10 minutes until the increase in gas resistance slows down enough to allow stable reading. Interestingly, Bosch does not seem to take this into account. The IAQ is set to 25 after the 5 minute burn-in and then drops down to 0. Only after resetting the Arduino and waiting for another 5 minutes one can get sensible readings.
- Both BME280 and BME680 seem to suffer from some kind of self-heating, probably due to heat produced by resistors. Over longer measurement durations, both sensors accumulate an offset of around +1.5°C. Again, Bosch themselves do not compensate for this in the [bsec](https://www.bosch-sensortec.com/software-tools/software/bsec/) example. This self-heating adds on top to the temperature offset induced by the gas sensor heating!
- My humidity compensation is far away from being perfect. This can easily be tested by breating onto the sensor. In this case, the [BSEC](https://www.bosch-sensortec.com/software-tools/software/bsec/) IAQ immediately rises and it is also possible to determine the approx. 4% CO_2 content of the breath. My IAQ, however, is overcompensated by the humidity and ceilings at 100%.

## Requirements
- Python 3.x
- [pimoroni bme680 driver](https://github.com/pimoroni/bme680-python)
