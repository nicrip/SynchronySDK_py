import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import json
import urllib3.contrib.pyopenssl
import ast
import base64
import numpy as np

urllib3.contrib.pyopenssl.inject_into_urllib3()

class RobotRequest(object):
    def __init__(self, id, name, description, status):
        self.id = id
        self.name = name
        self.description = description
        self.status = status

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class SessionDetailsRequest(object):
    def __init__(self, id, description, initial_pose_type="", should_initialize=True):
        self.id = id
        self.description = description
        self.initialPoseType = initial_pose_type
        self.shouldInitialize = should_initialize

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class BigDataElementRequest(object):
    def __init__(self, id, source_name, description, data, mime_type):
        self.id = id
        self.sourceName = source_name
        self.description = description
        self.data = data
        self.mimeType = mime_type

    def ReadImageIntoDataRequest(self, img_file):
        with open(img_file,'rb') as f:
            img = f.read()
        self.data = base64.b64encode(img)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class AddOdometryRequest(object):
    def __init__(self, timestamp, delta_measurement, p_odo, N=None):
        self.timestamp = timestamp
        self.deltaMeasurement = (delta_measurement.flatten().tolist())
        self.pOdo = (p_odo.T.tolist())
        self.N = N

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class Navi(object):
    def __init__(self, json_auth):
        with open(json_auth) as f:
            auth_info = json.load(f)
            self.url = auth_info['apiEndpoint']
            self.user_name = auth_info['userId']
            host = self.url.split('/')[2]
            self.navi_auth = AWSRequestsAuth(aws_access_key=auth_info['accessKey'],
                                           aws_secret_access_key=auth_info['secretKey'],
                                           aws_host=host,
                                           aws_region=auth_info['region'],
                                           aws_service='execute-api')

        #endpoints
        self.status_endpoint = "api/v0/status"
        self.robots_endpoint = "api/v0/users/{1}/robots"
        self.robot_endpoint = "api/v0/users/{1}/robots/{2}"
        self.sessions_endpoint = "api/v0/users/{1}/robots/{2}/sessions"
        self.session_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}"
        self.odo_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/odometry"

    def getStatus(self):
        request = self.url + '/' + self.status_endpoint
        response = requests.get(request, auth=self.navi_auth)
        return str(response.content)

    def printStatus(self):
        print self.getStatus()

    def getRobots(self):
        request = self.url + '/' + self.robots_endpoint
        request = request.replace("{1}", self.user_name)
        response = requests.get(request, auth=self.navi_auth)
        return json.loads(response.content)

    def getRobot(self, robotId):
        request = self.url + '/' + self.robot_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        response = requests.get(request, auth=self.navi_auth)
        return json.loads(response.content)

    def addRobot(self, robotRequest):
        request = self.url + '/' + self.robot_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotRequest.id)
        response = requests.post(request, data=robotRequest.toJSON(), auth=self.navi_auth)
        return json.loads(response.content)

    def isRobotExisting(self, robotId):
        robots = self.getRobots()['robots']
        existing = False
        for i,robot in enumerate(robots):
            if robot['id'] == robotId:
                existing = True
        return existing

    def getSessions(self, robotId):
        request = self.url + '/' + self.sessions_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        response = requests.get(request, auth=self.navi_auth)
        return json.loads(response.content)

    def getSession(self, robotId, sessionId):
        request = self.url + '/' + self.session_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        response = requests.get(request, auth=self.navi_auth)
        return json.loads(response.content)

    def addSession(self, robotId, sessionDetailsRequest):
        request = self.url + '/' + self.session_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionDetailsRequest.id)
        response = requests.post(request, data=sessionDetailsRequest.toJSON(), auth=self.navi_auth)
        return json.loads(response.content)

    def isSessionExisting(self, robotId, sessionId):
        sessions = self.getSessions(robotId)['sessions']
        existing = False
        for i,session in enumerate(sessions):
            if session['id'] == sessionId:
                existing = True
        return existing

    def addOdometryMeasurement(self, robotId, sessionId, addOdoRequest):
        request = self.url + '/' + self.odo_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        print request
        print addOdoRequest.toJSON()
        response = requests.post(request, data=addOdoRequest.toJSON(), auth=self.navi_auth)
        print response
        return json.loads(response.content)

import time

navi = Navi('./synchronyConfig.json')

navi.printStatus()
print ''

robotId = 'PythonBot'

if (navi.isRobotExisting(robotId)):
    robot = navi.getRobot(robotId)
    print 'robot exists!'
else:
    new_robot = RobotRequest(robotId, 'My New Python Bot', 'Description of my neat Python robot', 'Active')
    robot = navi.addRobot(new_robot)
    print 'adding new robot...'
print robot
print ''

sessionId = 'PythonSession'

if (navi.isSessionExisting(robotId, sessionId)):
    session = navi.getSession(robotId, sessionId)
    print 'session exists!'
else:
    new_session = SessionDetailsRequest(sessionId,'A test Python session','Pose2')
    session = navi.addSession(robotId, new_session)
    print 'adding new session...'
print session
print ''

img_request = BigDataElementRequest('navability_img.png', 'TestImage', 'NavAbility logo', None, 'image/png')
img_request.ReadImageIntoDataRequest('/home/rypkema/Desktop/navibility2.png')
for i in xrange(0,6):
    delta_measurement = np.array([[10.0], [0], [np.pi/3.0]])
    p_odo = np.array([[0.1, 0.0, 0.0],[0.0, 0.1, 0.0],[0.0, 0.0, 0.1]])
    print ' - Measurement', i, ': Adding new odometry measurement:'
    print delta_measurement, '...'

    new_odometry_measurement = AddOdometryRequest(str(time.time()),delta_measurement,p_odo)
    add_odo_response = navi.addOdometryMeasurement(robotId, sessionId, new_odometry_measurement)