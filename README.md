# Simplifies IAQ calculation with the Bosch bme680
`raspi-bme680-iaq` implemets a basic indoor air quality (IAQ) calculation using the VOC sensitive gas resistance of the Bosch bme680 sensor circumventing the closed cource Bosch [bsec](https://www.bosch-sensortec.com/software-tools/software/bsec/) library.

The IAQ calculation as a percentage value is inspired by the example in the [pimoroni bme60 linrary](https://github.com/pimoroni/bme680-python), where higher percentage values represent higher air quality. In contrast, the [bsec library](https://www.bosch-sensortec.com/software-tools/software/bsec/) return an IAQ value between 0 and 400, where lower values represent higher air quality.

## How to use


[pimoroni driver library](https://github.com/pimoroni/bme680-python)


## Mathematics


## Remarks
This is a list of oddities and things to consider I noticed during testing the bme680. 
- In their own example, Bosch themselves use a burn-in-time of 5 minutes with polling every second, which is too short. This cen be seen, when running the [bsec](https://www.bosch-sensortec.com/software-tools/software/bsec/) IAQ example on an arduino mega (which I did). The usual burn-in takes about 10 minutes until the increase in gas resistance slows down enough to allow stable reading. Interestingly, Bosch does not seem to take this into account. The IAQ is set to 25 after the 5 minute burn-in and then drops down to 0. Only after resetting the Arduino and waiting for another 5 minutes one can get sensible readings.
- Both bme280 and bme680 seem to suffer from some kind of self-heating, probably due to heat produced by resistors. Over longer measurement durations, both sensors accumulate an offset of around +1.5°C. Again, Bosch themselves do not compensate for this in the [bsec](https://www.bosch-sensortec.com/software-tools/software/bsec/) example. This self-heating adds on top to the temperature offset induced by the gas sensor heating!
- My humidity compensation is far away from being perfect. This can easily be tested by breating onto the sensor. In this case, the [bsec](https://www.bosch-sensortec.com/software-tools/software/bsec/) IAQ immediately rises and it is also possible to determine the approx. 4% CO_2 content of the breath. My IAQ, however, is overcompensated by the humidity and ceilings at 100%.

## Requirements
- Python 3.x
- [pimoroni bme680 driver](https://github.com/pimoroni/bme680-python)
