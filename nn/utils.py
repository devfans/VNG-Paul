# Map a value from one range to another
def translate(value, leftMin, leftMax, rightMin, rightMax):
    py_clip = lambda x, l, u: l if x < l else u if x > u else x

    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return py_clip(rightMin + (valueScaled * rightSpan), rightMin, rightMax)
    

def level(x):
   return float(translate(int(x), 1, 30, 0, 1))

def xp(x):
    return float(translate(int(x), 0, 1000000, 0, 1))

def ranked(x):
    return float(translate(int(x), 0, 10000, 0, 1))

def lossStreak(x):
    return float(translate(int(x), 0, 1000, 0, 1))

def winStreak(x):
   return float(translate(int(x), 0, 1000, 0, 1))

def wins(x):
    return float(translate(int(x), 0, 100000, 0, 1))

def played(x):
    return float(translate(int(x), 0, 1000000, 0, 1))   

    
def heroNameToInt(hero):
    if "Grumpjaw" in hero:
        return 0
    elif "Idris" in hero:
        return 1
    elif "Flicker" in hero:
        return 2
    elif "Gwen" in hero:
        return 3
    elif "Baron" in hero:
        return 4
    elif "Samuel" in hero:
        return 5
    elif "Lyra" in hero:
        return 6
    elif "Lance" in hero:
        return 7
    elif "Alpha" in hero:
        return 8
    elif "Ozo" in hero:
        return 9
    elif "Reim" in hero:
        return 10
    elif "Kestrel" in hero:
        return 11
    elif "Blackfeather" in hero:
        return 12
    elif "Phinn" in hero:
        return 13
    elif "Skye" in hero:
        return 14
    elif "Hero016" in hero: # Rona
        return 15
    elif "Fortress" in hero:
        return 16
    elif "Joule" in hero:
        return 17
    elif "Ardan" in hero:
        return 18
    elif "Hero010" in hero: # Skaarf
        return 19
    elif "Sayoc" in hero: # Taka
        return 20
    elif "Hero009" in hero: # Krul
        return 21
    elif "SAW" in hero:
        return 22
    elif "Petal" in hero:
        return 23
    elif "Glaive" in hero:
        return 24
    elif "Adagio" in hero:
        return 26
    elif "Ringo" in hero:
        return 27
    elif "Catherine" in hero:
        return 28
    elif "Celeste" in hero:
        return 29
    elif "Vox" in hero:
        return 30
    else:
        return -1   