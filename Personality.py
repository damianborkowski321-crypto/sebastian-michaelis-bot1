# personality.py
def update_personality(u):
    moods = ["calm", "protective", "wrathful", "mischievous"]
    u["personality"] = moods[int(u.get("bond",0)) % len(moods)]
    return u
