import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import json
import urllib3.contrib.pyopenssl
import ast
import base64
import numpy as np
import pprint

urllib3.contrib.pyopenssl.inject_into_urllib3()

# note: recurses through a json string, continuously unpacking the dictionary as attributes of the class
class GenericResponse(list):
    def __init__(self, json_str):
        if isinstance(json_str, dict):
            self.__dict__ = json_str
            self.__list__ = []
        elif isinstance(json_str, list):
            self.__list__ = json_str
        else:
            json_val = json.loads(json_str)
            if isinstance(json_val, dict):
                self.__dict__ = json_val
                self.__list__ = []
            elif isinstance(json_val, list):
                self.__list__ = json_val
        for d in self.__dict__:
            if (d == '__list__'):
                continue
            try:
                self.__dict__[d] = GenericResponse(self.__dict__[d])
            except:
                pass
        for i,l in enumerate(self.__list__):
            try:
                self.__list__[i] = GenericResponse(l)
            except:
                pass

    def __str__(self, level=0):
        tabinto = ' ' * (level*4)
        printstr = ''
        for d in self.__dict__:
            if (d == '__list__'):
                if len(self.__dict__[d]) > 0:
                    printstr += tabinto + '__list__:\n'
                    printstr += tabinto + '[\n'

                    for i,val in enumerate(self.__dict__[d]):
                        printstr += tabinto + '[\n'
                        if isinstance(val, GenericResponse):
                            added_str = val.__str__(level+1)
                        else:
                            added_str = str(val)
                        printstr += tabinto +  added_str.rstrip() + '\n'
                        printstr += tabinto + ']\n'

                    printstr += tabinto +  ']'
            else:
                if isinstance(self.__dict__[d], GenericResponse):
                    added_str = self.__dict__[d].__str__(level+1)
                else:
                    added_str = str(self.__dict__[d])
                printstr += tabinto +  str(d) + ':\n'
                printstr += tabinto +  added_str.rstrip() + '\n'
        return printstr

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
        self.deltaMeasurement = delta_measurement.flatten().tolist()
        self.pOdo = p_odo.T.tolist()
        self.N = N

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class VariableRequest(object):
    def __init__(self, label, variable_type, labels, N=None):
        self.label = label
        self.variableType = variable_type
        self.labels = labels
        self.N = N

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class DistributionRequest(object):
    def __init__(self, dist_type, params):
        self.distType = dist_type
        self.params = params.flatten().tolist()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class BearingRangeRequest(DistributionRequest):
    def __init__(self, pose2Id, point2Id, bearing, range):
        self.pose2Id = pose2Id
        self.point2Id = point2Id
        self.bearing = bearing
        self.range = range

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

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
        self.nodes_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/nodes"
        self.node_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/nodes/{4}"
        self.node_labelled_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/nodes/labelled/{4}"
        self.odo_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/odometry"
        self.big_data_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/nodes/{4}/data"
        self.big_data_element_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/nodes/{4}/data/{5}"
        self.big_data_raw_element_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/nodes/{4}/data/{5}/raw"
        self.variable_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/variables/{4}"
        self.factors_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/factors"
        self.factor_endpoint = "$factorsEndpoint/{4}"
        self.bearing_range_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/factors/bearingrange"
        self.session_ready_endpoint = "api/v0/users/{1}/robots/{2}/sessions/{3}/ready/{4}"

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
        return GenericResponse(response.content)

    def getRobot(self, robotId):
        request = self.url + '/' + self.robot_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        response = requests.get(request, auth=self.navi_auth)
        return GenericResponse(response.content)

    def addRobot(self, robotRequest):
        request = self.url + '/' + self.robot_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotRequest.id)
        response = requests.post(request, data=robotRequest.toJSON(), auth=self.navi_auth)
        return GenericResponse(response.content)

    def isRobotExisting(self, robotId):
        robots = self.getRobots().robots
        existing = False
        for i,robot in enumerate(robots.__list__):
            if robot.id == robotId:
                existing = True
        return existing

    def getSessions(self, robotId):
        request = self.url + '/' + self.sessions_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        response = requests.get(request, auth=self.navi_auth)
        return GenericResponse(response.content)

    def getSession(self, robotId, sessionId):
        request = self.url + '/' + self.session_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        response = requests.get(request, auth=self.navi_auth)
        return GenericResponse(response.content)

    def addSession(self, robotId, sessionDetailsRequest):
        request = self.url + '/' + self.session_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionDetailsRequest.id)
        response = requests.post(request, data=sessionDetailsRequest.toJSON(), auth=self.navi_auth)
        return GenericResponse(response.content)

    def isSessionExisting(self, robotId, sessionId):
        sessions = self.getSessions(robotId).sessions
        existing = False
        for i,session in enumerate(sessions.__list__):
            if session.id == sessionId:
                existing = True
        return existing

    def addOdometryMeasurement(self, robotId, sessionId, addOdoRequest):
        request = self.url + '/' + self.odo_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        response = requests.post(request, data=addOdoRequest.toJSON(), auth=self.navi_auth)
        return GenericResponse(response.content)

    def getDataEntries(self, robotId, sessionId, nodeId):
        request = self.url + '/' + self.big_data_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        request = request.replace("{4}", str(nodeId))
        response = requests.get(request, auth=self.navi_auth)
        return GenericResponse(response.content)

    def addOrUpdateDataElement(self, robotId, sessionId, node, dataElement):
        if isinstance(node, (int,long)):
            nodeId = node
        elif isinstance(node, GenericResponse):
            nodeId = node.id
        data_entries = self.getDataEntries(robotId, sessionId, nodeId)
        data_exists = False
        for i,entry in enumerate(data_entries.__list__):
            if entry.id == dataElement.id:
                data_exists = True
        if data_exists:
            print 'Existence test for ID', dataElement.id, 'passed - Updating it!'
            self.updateDataElement(robotId, sessionId, nodeId, dataElement)
        else:
            print 'Existence test for ID', dataElement.id, 'failed - Adding it!'
            self.addDataElement(robotId, sessionId, nodeId, dataElement)

    def addDataElement(self, robotId, sessionId, nodeId, dataElement):
        request = self.url + '/' + self.big_data_element_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        request = request.replace("{4}", str(nodeId))
        request = request.replace("{5}", dataElement.id)
        response = requests.post(request, data=dataElement.toJSON(), auth=self.navi_auth)

    def updateDataElement(self, robotId, sessionId, nodeId, dataElement):
        request = self.url + '/' + self.big_data_element_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        request = request.replace("{4}", str(nodeId))
        request = request.replace("{5}", dataElement.id)
        response = requests.put(request, data=dataElement.toJSON(), auth=self.navi_auth)

    def getNodes(self, robotId, sessionId):
        request = self.url + '/' + self.nodes_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        response = requests.get(request, auth=self.navi_auth)
        return GenericResponse(response.content)

    def getNode(self, robotId, sessionId, nodeId):
        if isinstance(nodeId, (int,long)):
            request = self.url + '/' + self.node_endpoint
            request = request.replace("{4}", str(nodeId))
        elif isinstance(nodeId, (unicode,str)):
            request = self.url + '/' + self.node_labelled_endpoint
            request = request.replace("{4}", nodeId)
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        response = requests.get(request, auth=self.navi_auth)
        return GenericResponse(response.content)

    def addVariable(self, robotId, sessionId, variableRequest):
        request = self.url + '/' + self.variable_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        request = request.replace("{4}", variableRequest.label)
        response = requests.post(request, data=variableRequest.toJSON(), auth=self.navi_auth)
        return GenericResponse(response.content)

    def addFactor(self, robotId, sessionId, factorRequest):
        request = self.url + '/' + self.factors_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        response = requests.post(request, data=factorRequest.toJSON(), auth=self.navi_auth)
        return GenericResponse(response.content)

    def addBearingRangeFactor(self, robotId, sessionId, bearingRangeRequest):
        request = self.url + '/' + self.bearing_range_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        response = requests.post(request, data=bearingRangeRequest.toJSON(), auth=self.navi_auth)
        return GenericResponse(response.content)

    def putReady(self, robotId, sessionId, isReady):
        request = self.url + '/' + self.session_ready_endpoint
        request = request.replace("{1}", self.user_name)
        request = request.replace("{2}", robotId)
        request = request.replace("{3}", sessionId)
        request = request.replace("{4}", str(isReady).lower())
        response = requests.put(request, data="", auth=self.navi_auth)