# CBPi4 Plugin for Sparge Steps

Still under development and in Beta test phase 

## Simple step for CBPi4 that allows to set a target temp for a kettle. I.e. a HLT or sparge tank


- TempStep:
	- Heats up to the target temp. This can be used to auto heat a HLT or sparge tank. After target temp is set, immediately resume to next step.
	- Parameters:
		- Temp: Target Temp to be set
		- Sensor: Sensor to be used
		- Heater: When target temp is set to 0, auto mode and heater are switched off
		- Kettle: Kettle to be used

- Sparge:
	- Notifies that Mashing is done. Stops sparge or HLT heater and waits for confirmation that sparging process is done
	- Parameters:
		- Heater: (optional) Stops heater on this step
		- Kettle: (optional) Sets kettle target temp to 0 and turns off auto mode

###Changelog:
	
** Initial release

Initial change to sparge specific brew steps

- Added SpargeStep
	Intended to be added after last MashStep.
	Notifies that Mashing is done.
	Stops sparge or HLT heater and waits for confirmation that sparging process is done

- Added TempStep
	Can be used to set a target temp for a kettle and turn on auto mode.
	Doesn't wait for kettle to get up to temp. Just sets the temp and moves to next step.
	Example: Pre-heat a HLT, sparge heater or a boiler
