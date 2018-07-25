import time
from Navi import *

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

sessionId = 'PythonBotSession'

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
    print delta_measurement

    new_odometry_measurement = AddOdometryRequest(str(time.time()),delta_measurement,p_odo)
    add_odo_response = navi.addOdometryMeasurement(robotId, sessionId, new_odometry_measurement)
    print ''

    print ' - Adding image data to the pose...'
    navi.addOrUpdateDataElement(robotId, sessionId, add_odo_response.variable, img_request)

nodes = navi.getNodes(robotId, sessionId)

# By NeoID
node = navi.getNode(robotId, sessionId, nodes.nodes.__list__[0].id)

# By Synchrony label
node = navi.getNode(robotId, sessionId, nodes.nodes.__list__[0].label)

new_landmark = VariableRequest("l1", "Point2", ["LANDMARK"])
response = navi.addVariable(robotId, sessionId, new_landmark)
newBearingRangeFactor = BearingRangeRequest("x1", "l1",
                                            DistributionRequest("Normal", np.array([[0.0], [0.1]])),
                                            DistributionRequest("Normal", np.array([[20.0], [1.0]])))
navi.addBearingRangeFactor(robotId, sessionId, newBearingRangeFactor)
newBearingRangeFactor = BearingRangeRequest("x6", "l1",
                                            DistributionRequest("Normal", np.array([[0.0], [0.1]])),
                                            DistributionRequest("Normal", np.array([[20.0], [1.0]])))
navi.addBearingRangeFactor(robotId, sessionId, newBearingRangeFactor)

navi.putReady(robotId, sessionId, True)

sessionLatest = navi.getSession(robotId, sessionId)
while session.lastSolvedTimestamp != sessionLatest.lastSolvedTimestamp:
    print 'Comparing latest session solver timestamp $(sessionLatest.lastSolvedTimestamp) with original $(session.lastSolvedTimestamp) - still the same so sleeping for 2 seconds'
    time.sleep(2)
    sessionLatest = navi.getSession(robotId, sessionId)

print 'Session solver finished!!!'