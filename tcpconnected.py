
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import untangle

from urllib.parse import quote

# Required for non-https traffic
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Device:
    did = None
    name = None
    on = None
    brightness = None

    def __init__ (self, did, name, on, brightness):
        self.did = did
        self.name = name
        self.on = on
        self.brightness = brightness

    def getDid (self):
        return self.did

    def getName (self):
        return self.name

    def isOn (self):
        return self.on

    def getBrightness (self):
        return self.brightness

    def update (self, device):
        self.did = device.getDid()
        self.name = device.getName()
        self.on = device.isOn()
        self.brightness = device.getBrightness()

    def __str__ (self):
        return '%s (%d) is %s with brightness of %d' % (self.name, self.did, 'on' if self.on else 'off', self.brightness)

class Room:
    rid = None
    name = None
    devices = []

    def __init__ (self, rid, name, devices):
        self.rid = rid
        self.name = name
        self.devices = devices
    
    def getRid (self):
        return self.rid

    def getName (self):
        return self.name

    def getDevices (self):
        return self.devices

class Gateway:
    host = None
    token = None
    apiSession = None

    def __init__ (self, host, token):
        self.host = host
        self.token = token
        self.apiSession = requests.Session()

    def formatCommand(self, command, commandString):
        requestString = 'cmd=%s&data=%s&fmt=xml'
        return requestString % (command, quote(commandString))

    def makeApiRequest (self, payload):
        r = self.apiSession.post('https://%s/gwr/gop.php' % self.host, data=payload, verify=False)
        obj = untangle.parse(r.text)

        return obj

    def getState (self):
        getStateCommand = '<gwrcmds><gwrcmd><gcmd>RoomGetCarousel</gcmd><gdata><gip><version>1</version><token>%s</token><fields>name,control,power,product,class,realtype,status</fields></gip></gdata></gwrcmd></gwrcmds>'

        commandString = getStateCommand % self.token
        
        response = self.makeApiRequest(self.formatCommand('GWRBatch', commandString))
        
        rooms = []
        for roomData in response.gwrcmds.gwrcmd.gdata.gip.room:
            devices = []
            for deviceData in roomData.device:
                if 'offline' not in dir(deviceData):
                    did = int(deviceData.did.cdata)
                    name = deviceData.name.cdata
                    state = bool(int(deviceData.state.cdata))
                    level = int(deviceData.level.cdata)

                    device = Device(did, name, state, level)
                    devices.append(device)
            
            room = Room(int(roomData.rid.cdata), roomData.name.cdata, devices)
            rooms.append(room)
            
        return rooms

    def printState (self):
        rooms = self.getState()

        for room in rooms:
            print('%s (%d)' % (room.getName(), room.getRid()))
            
            for device in room.getDevices():
                print('  - %s (%d)' % (device.getName(), device.getDid()))

    def sendDeviceCommand (self, device, status):
        sendDeviceCommandString = '<gip><version>1</version><token>%s</token><did>%s</did><value>%s</value></gip>'
        sendDeviceLevelCommandString = '<gip><version>1</version><token>%s</token><did>%s</did><value>%s</value><type>level</type></gip>'
        
        if isinstance(status, bool):
            if status:
                commandString = sendDeviceCommandString % (self.token, device.getDid(), '1')
            else:
                commandString = sendDeviceCommandString % (self.token, device.getDid(), '0')
        else:
            commandString = sendDeviceLevelCommandString % (self.token, device.getDid(), '%d' % status)

        return self.makeApiRequest(self.formatCommand('DeviceSendCommand', commandString))

    def turnOnDevice (self, device):
        self.sendDeviceCommand(device, True)

    def turnOffDevice (self, device):
        self.sendDeviceCommand(device, False)

    def setDeviceLevel (self, device, level):
        self.sendDeviceCommand(device, level)

    def sendRoomCommand (self, room, status):
        sendRoomCommandString = '<gip><version>1</version><token>%s</token><rid>%s</rid><value>%s</value></gip>'
        sendRoomLevelCommandString = '<gip><version>1</version><token>%s</token><rid>%s</rid><value>%s</value><type>level</type></gip>'
        
        if isinstance(status, bool):
            if status:
                commandString = sendRoomCommandString % (self.token, room.getRid(), '1')
            else:
                commandString = sendRoomCommandString % (self.token, room.getRid(), '0')
        else:
            commandString = sendRoomLevelCommandString % (self.token, room.getRid(), '%d' % status)

        return self.makeApiRequest(self.formatCommand('RoomSendCommand', commandString))

    def turnOnRoom (self, room):
        self.sendRoomCommand(room, True)

    def turnOffRoom (self, room):
        self.sendRoomCommand(room, False)

    def setRoomLevel (self, room, level):
        self.sendRoomCommand(room, level)

class Session:
    host = None
    token = None
    gateway = None
    rooms = None

    def __init__ (self, host, token):
        self.host = host
        self.token = token
        self.gateway = Gateway(host, token)
        
        self.updateState()

    def updateState(self):
        rooms = self.gateway.getState()

        if self.rooms is None:
            self.rooms = rooms
        else:
            for room in rooms:
                for device in room.getDevices():
                    oldDevice = self.findDeviceByDid(device.getDid())
                    if oldDevice is not None:
                        oldDevice.update(device)

    def findDeviceByDid(self, did):
        result = None

        for room in self.rooms:
            for device in room.getDevices():
                if did == device.getDid():
                    result = device

        return result

    def getGateway(self):
        return self.gateway

    def getRooms(self):
        return self.rooms

def getlights():
    token = ''
    session = Session('ip', token)
    for room in session.rooms:
        for device in room.getDevices():
            print(device)

