import time
from Navi import *
from NaviUtils import *

robotId = 'CarTest'
sessionId = 'TESTSESS_003'

navi = Navi('/home/dehann/Documents/synchronyConfig.json')
# check the server is alive
navi.printStatus()
print ''

# configure the robot and session
robot = registerRobot(navi, robotId)
session = registerSession(navi, robotId, sessionId)


img_request = BigDataElementRequest('pexels_small.png', 'TestImage', 'test image', None, 'image/png')
img_request.ReadImageIntoDataRequest('/home/dehann/software/SynchronySDK_py/data/pexels_small.png')
print 'starting loop'
for i in xrange(0,1):
    delta_measurement = np.array([[10.0], [0], [np.pi/3.0]])
    p_odo = np.array([[0.1, 0.0, 0.0],[0.0, 0.1, 0.0],[0.0, 0.0, 0.1]])
    print ' - Measurement', i, ': Adding new odometry measurement:'
    print delta_measurement

    add_odo_response = addNodeFactor_OdoNormal(navi, time.time(), robotId, sessionId, delta_measurement, p_odo)
    print ''

    print ' - Adding image data to the pose...'
    navi.addOrUpdateDataElement(robotId, sessionId, add_odo_response.variable, img_request)


# add a landmark with a loop closure betwen x1 and x6
addNode_landmark(navi, robotId, sessionId, "l1")

addFactor_BearingRangeNormal(navi, robotId, sessionId, "x1", "l1", 0.0, 20.0)


for i in xrange(1,2):
    delta_measurement = np.array([[10.0], [0], [np.pi/3.0]])
    p_odo = np.array([[0.1, 0.0, 0.0],[0.0, 0.1, 0.0],[0.0, 0.0, 0.1]])
    print ' - Measurement', i, ': Adding new odometry measurement:'
    print delta_measurement

    add_odo_response = addNodeFactor_OdoNormal(navi, time.time(), robotId, sessionId, delta_measurement, p_odo)
    print ''

    print ' - Adding image data to the pose...'
    navi.addOrUpdateDataElement(robotId, sessionId, add_odo_response.variable, img_request)


addNode_landmark(navi, robotId, sessionId, "l2")

addFactor_BearingRangeNormal(navi, robotId, sessionId, "x1", "l2", 0.0, 20.0)


for i in xrange(2,6):
    delta_measurement = np.array([[10.0], [0], [np.pi/3.0]])
    p_odo = np.array([[0.1, 0.0, 0.0],[0.0, 0.1, 0.0],[0.0, 0.0, 0.1]])
    print ' - Measurement', i, ': Adding new odometry measurement:'
    print delta_measurement

    add_odo_response = addNodeFactor_OdoNormal(navi, time.time(), robotId, sessionId, delta_measurement, p_odo)
    print ''

    print ' - Adding image data to the pose...'
    navi.addOrUpdateDataElement(robotId, sessionId, add_odo_response.variable, img_request)


addFactor_BearingRangeNormal(navi, robotId, sessionId, "x6", "l1", 0.0, 20.0)



# tell the solver all these new nodes are ready to be solved
navi.putReady(robotId, sessionId, True)
print 'finished uploading session!!!'

# initial versions of solves are slow, so dont be in a too much of a hurry just yet
sessionLatest = navi.getSession(robotId, sessionId)
# while session.lastSolvedTimestamp != sessionLatest.lastSolvedTimestamp:
#     print 'Comparing latest session solver timestamp $(sessionLatest.lastSolvedTimestamp) with original $(session.lastSolvedTimestamp) - still the same so sleeping for 2 seconds'
#     time.sleep(2)
#     sessionLatest = navi.getSession(robotId, sessionId)


# Inspect the contects of the nodes at any time!
nodes = navi.getNodes(robotId, sessionId)


# By Synchrony label
node = navi.getNode(robotId, sessionId, nodes.nodes.__list__[0].label)
# node = navi.getNode(robotId, sessionId, nodes.nodes.__list__[0].id) # By NeoID


print 'done.'
