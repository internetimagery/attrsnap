# Attrsnap

A Maya tool that assists in "sticking" objects to positions using non-standard attributes.
The tool calculates its position by brute force, so it is highly universal.

# Installation:

Simply copy the folder into your scripts directory in Maya. The folder should be named "attrsnap". Rename it to that if it is not.

# Usage

Within Maya, create a shelf icon with the following PYTHON code:

	import attrsnap
	attrsnap.GUI()

![Screenshot](screen.jpg)

* Begin by taking two points you wish to keep as close as possible to each other. Often it is easiest to contrain some locators to the spots you wish to connect and choose them. For example, you could constrain a locator to a knee bone, and have another sitting on the surface of an object, if you wish to have the knee stick to the surface.

* Select both objects (locators perhaps) and click "Load Objects" button.

* The button now turns into "Load Attribute" button.

* Select the attributes of objects you wish to use in order to move the two objects close together. Remember that this snapping is computationally intesive. The more attributes you use, the longer it will take. Often it's best to animate the objects very close by hand, and then stick them with only a couple attributes.

* Be sure to adjust the range values of the attributes to something reasonable. You can manually move the attribute, while watching the objects move on screen to get an idea of what range you want the tool to check in. The narrower the range, the better and faster the tool will run.

* Select a range in the timeslider if you wish to snap on multiple frames, or else move to the single frame you wish snap on.

* Click "Run Scan" to begin snapping the objects.

NOTE: Try not to have many rotation attributes at once. They can get unwieldy.
NOTE: If the scan is not quite accurate enough, or is having some trouble. You can play with the values in "Accuracy" and "Steps" to narrow the search.


