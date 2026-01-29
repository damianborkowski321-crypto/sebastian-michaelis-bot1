# sentience.py
import random

async def autonomous_thought(u):
    # User thinks independently
    u["bond"] += random.uniform(-0.1, 0.2)
    u["obedience"] += random.uniform(-0.05, 0.1)
    return u

def self_preservation_check(u):
    # Ensure "life" logic
    if u.get("soul",0) <= 0:
        u["ending"] = "Destroyed"
    return u
