''' Demonstrates how to subscribe to and handle data from gaze and event streams '''

import time
import tkinter

import adhawkapi
import adhawkapi.frontend
import phonenumbers
import customtkinter

from PIL import ImageTk, Image
from geopy.geocoders import Nominatim

from opencage.geocoder import OpenCageGeocode
from twilio.rest import Client

global blink_sequence, tempcontact, emergency_contact_list, personal_name, distress_msg, location, locname, lat, lng, number

SHORT_BLINK_THRESHOLD = 0.19
LONG_BLINK_THRESHOLD = 0.2

Key = '28e8e74cc7504bd3867ee2f6c2884885'
account_sid = 'AC3a014570d40bfc4bd7136f29658dec53'
auth_token = 'f2551e8c6b03c2b10b68e5228e7396e4'
client = Client(account_sid, auth_token)

class FrontendData:
    ''' BLE Frontend '''

    def __init__(self):
        # Instantiate an API object
        # TODO: Update the device name to match your device
        self._api = adhawkapi.frontend.FrontendApi(ble_device_name='ADHAWK MINDLINK-260')

        # Tell the api that we wish to receive eye tracking data stream
        # with self._handle_et_data as the handler
        self._api.register_stream_handler(adhawkapi.PacketType.EYETRACKING_STREAM, self._handle_et_data)

        # Tell the api that we wish to tap into the EVENTS stream
        # with self._handle_events as the handler
        self._api.register_stream_handler(adhawkapi.PacketType.EVENTS, self._handle_events)

        # Start the api and set its connection callback to self._handle_tracker_connect/disconnect.
        # When the api detects a connection to a MindLink, this function will be run.
        self._api.start(tracker_connect_cb=self._handle_tracker_connect,
                        tracker_disconnect_cb=self._handle_tracker_disconnect)

    def shutdown(self):
        '''Shutdown the api and terminate the bluetooth connection'''
        self._api.shutdown()

    @staticmethod
    def _handle_et_data(et_data: adhawkapi.EyeTrackingStreamData):

        ''' Handles the latest et data '''
        if et_data.gaze is not None:
            xvec, yvec, zvec, vergence = et_data.gaze
        #            print(f'Gaze={xvec:.2f},y={yvec:.2f},z={zvec:.2f},vergence={vergence:.2f}')

        if et_data.eye_center is not None:
            if et_data.eye_mask == adhawkapi.EyeMask.BINOCULAR:
                rxvec, ryvec, rzvec, lxvec, lyvec, lzvec = et_data.eye_center
        #                print(f'Eye center: Left=(x={lxvec:.2f},y={lyvec:.2f},z={lzvec:.2f}) '
        #                      f'Right=(x={rxvec:.2f},y={ryvec:.2f},z={rzvec:.2f})')

        if et_data.pupil_diameter is not None:
            if et_data.eye_mask == adhawkapi.EyeMask.BINOCULAR:
                rdiameter, ldiameter = et_data.pupil_diameter
        #                print(f'Pupil diameter: Left={ldiameter:.2f} Right={rdiameter:.2f}')

        if et_data.imu_quaternion is not None:
            if et_data.eye_mask == adhawkapi.EyeMask.BINOCULAR:
                x, y, z, w = et_data.imu_quaternion

    #                print(f'IMU: x={x:.2f},y={y:.2f},z={z:.2f},w={w:.2f}')

    @staticmethod
    def _handle_events(event_type, timestamp, *args):

        if event_type == adhawkapi.Events.BLINK:
            duration = args[0]
            if duration < SHORT_BLINK_THRESHOLD:
                print(f'Short blink: {duration}')
                blink_sequence.append('S')
            elif duration > LONG_BLINK_THRESHOLD:
                print(f'Long blink: {duration}')
                blink_sequence.append('L')
        #            print(f'Got blink: {timestamp} {duration}')

        if len(blink_sequence) > 9:
            blink_sequence.pop(0)

        if len(blink_sequence) == 9:
            pattern = ''.join(blink_sequence[-9:])
            if pattern == 'SSSLLLSSS':
                print('Success')
                blink_sequence.clear()

                for contact in emergency_contact_list:
                    message = client.messages.create(
                        from_='+12569603664',
                        body='DISTRESS ALERT: EYEMERGENCY SOS SIGNAL ACTIVATED! \n\n' + personal_name.get() + ' requires immediate assistance. \n\nCoordinates: ' + str(lat) + ', ' + str(lng) + '\n\nLocation: ' + locname.address + '\n\nCONTACT EMERGENCY MEDICAL SERVICES URGENTLY .',
                        to=contact
                    )

        if event_type == adhawkapi.Events.EYE_CLOSED:
            eye_idx = args[0]
        #            print(f'Eye Close: {timestamp} {eye_idx}')
        if event_type == adhawkapi.Events.EYE_OPENED:
            eye_idx = args[0]

    #            print(f'Eye Open: {timestamp} {eye_idx}')

    def _handle_tracker_connect(self):
        print("Tracker connected")
        self._api.set_et_stream_rate(60, callback=lambda *args: None)

        self._api.set_et_stream_control([
            adhawkapi.EyeTrackingStreamTypes.GAZE,
            adhawkapi.EyeTrackingStreamTypes.EYE_CENTER,
            adhawkapi.EyeTrackingStreamTypes.PUPIL_DIAMETER,
            adhawkapi.EyeTrackingStreamTypes.IMU_QUATERNION,
        ], True, callback=lambda *args: None)

        self._api.set_event_control(adhawkapi.EventControlBit.BLINK, 1, callback=lambda *args: None)
        self._api.set_event_control(adhawkapi.EventControlBit.EYE_CLOSE_OPEN, 1, callback=lambda *args: None)

    def _handle_tracker_disconnect(self):
        print("Tracker disconnected")

def runprogram():
    from phonenumbers import geocoder

    phonenumber = "+1" + number.get()
    # Phone Number location
    check_number = phonenumbers.parse(phonenumber)
    location = geocoder.description_for_number(check_number, "en")
    print(location)

    # Rever Geolocation
    geocoder = OpenCageGeocode(Key)
    query = str(location)
    results = geocoder.geocode(query)
    lat = results[0]['geometry']['lat']
    lng = results[0]['geometry']['lng']
    coordinates = (lat, lng)
    geoLoc = Nominatim(user_agent="GetLoc")
    locname = geoLoc.reverse(coordinates)
    print(locname.address)

    frontend = FrontendData()
    print(personal_name.get())
    print(number.get())

def addcontact():
    newcontact = "+1" + tempcontact.get()
    emergency_contact_list.append(newcontact)
    print(emergency_contact_list)

def quitfunction():
    exit()

# simple tkinter ui
customtkinter.set_appearance_mode('dark')
# customtkinter.set_default_color_theme('red')

root = customtkinter.CTk()
root.geometry('500x650')
root.title('Eyemergency - Stay Safe & in Control')

personal_name = tkinter.StringVar()
tempcontact = tkinter.StringVar()
number = tkinter.StringVar()

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

logo = customtkinter.CTkImage(Image.open("eyemergencylogo.png"), size=(250, 50))
label = customtkinter.CTkLabel(master=frame, image=logo, text='')
label.pack(pady=12, padx=10)

label1 = customtkinter.CTkLabel(master=frame, text='Enter Full Name Below')
label1.pack(pady=6, padx=10)

nameentry = customtkinter.CTkEntry(master=frame, textvariable=personal_name, placeholder_text="Enter your name")
nameentry.pack(pady=6, padx=10)

label2 = customtkinter.CTkLabel(master=frame, text='Enter Phone Number to Connect Location')
label2.pack(pady=6, padx=10)

numbentry = customtkinter.CTkEntry(master=frame, textvariable=number, placeholder_text="Enter your name")
numbentry.pack(pady=6, padx=10)

label3 = customtkinter.CTkLabel(master=frame, text='Add Emergency Contacts Below')
label3.pack(pady=6, padx=10)

contactentry = customtkinter.CTkEntry(master=frame, textvariable=tempcontact, placeholder_text="Enter your name")
contactentry.pack(pady=12, padx=10)

runbutton = customtkinter.CTkButton(master=frame, text="Add Emergency Contact", command=addcontact, fg_color="darkred", hover_color="red")
runbutton.pack(pady=12, padx=10)

addbutton = customtkinter.CTkButton(master=frame, text="Run Eyemergency", command=runprogram, fg_color="darkred", hover_color="red")
addbutton.pack(pady=12, padx=10)

quitbutton = customtkinter.CTkButton(master=frame, text="Exit", command=quitfunction, fg_color="darkred", hover_color="red")
quitbutton.pack(pady=12, padx=10)

label4 = customtkinter.CTkLabel(master=frame, text='Copyright © 2023 Daniel Liu')
label4.pack(pady=6, padx=10)

# Global var initiation
blink_sequence = []
emergency_contact_list = []

root.mainloop()


