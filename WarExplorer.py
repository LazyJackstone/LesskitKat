#TODO : memoriser position nourriture non ramassee ???

import math
class SearchFoodState(object):
    @staticmethod
    def execute():
        setDebugString("SearchFoodState")
        if isBagFull():
            actionWarExplorer.nextState = GoHomeState
            percepts=getPerceptsFood()
            if len(percepts)>0:
                sendMessageToExplorers("INFORM", ["Food", str(percepts[0].getAngle()), str(percepts[0].getDistance())])
                return move()

        actionWarExplorer.nextState = SearchFoodState
        percepts = getPerceptsFood()
        if len(percepts)>0:
            if "DistanceToFood" in memory:
                del memory["DistanceToFood"]
            if "AngleToFood" in memory:
                del memory["AngleToFood"]
            closestFood = None
            for percept in percepts :
                if percept.getDistance() < getMaxDistanceTakeFood() :
                    return take()
                else :
                    if closestFood is None :
                        closestFood = percept
                    else :
                        if percept.getDistance()< closestFood.getDistance():
                            closestFood = percept

            followTarget(closestFood)
            return move()
        else :
            messages = getMessages()
            if len(messages) > 0:
                for message in getMessages():
                    if message.getMessage()=="INFORM":
                        if message.getContent()[0]=="Food":
                            foodData = determinateAttacksAngle(float(message.getContent()[1]),float(message.getContent()[2]), message.getAngle(), message.getDistance())
                            if "DistanceToFood" not in memory:
                                memory["DistanceToFood"] = foodData[1]

                            if "AngleToFood" not in memory:
                                memory["AngleToFood"] = foodData[0]
                                setHeading(foodData[0])

                            if foodData[1] < memory["DistanceToFood"]:
                                memory["DistanceToFood"] = foodData[1]
                                memory["AngleToFood"] = foodData[0]
                                setHeading(memory["AngleToFood"])

            if "AngleToFood" not in memory :
                setRandomHeading(30)
            else :
                memory["DistanceToFood"]=memory["DistanceToFood"] - getSpeed()

            return move()

class GoHomeState(object):
    @staticmethod
    def execute():
        setDebugString("GoHomeState")
        if getNbElementsInBag() == 0 :
            if "BaseAngle" in memory :
                del memory["BaseAngle"]
            actionWarExplorer.nextState = SearchFoodState
            return idle()

        actionWarExplorer.nextState = GoHomeState
        percepts = getPerceptsAlliesWarBase()
        if len(percepts) > 0:
            for percept in percepts:
                selectedBase = None
                if percept.getDistance() < maxDistanceGive():
                    giveToTarget(percept)
                    if "BaseAngle" in memory:
                        del memory["BaseAngle"]
                    return give()
                else:
                    if selectedBase is None:
                        selectedBase = percept
                    else:
                        if percept.getDistance() < selectedBase.getDistance():
                            selectedBase=percept
            followTarget(percept)
            if "BaseAngle" in memory:
                del memory["BaseAngle"]
            return move()
        else:
            if "BaseAngle" in memory:
                setHeading(memory["BaseAngle"])
                return move()
            else:
                messages= getMessages()
                if len(messages) > 0 :
                    selectedBaseData = None
                    for message in messages :
                        if message.getMessage() == "INFORM" :
                            if message.getContent()[0] == "Here":
                                if selectedBaseData is None :
                                    selectedBaseData = [message.getAngle(), message.getDistance()]
                                else :
                                    if message.getDistance() < selectedBaseData[1] :
                                        selectedBaseData = [message.getAngle(), message.getDistance()]

                    if selectedBaseData is not None :
                        memory["BaseAngle"] = selectedBaseData[0]
                        setHeading(memory["BaseAngle"])
                        return move()

                sendMessageToBases("ASK",["Where are you"])
                return idle()
class WiggleState(object):
    @staticmethod
    def execute():
        setDebugString("WiggleState")
        if (isBlocked()) :
            RandomHeading()
        return move()

class CreateGroupState(object):
    @staticmethod
    def execute() :
        setDebugString("CREATING GROUP")
        actionWarExplorer.nextState = CreateGroupState
        memory["NbTickSinceCreationStarted"] = memory["NbTickSinceCreationStarted"] + 1
        if "Group" not in memory :
            print "Groupe Créer"
            requestRole("BaseAttack", "Manager")
            memory["Group"] = "BaseAttack"
            sendMessageToRocketLaunchers("REQUEST", ["Group","BaseAttack"])
            sendMessageToEngineers("REQUEST", ["Group", "BaseAttack"])
            print "Messages envoyés"
            return idle()
        else :
            messages = getMessages()
            print " Explorer Messages" + str(messages)
            AvailableRL = []
            AvailableE = []
            if len(messages) > 0 : #TODO: Add selection of RL and Engineer that fit the most
                for message in messages :
                    if message.getMessage() == "INFORM" :
                        if message.getContent()[0] == "Group" :
                            if message.getContent()[1] == "OK" :
                                if message.getContent()[2] == "RocketLauncher" :
                                    AvailableRL.append(message)
                                    print "Rl Added"
                                else :
                                    AvailableE.append(message)
                                    print "E added"

            selectedEngineer = None
            if AvailableE is not None :
                for engineer in AvailableE:
                    if selectedEngineer is None :
                        selectedEngineer = engineer
                    else :
                        if engineer.getDistance() < selectedEngineer.getDistance() :
                            selectedEngineer = engineer
            selectedRl = None
            if AvailableRL is not None : #TODO: Add tri of AvailableRL
                for rl in AvailableRL :
                    if selectedRl is None:
                        selectedRl.append(rl)
                    else :
                        if len (selectedRl) < 2 :
                            selectedRl.append(rl)
                        else :
                            if rl.getDistance() < selectedRl[0].getDistance():
                                selectedRl[1] = selectedRl[0]
                                selectedRl[0] = rl
                            else :
                                if rl.getDistance() < selectedRl[1]:
                                    selectedRl[1] = rl
            if selectedRl is not None:
                print "Can Follow"
                for rl in selectedRl :
                    reply(message, "REQUEST", ["Join", "BaseAttack"])
                    if "LauncherInGroup" in memory :
                        memory["LauncherInGroup"].append(message.senderID())
                    else :
                        memory["LauncherInGroup"] = [message.senderID()]


            if selectedEngineer is not None :
                reply(message, "REQUEST", ["Join", "BaseAttack"])
                memory["EngineerInGroup"] = selectedEngineer.senderID()


        if memory["NbTickSinceCreationStarted"] == 3 :
            if "LauncherInGroup" in memory:
                actionWarExplorer.nextState = CommanderState
            else :
                actionWarExplorer.nextState = SearchFoodState

        return idle()

class CommanderState(object):
    @staticmethod
    def execute():
        setDebugString("COMMANDER")
        messages = getMessages()
        if len(messages) > 0 :
            newsFrom = []
            for message in messages:
                if message.senderID() in memory["LauncherInGroup"] or message.senderID() in memory["EngineerInGroup"] :
                    newsFrom.append(message.senderID())
                    if message.getMessage() == "INFORM":
                        if message.getContent()[0] == "Arrived" :
                            percepts = getPerceptsEnemiesWarBase() #TODO : Select best base to attack
                            if len(percepts) > 0 :
                                reply(message, "ORDER", "Fire", str(percepts[0].getAngle(), percepts[0].getDistance()))
                        else :
                            if message.getContent()[0] == "Travelling" :
                                if message.senderID() in memory["LauncherInGroup"]:
                                    for i in range(len(memory["LauncherInGroup"])) :
                                        if i == 0 :
                                            reply( message, "ORDER", ["Travel", str(getHeading() + 90), str(15)])
                                        if i == 1 :
                                            reply( message, "ORDER", ["Travel", str(getHeading()) - 90, str(15)])
                                if message.senderID() == memory["EngineerInGroup"] :
                                    reply(message, "ORDER", ["Travel", str(getHeading() + 180), str(5)])

            if len(newsFrom) != len(memory["LauncherInGroup"]) + len(memory["EngineerInGroup"]) :
                if memory["EngineerInGroup"] in newsFrom:
                    if len(newsFrom) == 1 :
                        #TODO: Add Abort
                        print "ABORD"
                    else :
                        for i in range(len(memory["LauncherInGroup"])):
                            if memory["LauncherInGroup"][i] not in newsFrom :
                                del memory["LauncherInGroup"][i]

def reflexes():
    percepts = getPerceptsEnemiesWarBase()
    if len(percepts) > 0 : #TODO : Add choose one + send data to bases
        sendMessageToBases("INFORM",["EnemyBase", str(percepts[0].getID()), str(percepts[0].getAngle()), str(percepts[0].getDistance()), str(percepts[0].getHealth())])
        if "Group" not in memory:
            actionWarExplorer.nextState = CreateGroupState
            memory["NbTickSinceCreationStarted"] = 0

    if isBlocked():
        RandomHeading()

    return None


def actionWarExplorer():
    memory["NbTicksFromStart"] = memory["NbTicksFromStart"] + 1
    #sendMessageToBases("STATUS", ["Explorer"])
    result = reflexes() # Reflexes
    if result:
        return result

    # FSM - Changement d'Ã©tat
    actionWarExplorer.currentState = actionWarExplorer.nextState
    actionWarExplorer.nextState = None
    if actionWarExplorer.currentState:
        return actionWarExplorer.currentState.execute()
    else :
        result = WiggleState.execute()
        actionWarExplorer.nextState = WiggleState
        return result

"""
    Détermine l'angle entre l'unité courante et le percept.
    anglePercept:    Angle entre l'envoyeur du message et le percept
    distancePercept: Distance entre l'envoyeur du message et le percept
    angleMessage:    Angle entre l'envoyeur du message et l'unité courante
    distanceMessage: Distance entre l'envoyeur du message et l'unité courante
"""
def determinateAttacksAngle(anglePercept, distancePercept, angleMessage, distanceMessage): #TODO : Corriger Distance --> taille carte :  1000*600
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
actionWarExplorer.nextState = SearchFoodState
actionWarExplorer.currentState = None
memory={}
memory["NbTicksFromStart"] = 0
