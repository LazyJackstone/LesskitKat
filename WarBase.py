import math
class IdleState(object):
    @staticmethod
    def execute():
        actionWarBase.nextState= IdleState
        return idle()

#TODO add what kind of agent to create AND when
class CreateAgent(object):
    @staticmethod
    def execute():
        setNextAgentToCreate(WarAgentType.WarExplorer)
        actionWarBase.nextState= CreateAgent
        return create()

class AlertState :
    @staticmethod
    def execute():
        return idle()
        
def reflexes():
    messages = getMessages()
    if len(messages)>0:
        for message in messages:
            if message.getMessage()=="INFORM":
                if message.getContent()[0]=="EnemyBase":
                    memory["EnemyBaseAngle"] = float(message.getContent()[1])#*
                    memory["EnemyBaseDistance"] = float(message.getContent()[2])#*
                    memory["EnemyBaseID"] = message.getContent()[3]
                    enemyBaseData = determinateAttacksAngle(memory["EnemyBaseAngle"], memory["EnemyBaseDistance"], message.getAngle(), message.getDistance())
                    broadcastMessageToAgentType(WarAgentType.WarRocketLauncher, "REQUEST", ["Attack Enemy Base",str(enemyBaseData[0]), str(enemyBaseData[1]), str(memory["EnemyBaseID"])]) # NOTE: Variation en ORDER ??

            if message.getMessage()=="ASK":
                if message.getContent()[0]=="Where are you":
                    setDebugString("Here")
                    print(message.getSenderID())
                    broadcastMessageToAgentType(WarAgentType.WarExplorer, "INFORM", ["Here"])

    if isBlocked():
        RandomHeading()
    return None


def actionWarBase():
    result = reflexes() # Reflexes
    if result:
        return result


    # FSM - Changement d'Ã©tat
    actionWarBase.currentState = actionWarBase.nextState
    actionWarBase.nextState = None

    if actionWarBase.currentState:
        return actionWarBase.currentState.execute()



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
    distance = math.sqrt(distancePercept**2 + distanceMessage**2)
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
actionWarBase.nextState = IdleState
actionWarBase.currentState = None
memory={}
