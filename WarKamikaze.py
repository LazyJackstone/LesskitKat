"""Module pour WarKamikaze."""
import math

def actionWarKamikaze():
    """Fonction principale WarKamikaze."""
    result = reflexes()
    if result:
        return result

    # Implémentation de la FSM
    actionWarKamikaze.currentState = actionWarKamikaze.nextState
    actionWarKamikaze.nextState = None

    if actionWarKamikaze.currentState:
        return actionWarKamikaze.currentState.execute()
    else:
        actionWarKamikaze.nextState = WiggleState
        return WiggleState.execute()


def reflexes():
    """Reflexes."""
    if isBlocked():
        RandomHeading()
    for base in getPerceptsEnemiesWarBase():
    	if base.getDistance() < WarKamikazeMemory['radiusBomb']:
    		return fire()
    return None


class WiggleState(object):
    """WiggleState."""

    @staticmethod
    def execute():
        """Execute."""
        setDebugString("WiggleState")
        messages = getMessages()
        for message in messages:
            if message.getMessage() == "EnemyBaseHere":
                actionWarKamikaze.nextState = OffensiveState
                WarKamikazeMemory['message'] = message
                return idle()
        return move()


class OffensiveState(object):
    """OffensiveState."""

    @staticmethod
    def execute():
        """Execute."""
        setDebugString("OffensiveState")
        actionWarKamikaze.nextState = OffensiveState
        message = WarKamikazeMemory['message']

        # Va vers la base ennemie si on lui envoie un ordre d'attaque
        if message is not None:
            # On détermine l'angle d'attaque
            anglePercept = float(message.getContent()[1]); distancePercept = float(message.getContent()[0])
            angleMessage = message.getAngle(); distanceMessage = message.getDistance()
            setHeading(determinateAttacksAngle(anglePercept, distancePercept, angleMessage, distanceMessage))

        # Attaque tout seul la base s'il la perçoit
        for base in getPerceptsEnemiesWarBase():
    		if base.getDistance() < WarKamikazeMemory['radiusBomb']:
    			return fire()

        return move()


# Variables d'etat du WarKamikaze
actionWarKamikaze.currentState = None
actionWarKamikaze.nextState = WiggleState
# Memoire du WarKamikaze
WarKamikazeMemory = {}
WarKamikazeMemory['message'] = None
WarKamikazeMemory['radiusBomb'] = 40

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
    angle = math.degrees(math.atan2(vectorResult[1], vectorResult[0]))

    return angle

"""
    Calcul les coordonnées du point.
"""
def calculateCoord(angle, rayon):
    x = rayon * math.degrees(math.cos(math.radians(angle)))
    y = rayon * math.degrees(math.sin(math.radians(angle)))

    return [x, y]
