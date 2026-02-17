# Scrap-Mechanic-Compiler
Compiles simple code into a blueprint that uses logic gates to follow your instructions.

See this example code which could be used for a rocket (With lights for some reason):
```
Output Thrusters
Output Light
Output Bomb
ButtonInput Button

Function Launch:
	Wait 3 seconds
	Enable Thrusters
	Enable Light

	Wait 6 seconds
	Disable Thrusters

	Wait 3 seconds
	Enable Bomb
Done

When Button Run Launch
```

The `Output` creates a logic gate that can be controlled with code
The `ButtonInput` creates a logic gate that you can attach a button to to do something

In the code above there is just one thing that happens triggered by one button.
When the button is pressed the code will:
- Wait 3 seconds
- Turn on the Thruster and Light logic gates
- Wait 6 seconds
- Turn off the Thruster logic gate
- Enable the Bomb logic gate

Hopefull this is pretty obvious but whatever.

You need to connect the inputs and outputs to the things they are suppost to be triggered by.
The output logic gates are red, and the input logic gates are light blue.

The inputs and outputs are also on a diffrent row to all te other logic gates which do the processing.

See `example code/Ordinator.txt` for another example of how to use.

#### This is a work in progress
It does work right now but i have some plans:
- [x] Make it so you can run other function from inside a function
- [x] Right now the logic gates are just lined up, so make them into a box or something more space efficient
- [ ] Make it easier to use
- [ ] Add a logic gates simulation to test the output

Also shows a picture of what the blueprint looks like:

<img width="351" height="419" alt="Screenshot from 2026-02-17 01-57-22" src="https://github.com/user-attachments/assets/c0a463f3-c724-4658-8567-e488a27df4d5" />
