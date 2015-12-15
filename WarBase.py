import math
class IdleState(object): #TODO : Add when base should eat because low health.
    @staticmethod
    def execute():
        setDebugString("Creating")
        actionWarBase.nextState= IdleState
        """
        memory["NbUnitPreviousTick"] = memory["NbUnit"]
        memory["NbUnit"] = 0
        memory["NbExplorerPreviousTick"] = memory["NbExplorer"]
        memory["NbExplorer"] = 0
        memory["NbRocketLauncherPreviousTick"] = memory["NbRocketLauncher"]
        memory["NbRocketLauncher"] = 0
        memory["NbBasePreviousTick"] = memory["NbBase"]
        memory["NbBase"] = 1
        memory["NbKamiKazePreviousTick"] = memory["NbKamiKaze"]
        memory["NbKamiKaze"] = 0
        memory["NbEngineerPreviousTick"] = memory["NbEngineer"]
        memory["NbEngineer"] = 0
        messages = getMessages()

        if len(messages)>0 :
            for message in messages : #Message PRIORITE 0 : MISE A JOUR DATABASE
                if message.getMessage() ==  "STATUS" :
                    if message.getContent()[0] == "RocketLauncher" :
                        if "NbRocketLauncher" in memory :
                            memory["NbRocketLauncher"] = memory["NbRocketLauncher"] + 1
                    if message.getContent()[0] == "Explorer" :
                        if "NbExplorer" in memory :
                            memory["NbExplorer"] = memory["NbExplorer"] + 1
                    if message.getContent()[0] == "Engineer" :
                        if "NbEngineer" in memory :
                            memory["NbEngineer"] = memory["NbEngineer"] + 1
                    if message.getContent()[0] == "KamiKaze" :
                        if "NbKamiKaze" in memory :
                            memory["NbKamiKaze"] = memory["NbKamiKaze"] + 1
                    if message.getContent()[0] == "Base" :
                        if "NbBase" in memory :
                            memory["NbBase"] = memory["NbBase"] + 1
                if message.getMessage() == "INFORM" :
                    if message.getContent()[0]=="EnemyBase" :
                        enemyBaseData = determinateAttacksAngle( float(message.getContent()[2]), float(message.getContent()[3]), message.getAngle(), message.getDistance())
                        if "NbEnemyBase" in memory and "ListEnemyBase" in memory:
                            memory["NbEnemyBase"] = memory ["NbEnemyBase"] + 1
                            memory["ListEnemyBase"] = memory.append([ message.getContent()[1], enemyBaseData[0], enemyBaseData[1], message.getContent()[4]])
                        else :
                            memory["NbEnemyBase"] = 1
                            memory["ListEnemyBase"] = [[ message.getContent()[1], enemyBaseData[0], enemyBaseData[1], message.getContent()[4]]] # Base ID, Angle, Distance, Health

        memory["NbUnit"] = memory["NbRocketLauncher"] + memory["NbBase"] + memory["NbKamiKaze"] + memory["NbEngineer"] + memory["NbExplorer"]

        if memory["NbUnitPreviousTick"] > memory["NbUnit"] :
            if isAbleToCreate(WarAgentType.WarRocketLauncher) and (memory["NbRocketLauncher"] < 2 or memory["NbRocketLauncher"]%2!=0):
                actionWarBase.nextState = HealingState
                return createRocketLauncher()

            if isAbleToCreate(WarAgentType.WarExplorer) and memory["NbExplorer"] < 10 : #TODO : Choisir une meilleur priorité et meilleur conditions de création
                actionWarBase.nextState = HealingState
                return createExplorer()

            if isAbleToCreate(WarAgentType.WarKamikaze) and memory["NbKamiKaze"] < 5 :
                actionWarBase.nextState = HealingState
                return createKamikaze()

            if isAbleToCreate(WarAgentType.WarEngineer) and memory["NbEngineer"] < 1 :
                actionWarBase.nextState = HealingState
                return createEngineer()
        """
        return idle()
class HealingState :
    @staticmethod
    def execute() :
        return idle()

class AlertState :
    @staticmethod
    def execute() :
        percepts = getPerceptsEnemies()
        if len(percepts) > 0 :
            actionWarBase.nextState = AlertState
        else :
            messages = getMessages()
            if len (messages) > 0 :
                for message in messages :
                    if message.getMessage() == "STATUS" :
                        if message.getContent()[0] == "ALERT" :
                            actionWarBase.nextState = AlertState


        return idle() # TODO :  Add Médéric Part

def reflexes():
    #sendMessageToBases("STATUS", ["Base"])
    #if getHealth() < (maxHealth()/25)*100 :
    #    actionWarBase.nextState = HealingState
    messages = getMessages()
    if len(messages) > 0 :
        for message in messages :
            if message.getMessage()=="ASK" :
                if message.getContent()[0]=="Where are you" :
                    setDebugString("Here")
                    reply(message, "INFORM", ["Here"])

    #percepts = getPerceptsEnemies()
    #if len(percepts) > 0 :
    #    actionWarBase.nextState = AlertState

    if isBlocked() :
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
"""
memory["NbUnitPreviousTick"] = 0
memory["NbUnit"] = 0
memory["NbExplorerPreviousTick"] = 0
memory["NbExplorer"] = 0
memory["NbRocketLauncherPreviousTick"] = 0
memory["NbRocketLauncher"] = 0
memory["NbBasePreviousTick"] = 0
memory["NbBase"] = 1
memory["NbKamiKazePreviousTick"] = 0
memory["NbKamiKaze"] = 0
memory["NbEngineerPreviousTick"] = 0
memory["NbEngineer"] = 0
"""
