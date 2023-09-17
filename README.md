# Eyemergency-HackTheNorth2023
Github repository for my project, Eyemergency, solo submission to the Hack The North 2023 Hackathon.

![alt text](eyemergencylogo.png)

Eyemergency is a cutting-edge eye tracking application designed to detect and respond to emergency situations using intuitive blink patterns. With the power of your eyes, it can trigger life-saving alerts or actions when you need them most. 

If users ever find themselves in a dangerous situation where they are unable to contact the proper emergency services, they can blink the SOS morse code (3 short, 3 long, 3 short) to send a distress signal to a list of emergency contacts. This allows users to reach others in a safe and discreet way, without drawing attention using their voice or body gestures.


# Setup Eyemergency
Here is a list of python packages that will need to be installed prior to running the .py file:
- tkinter
- customtkinter
- adhawkapi
- adhawkapi.frontend
- phonenumbers
- PIL
- geopy.geocoders
- opencage.geocoder
- twilio

This program should in theory run in any python IDE, so long as the correct packages are installed, and the emergencylogo.png is within the file. Of course, you will need a pair of AdHawk MindLink glasses to run the program. If you do manage to get your hands on them, remember to change the serialization number to the one on your glasses:

'''
self._api = adhawkapi.frontend.FrontendApi(ble_device_name='ADHAWK MINDLINK-260')
'''
Line 33, where 260 is replaced by the 3 digit code on your glasses.

Additionally, my Twilio account only has 20$ worth of SMS messages, so use the application sparingly. Each SMS is about 0.0007$.

# Contributors
Built and Developed entirely by Daniel Liu

# Credits
Credits to AdHawk for the glasses, to Thomas Kim for teaching me with some code oversights, to Sarah Li for ideas and inspiration, and all the people at Hack The North 2023.
