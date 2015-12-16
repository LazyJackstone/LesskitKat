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

def reflexes():

    messages = getMessages()
    if len(messages) > 0:
        for message in messages:
            if message.getMessage() == "INFORM":
                if message.getContent()[0] == "BaseID":
                    memory["BaseID"] = message.getSenderID()

    percepts = getPerceptsEnemiesWarBase()
    if len(percepts) > 0 : #TODO : Add choose one + send data to bases
        sendMessage(memory["BaseID"], "INFORM",["EnemyBase", str(percepts[0].getID()), str(percepts[0].getAngle()), str(percepts[0].getDistance()), str(percepts[0].getHealth())]) #id + angle + distance + vie

    if isBlocked():
        RandomHeading()

    return None


def actionWarExplorer():
    result = reflexes() # Reflexes
    if result:
        return result

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
actionWarExplorer.nextState = SearchFoodState
actionWarExplorer.currentState = None
memory={}
