# convenience functions for navi

from Navi import *

def addNodeFactor_OdoNormal(navi, ts, robotname, sessionname, delta_meas, p_odo):
    new_odometry_measurement = AddOdometryRequest(str(ts),delta_meas,p_odo)
    return navi.addOdometryMeasurement(robotname, sessionname, new_odometry_measurement)

def addNode_landmark(navi, robotname, sessionname, lm):
    new_landmark = VariableRequest(lm, "Point2", ["LANDMARK"])
    return navi.addVariable(robotname, sessionname, new_landmark)

def addFactor_BearingRangeNormal(navi, robotname, sessionname, xi, lj, br, rn, bnoise=0.1, rnoise=1.0):
    newBearingRangeFactor = BearingRangeRequest(xi, lj,
                                                DistributionRequest("Normal", np.array([[br], [0.1]])),
                                                DistributionRequest("Normal", np.array([[rn], [1.0]])))
    navi.addBearingRangeFactor(robotname, sessionname, newBearingRangeFactor)

def registerRobot(navi, robotname):
    if (navi.isRobotExisting(robotname)):
        robot = navi.getRobot(robotname)
        print 'robot exists!'
    else:
        new_robot = RobotRequest(robotname, 'My New Python Bot', 'Description of my neat Python robot', 'Active')
        robot = navi.addRobot(new_robot)
        print 'adding new robot...'
    print robot
    print ''
    return robot

def registerSession(navi, robotname, sessionname):
    if (navi.isSessionExisting(robotname, sessionname)):
        session = navi.getSession(robotname, sessionname)
        print 'session exists!'
    else:
        new_session = SessionDetailsRequest(sessionname,'A test Python session','Pose2')
        session = navi.addSession(robotname, new_session)
        print 'adding new session...'
    print session
    print ''
    return session
