import math
#TODO: Check Triangulation // Distance
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
                    return idle()
                else :
                    actionWarRocketLauncher.nextState = ReloadingState
                    return idle()
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

class TravelToEnemyBaseState(object):
    @staticmethod
    def execute() :
        setDebugString("OMW to Enemy Base")
        percepts= getPerceptsEnemiesWarBase()
        targetedBasePercept= None
        if len(percepts) > 0 :
            for percept in percepts :
                if str(percept.getID()) == memory["EnemyBaseID"]:
                    targetedBasePercept= percept

            if targetedBasePercept is not None :
                actionWarRocketLauncher.nextState= FiringState
                setHeading(percept.getAngle())
                return idle()
            else :
                actionWarRocketLauncher.nextState= TravelToEnemyBaseState
                return move() #TODO setHeading
        else :
            actionWarRocketLauncher.nextState= TravelToEnemyBaseState
            return move()

def reflexes() :
    if "BaseID" not in memory :
        sendMessageToBases("INFORM", ["Type", "RocketLauncher"])

    messages = getMessages()
    for message in messages :
        if message.getMessage() == "ORDER" :
            if message.getContent()[0] == "EnemyBase" :
                memory["EnemyBaseID"] = message.getContent()[1]
                enemyBaseData = determinateAttacksAngle( float(message.getContent()[2]), float(message.getContent()[3]), message.getAngle(), message.getDistance())
                setHeading(enemyBaseData[0])
                memory["EnemyBaseDistance"] = enemyBaseData[1]
                actionWarRocketLauncher.nextState = TravelToEnemyBaseState

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
    distance = math.sqrt(distancePercept * distancePercept + distanceMessage*distanceMessage)
    angle = math.degrees(math.atan2(vectorResult[1], vectorResult[0]))

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
memory["NbTickFromStart"] = 0
