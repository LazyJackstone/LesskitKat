import math
#TODO : Add Send message when Enemy Base destroyed
#TODO: Finir la communication Group : Ordre Base ne peut être interrompu/ Request explorer possiblement interuptible.
class SearchFoeState(object):
    @staticmethod
    def execute():
        setDebugString("SearchFoeState")
        percepts = getPerceptsEnemies()
        if len(percepts)>0:
            selectedPercept = None
            for percept in percepts:
                if isEnemy(percept) and (percept.getType().equals(WarAgentType.WarBase) or percept.getType().equals(WarAgentType.WarExplorer) or percept.getType().equals(WarAgentType.WarRocketLauncher)):
                    setDebugString("ENEMY FOUND")
                    if selectedPercept is None:
                        selectedPercept = percept
                    elif percept.getHealth() < selectedPercept.getHealth():
                        selectedPercept = percept

            if selectedPercept is not None:
                followTarget(selectedPercept)
                if isReloaded():
                    actionWarRocketLauncher.nextState = FiringState
                else :
                    actionWarRocketLauncher.nextState = ReloadingState
            else:
                actionWarRocketLauncher.nextState = SearchFoeState
                setRandomHeading(25)
        else:
            actionWarRocketLauncher.nextState = SearchFoeState
            setRandomHeading(25)

        return move()

class FiringState(object):
    @staticmethod
    def execute():
        setDebugString("Firing State")
        actionWarRocketLauncher.nextState = ReloadingState
        return fire()

class ReloadingState(object): #TODO add resume firing on targeted if setted
    @staticmethod
    def execute():
        setDebugString("Reloading State")
        if isReloaded():
            actionWarRocketLauncher.nextState = SearchFoeState
        else:
            actionWarRocketLauncher.nextState = ReloadingState

        return reloadWeapon()

class WiggleState(object):
    @staticmethod
    def execute():
        setDebugString("WiggleState")
        if (isBlocked()) :
            RandomHeading()
        return move()

class FollowOrderState(object): #TODO : FINIR getting info
    @staticmethod
    def execute() :
        setDebugString("Following Order")
        messages = getMessages()
        if len(messages) > 0 :
            for message in messages :
                if message.getMessage() == "ORDER" :
                    if message.getContent()[0] == "Travel" :
                        movingData = determinateAttacksAngle(float(message.getContent()[1]), float(message.getContent()[2]), message.getAngle(), message.getDistance())
                        setHeading(movingData[0])
                        return move()
                    else :
                        if message.getContent()[1] == "Fire" :
                            if isReloaded():
                                shootingData = determinateAttacksAngle(float(message.getContent()[1]), float(message.getContent()[2]), message.getAngle(), message.getDistance())
                                setHeading(shootingData[0])
                                return fire()
                            else :
                                return reloadWeapon()

        else :
            #TODO :  LeaveGroup + return SearchFoeState
            actionWarRocketLauncher.nextState = FollowOrderState
            return move()

# TODO : Add send message when percept ennemy to other rl which will come to help if they are not busy.
# TODO : Add gestion refus grouping
# TODO : Add when receiving order from base attack destination given without interruption possible
def reflexes() :
    #sendMessageToBases("STATUS", ["RocketLauncher"])
    messages = getMessages()
    print " " + str(getID()) + " " + str(messages)
    for message in messages :
        if message.getMessage() == "REQUEST" :
            if message.getContent()[0] == "Attack Enemy Base" : #NOTE : DEPRECATED
                memory["EnemyBaseAngleFromBase"] = float(message.getContent()[2])#*
                memory["EnemyBaseDistanceFromBase"] = float(message.getContent()[3])#*
                memory["EnemyBaseID"] = message.getContent()[1]
                actionWarRocketLauncher.nextState = FollowOrderState
                enemyBaseData = determinateAttacksAngle( memory["EnemyBaseAngleFromBase"], memory["EnemyBaseDistanceFromBase"], message.getAngle(), message.getDistance())
                setHeading(enemyBaseData[0])
                memory["EnemyBaseDistance"] = enemyBaseData[1]

            if message.getContent()[0] == "Group" :
                print "Got Message"
                if "Group" not in memory :
                    memory["Group"] = message.getContent()[1]
                    reply(message, "INFORM", ["OK"])
                else :
                    reply(message, "INFORM", ["BUSY"])

            if message.getContent()[0] == "Join":
                print "GotJoiningRequest"
                requestRole(message.getContent()[1], "Bidder")
                determinateAttacksAngle()
                setHeading(message.getAngle()) # TODO Add triangulation
                actionWarRocketLauncher.nextState = FollowOrderState

        if message.getMessage() == "INFORM":
            if message.getContent()[0] == "Here":
                memory["AllyBaseAngle"] = message.getAngle()

        #if message.getMessage()== "ASK": #Cas Message ASK

        #if message.getMessage()== "ORDER": #Cas Message ORDER

    if isBlocked():
        RandomHeading()
    return None


def actionWarRocketLauncher():
    result = reflexes() # Reflexes
    if result:
        return result

    # FSM - Changement d'Ã©tat
    actionWarRocketLauncher.currentState = actionWarRocketLauncher.nextState
    actionWarRocketLauncher.nextState = None

    if actionWarRocketLauncher.currentState:
        return actionWarRocketLauncher.currentState.execute()


"""
    Détermine l'angle entre l'unité courante et le percept.
    anglePercept:    Angle entre l'envoyeur du message et le percept
    distancePercept: Distance entre l'envoyeur du message et le percept
    angleMessage:    Angle entre l'envoyeur du message et l'unité courante
    distanceMessage: Distance entre l'envoyeur du message et l'unité courante
"""
def determinateAttacksAngle(anglePercept, distancePercept, angleMessage, distanceMessage):
    vectorCoord1 = calculateCoord(anglePercept, distancePercept)
    vectorCoord2 = calculateCoord(angleMessage, distanceMessage)
    vectorResult = [vectorCoord1[0] + vectorCoord2[0], vectorCoord1[1] + vectorCoord2[1]]
    distance = math.sqrt(vectorResult[0]**2 + vectorResult[1]**2)
    angleRadian = math.atan2(vectorResult[1], vectorResult[0])
    angle = math.degrees(angleRadian)

    return [angle, distance]

"""
    Calcul les coordonnées du point.
"""
def calculateCoord(angle, rayon):
    x = rayon * math.degrees(math.cos(math.radians(angle)))
    y = rayon * math.degrees(math.sin(math.radians(angle)))

    return [x, y]

# Initialisation des variables
actionWarRocketLauncher.nextState = SearchFoeState
actionWarRocketLauncher.currentState = None
memory={}
