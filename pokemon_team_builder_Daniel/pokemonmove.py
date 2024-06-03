import json

# Load the JSON data
with open("pokemon_type_chart.json", "r") as f:
    type_chart = json.load(f)

with open("moves.json", "r") as f:
    moves = json.load(f)

# Define helper functions
def get(move_name):
    """
    Returns the move data for the given move name.
    """
    move_data = moves.get(move_name.lower(), None)
    if move_data:
        return MoveData(move_data)
    else:
        return None

def contains_status(move_names):
    """
    Returns True if any of the given move names is a status move, False otherwise.
    """
    for move_name in move_names:
        clean_name = move_name.replace(" ", "")
        move_data = get(clean_name)
        if move_data and move_data.category == "Status":
            return True
    return False

def contains_special(move_names):
    """
    Returns True if any of the given move names is a special move, False otherwise.
    """
    for move_name in move_names:
        move_data = get(move_name)
        if move_data and move_data.category == "Special":
            return True
    return False

def contains_physical(move_names):
    """
    Returns True if any of the given move names is a physical move, False otherwise.
    """
    for move_name in move_names:
        move_data = get(move_name)
        if move_data and move_data.category == "Physical":
            return True
    return False

def moveset_contains_type(move_names, move_type):

    for move_name in move_names:
        print(f"name: {move_name}")
        if move_name != '' and move_name != ' ':
            move_data = get(move_name.replace(" ", ""))
            print(move_data)
            if move_data.typing == move_type:
                return True

    return False



class MoveData:
    """
    A class to represent a Pokemon move and provide convenient methods to access its data.
    """
    def __init__(self, move_data):
        self.data = move_data

    @property
    def name(self):
        return self.data["name"]

    @property
    def bp(self):
        return self.data.get("basePower", 0)

    @property
    def typing(self):
        return self.data["type"]

    @property
    def category(self):
        return self.data["category"]

    @property
    def shortdesc(self):
        return self.data.get("shortDesc", "")
