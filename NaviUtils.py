# convenience functions for navi

from Navi import *




def addNode(navi, robotname, sessionname, symbol, vartype, labels=[""]):
    new_node = VariableRequest(symbol, vartype, labels)
    return navi.addVariable(robotname, sessionname, new_node)

def addNode_landmark(navi, robotname, sessionname, symbol):
    return addNode(navi, robotname, sessionname, symbol, "Point2", labels=["LANDMARK"])

def addNode_tag2(navi, robotname, sessionname, symbol):
    return addNode(navi, robotname, sessionname, symbol, "Pose2", labels=["LANDMARK","TAG"])

def addNode_pose2(navi, robotname, sessionname, symbol):
    return addNode(navi, robotname, sessionname, symbol, "Pose2", labels=["POSE"])

# def addNode_landmark(navi, robotname, sessionname, lm):
#     new_landmark = VariableRequest(lm, "Point2", ["LANDMARK"])
#     return navi.addVariable(robotname, sessionname, new_landmark)

def addFactor_Pose2Pose2Normal(navi, robotname, sessionname, sym_i, sym_j, mu, sig, labels=[""]):
    packedstr = 
    new_fct_body = FactorBody("Pose2Pose2", "PackedPose2Pose2", "json", packedstr) # TODO what up json
    new_factor = FactorRequest([sym_i, sym_j], ,p_odo)

def addNodeFactor_OdoNormal(navi, ts, robotname, sessionname, delta_meas, p_odo):
    new_odometry_measurement = AddOdometryRequest(str(ts),delta_meas,p_odo)
    return navi.addOdometryMeasurement(robotname, sessionname, new_odometry_measurement)

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
