import math
class SearchFoeState(object):
    @staticmethod
    def execute():
        setDebugString("SearchFoeState")
        percepts = getPercepts()
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
                #setHeading(selectedPercept.getAngle())
                if isReloaded():
                    actionWarRocketLauncher.nextState = FiringState
                    #memory["nextState"]= FiringState
                else :
                    actionWarRocketLauncher.nextState = ReloadingState
                    #memory["nextState"]= ReloadingState
            else:
                actionWarRocketLauncher.nextState = SearchFoeState
                #memory["nextState"]= SearchFoeState
                setRandomHeading(25)
        else:
            actionWarRocketLauncher.nextState = SearchFoeState
            #memory["nextState"]= SearchFoeState
            setRandomHeading(25)

        return move()

class FiringState(object):
    @staticmethod
    def execute():
        setDebugString("Firing State")
        actionWarRocketLauncher.nextState = ReloadingState
        #memory["nextState"]= ReloadingState
        return fire()

class ReloadingState(object):
    @staticmethod
    def execute():
        setDebugString("Reloading State")
        if isReloaded():
            actionWarRocketLauncher.nextState = SearchFoeState
            #memory["nextState"]= SearchFoeState
        else:
            actionWarRocketLauncher.nextState = ReloadingState
            #memory["nextState"]= ReloadingState

        return reloadWeapon()

class WiggleState(object):
    @staticmethod
    def execute():
        setDebugString("WiggleState")
        if (isBlocked()) :
            RandomHeading()
        return move()

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

# TODO ADD Gestion de la priorite ORDER > REQUEST
def reflexes() :
    messages = getMessages()
    for message in messages :
        if message.getMessage()=="REQUEST" :
            if message.getContent()[0] == "Attack Enemy Base" :
                actionWarRocketLauncher.nextState = TravelToEnemyBaseState
                memory["EnemyBaseAngleFromBase"] = float(message.getContent()[1])#*
                print (memory["EnemyBaseAngleFromBase"])
                memory["EnemyBaseDistanceFromBase"] = float(message.getContent()[2])#*
                memory["EnemyBaseID"] = message.getContent()[3]
                actionWarRocketLauncher.nextState= TravelToEnemyBaseState
                enemyBaseData = determinateAttacksAngle(memory["EnemyBaseAngleFromBase"],memory["EnemyBaseDistanceFromBase"],message.getAngle(),message.getDistance())
                print (enemyBaseData)
                setHeading(enemyBaseData[0])
                memory["EnemyBaseDistance"] = enemyBaseData[1]

            if message.getContent()[0] == "Group" :
                if "Group" not in memory:
                    requestRole(message.getContent()[1], "Bidder")
                    memory["Group"] = message.getContent()[1]
                    reply(message, "INFORM", ["OK"])
                else :
                    reply(message, "INFORM", ["BUSY"])

        if message.getMessage() == "INFORM":
            if message.getContent()[0] == "Here":
                memory["AllyBaseAngle"]= message.getAngle()

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

    ##memory["currentState"]= memory["nextState"]
    #memory["nextState"]= None

    #if memory["currentState"]:
    #    return memory["currentState"].execute()
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
#memory["currentState"]= None
#memory["nextState"]= SearchFoeState
