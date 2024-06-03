from flask import Flask, render_template, jsonify, request
import json
import numpy as np
import math
import random

import pokemonmove as pkmove



app = Flask(__name__)



# Load data
with open('gen9ou.json') as f:
    data = json.load(f)

def usage_data_individual(pokemon_name):
    return data["pokemon"].get(pokemon_name, {}).get("usage", {}).get("raw", 0)

def teammate_percentage(pokemon_1, pokemon_2):
    return data["pokemon"].get(pokemon_1, {}).get("teammates", {}).get(pokemon_2, 0.00001)

def log_probability(p):
    return math.log(p) if p > 0 else float('-inf')

def exp_log_probability(log_p):
    return math.exp(log_p) if log_p != float('-inf') else 0

def create_pokemon(pokemon):
    name = pokemon
    sample = {
        'name': name,
        'ability': '',
        'item': '',
        'moves': ['', '', '', ''],
        'nature': '',
        'evs': { 'HP': 0, 'Atk': 0, 'Def': 0, 'SpA': 0, 'SpD': 0, 'Spe': 0 },
        'teraType': '',
        'lead': False
    }
    return sample

def differing_weathers(team, individual, change, w, f):
    #if change['category'] == None or change['category'] != 'ability':
        #return
    sun = 0
    snow = 0
    rain = 0
    sand = 0
    weather_abilities = {'Drizzle': rain, 'Drought': sun, 'Sand Stream': sand, 'Snow Warning': snow}

    if individual['ability'] in weather_abilities.keys():
        weather_abilities[individual['ability']] += 1

    for pokemon in team:
        if pokemon['ability'] == 'Drizzle':
            rain += 1
        if pokemon['ability'] == 'Drought':
            sun += 1
        if pokemon['ability'] == 'Sand Stream':
            sand += 1
        if pokemon['ability'] == 'Snow Warning':
            snow += 1
    if (sun and snow) or (sun and rain) or (sun and sand) or (snow and rain) or (snow and sand) or (rain and sand):
        f[1] += w
    return

def assault_vest_with_status(individual, w, f):
    if individual['item'] == 'Assault Vest' and pkmove.contains_status(individual['moves']):
        f[1] += w
    return

def choice_with_status_minus_trick(individual, w, f):
    choice_items = ["Choice Scarf", "Choice Band", "Choice Specs"]
    moveset_doesnt_contain_trick = "Trick" not in individual['moves']
    moveset_contains_contain_status = pkmove.contains_status(individual['moves'])
    holding_choice_item = individual['item'] in choice_items

    if holding_choice_item and moveset_contains_contain_status and moveset_doesnt_contain_trick:
        f[1] += w
    return

def seed_and_terrain(team, individual, w, f):
    abilities = [each['ability'] for each in team]
    items = [each['item'] for each in team]

    if 'Grassy Seed' in items and 'Grassy Surge' not in abilities:
        f[1] += w
    if 'Misty Seed' in items and 'Misty Surge' not in abilities:
        f[1] += w
    if 'Electric Seed' in items and 'Electric Surge' not in abilities:
        f[1] += w
    if 'Psychic Seed' in items and 'Psychic Surge' not in abilities:
        f[1] += w    
    return

def extender_and_terrain(individual, w, f):
    possible_abilities = data["pokemon"][individual['name']]['abilities'].keys()
    ability = individual['ability']
    item = individual['item']

    if item == 'Terrain Extender' and ability != 'Grassy Surge' and 'Grassy Surge' in possible_abilities:
        f[1] += w
    if item == 'Terrain Extender' and ability != 'Misty Surge' and 'Misty Surge' in possible_abilities:
        f[1] += w
    if item == 'Terrain Extender' and ability != 'Electric Surge' and 'Electric Surge' in possible_abilities:
        f[1] += w
    if item == 'Terrain Extender' and ability != 'Psychic Surge' and 'Psychic Surge' in possible_abilities:
        f[1] += w    
    return

def item_typing_and_moves(individual, w, f):
    held_item = individual['item']
    move_set = individual['moves']
    if len(move_set) == 0:
        return
    categories = { 
        "Black Glasses" : "dark",
        "Dread Plate" : "dark",
        ""
        "Earth Plate" : "ground",

        "Sharp Beak" : "flying",
        "Dragon Fang" : "dragon",
        "Draco Plate" : "dragon",
        "Spooky Plate" : "ghost",
        "Silk Scarf": "Normal"
    }
    if held_item in categories.keys() and not pkmove.moveset_contains_type(move_set, categories[held_item]):
        f[1] += w 
    return

def status_ability_no_status_item(individual, w, f):
    held_item = individual['item']
    chosen_ability = individual['ability']
    fire_abilities = ["Guts", "Quick Feet"]
    poison_abilities = ["Poison Heal", "Toxic Boost"]
    if held_item == 'Flame Orb' and chosen_ability not in fire_abilities:
        f[1] += w
    if held_item == 'Toxic Orb' and chosen_ability not in poison_abilities:
        f[1] += w
    return

def light_clay_no_screens(individual, w, f):
    held_item = individual['item']
    screen_moves = ['Light Screen', 'Reflect', 'Aurora Veil']
    possible_moves = data["pokemon"][individual['name']]['moves'].keys()
    individual_moveset = individual['moves']
    if held_item != 'Light Clay':
        return
    if held_item == 'Light Clay':
        for move in individual_moveset:
            if move in screen_moves:
                return
    for move in screen_moves:
        if move in possible_moves:
            f[1] += w
            return
    return

def rock_no_weather(individual, w, f):
    held_item = individual['item']
    ability = individual['ability']
    converter = {
        "Smooth Rock":"Sand Stream",
        "Damp Rock":"Drizzle",
        "Heat Rock":"Drought",
        "Icy Rock":"Snow Warning"
    }

    if held_item in converter.keys() and ability != converter[held_item]:
        f[1] += w
    return

def weather_no_depencies(team, individual, w, f):
    rain = ["weather ball", ]

    return



def conventionality_factor(team, individual, change=None):
    numerator = 1.0
    denominator = 1.0
    factor = [numerator, denominator]

    differing_weathers(team, individual, change, 5000, factor)
    assault_vest_with_status(individual, 1000, factor)
    seed_and_terrain(team, individual, 1000, factor)
    extender_and_terrain(individual, 1000, factor)
    choice_with_status_minus_trick(individual, 1000, factor)
    #item_typing_and_moves(individual, 1000, factor)
    light_clay_no_screens(individual, 1000, factor)
    rock_no_weather(individual, 1000, factor)
    
    return factor[0]/factor[1]


def individual_pokemon_likeliness_given_team(individual, team):
    #print(individual)
    p_individual = usage_data_individual(individual)
    log_p_individual = log_probability(p_individual)
    joint_probabilities = 1
    final_probability = 1
    log_joint_probability = log_p_individual
    if team == None or len(team) == 0:
        return usage_data_individual(individual)
    
    else:   

        for i in range(len(team)):
            final_probability = final_probability*teammate_percentage(team[i]['name'], individual)

    return final_probability

def predict_next_pokemon(current_team):
    total = 0
    pokemon_list = list(data['pokemon'].keys())
    probabilities = []
    
    for pokemon in pokemon_list:
        if pokemon not in [p['name'] for p in current_team]:
            prob = individual_pokemon_likeliness_given_team(pokemon, current_team)
            total += prob
            probabilities.append((pokemon, prob))

    #print(total)
    probabilities.sort(key=lambda x: x[1], reverse=True)
    top_pokemon = probabilities
    individuals = []
    individuals_p = []
    for p in top_pokemon:
        name = p[0]
        individuals.append(create_pokemon(name))
        individuals_p.append(p[1])

    return individuals, individuals_p

def generate_first_choice():
    initial_probabilities = list(data['pokemon'].keys())
    weights = (usage_data_individual(pokemon) for pokemon in initial_probabilities)
    first_choice = random.choices(initial_probabilities, weights, k=1)
    return first_choice

def generate_team():
    team = []
    first_pokemon_name = generate_first_choice()
    team.append(create_pokemon(first_pokemon_name))
    while len(team) < 6:
        pass

    return


    


def create_temp_team(current_team, temp_pokemon):
    temp_team = current_team.copy()
    for i in range(0,len(current_team)):
        if temp_team[i]['name'] == temp_pokemon['name']:
            temp_team[i] = temp_pokemon
    return temp_team


def convert_numpy_types(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

@app.route('/')
def index():
    return render_template('team.html', pokemon_data=json.dumps(data))

@app.route('/suggest', methods=['POST'])
def suggest():
    current_team = request.json.get('team', [])
    next_pokemon_suggestions, probabilities = predict_next_pokemon(current_team)
    next_pokemon_suggestions = convert_numpy_types(next_pokemon_suggestions)
    probabilities = convert_numpy_types(probabilities)
    return jsonify({
        'suggestions': next_pokemon_suggestions,
        'probabilities': probabilities
    })
    

def predict_next_move(current_team, pokemon_we_are_choosing_for):
    move_list = list(data['pokemon'][pokemon_we_are_choosing_for['name']]['moves'].keys())
    probabilities = []
    temp_pokemon = pokemon_we_are_choosing_for.copy()
    if len(temp_pokemon['moves']) < 4:
        empty_space = temp_pokemon['moves'].index('') 
    else:
        empty_space = 0
    temp_team = None
    #print(move_list)
    normalizing_factor = 0

    for move in move_list:
        if move not in pokemon_we_are_choosing_for['moves']:
            temp_pokemon['moves'][empty_space] = move
            temp_team = create_temp_team(current_team, temp_pokemon)
            prob = (conventionality_factor(temp_team, temp_pokemon, change={'category':'move','chosen':move}) * data['pokemon'][pokemon_we_are_choosing_for['name']]['moves'][move])
            normalizing_factor += prob
            #probabilities.append((move, prob))
            #print(temp_pokemon['moves'])
            temp_pokemon['moves'][empty_space] = ''
    #print(len(probabilities))
    #print(len(move_list))
    #print(move_list)
    for move in move_list:
        if move not in pokemon_we_are_choosing_for['moves']:
            temp_pokemon['moves'][empty_space] = move
            temp_team = create_temp_team(current_team, temp_pokemon)
            prob = (conventionality_factor(temp_team, temp_pokemon, change={'category':'move','chosen':move}) * data['pokemon'][pokemon_we_are_choosing_for['name']]['moves'][move])
            probabilities.append((move, prob/normalizing_factor))
            #print(temp_pokemon['moves'])
            temp_pokemon['moves'][empty_space] = ''
    #print(len(probabilities))


    probabilities.sort(key=lambda x: x[1], reverse=True)
    #print(probabilities)
    top_moves = probabilities
    individuals = [p[0] for p in top_moves]
    individuals_p = [p[1] for p in top_moves]

    return individuals, individuals_p

@app.route('/suggest_move', methods=['POST'])
def suggest_move():
    current_team = request.json.get('team', [])
    pokemon_we_are_choosing_for = request.json.get('pokemon', {})

    next_move_suggestions, probabilities = predict_next_move(current_team, pokemon_we_are_choosing_for)
    next_move_suggestions = convert_numpy_types(next_move_suggestions)
    probabilities = convert_numpy_types(probabilities)

    return jsonify({
        'suggestions': next_move_suggestions,
        'probabilities': probabilities
    })

def predict_next_item(current_team, pokemon_we_are_choosing_for):
    item_list = list(data['pokemon'][pokemon_we_are_choosing_for['name']]['items'].keys())
    probabilities = []
    temp_pokemon = pokemon_we_are_choosing_for.copy()
    #print(move_list)
    normalizing_factor = 0

    for item in item_list:
        temp_pokemon['item']= item
        temp_team = create_temp_team(current_team, temp_pokemon)
        prob = (conventionality_factor(temp_team, temp_pokemon) * data['pokemon'][pokemon_we_are_choosing_for['name']]['items'][item])
        normalizing_factor += prob
        #print(temp_pokemon['item'])
    
    for item in item_list:
        temp_pokemon['item']= item
        temp_team = create_temp_team(current_team, temp_pokemon)
        prob = (conventionality_factor(temp_team, temp_pokemon) * data['pokemon'][pokemon_we_are_choosing_for['name']]['items'][item])
        probabilities.append((item, prob/normalizing_factor))
        #print(temp_pokemon['item'])

    probabilities.sort(key=lambda x: x[1], reverse=True)
    top_items = probabilities
    individuals = [p[0] for p in top_items]
    individuals_p = [p[1] for p in top_items]

    return individuals, individuals_p

@app.route('/suggest_item', methods=['POST'])
def suggest_item():
    current_team = request.json.get('team', [])
    pokemon_we_are_choosing_for = request.json.get('pokemon', {})

    next_item_suggestions, probabilities = predict_next_item(current_team, pokemon_we_are_choosing_for)
    next_item_suggestions = convert_numpy_types(next_item_suggestions)
    probabilities = convert_numpy_types(probabilities)

    return jsonify({
        'suggestions': next_item_suggestions,
        'probabilities': probabilities
    })

def predict_next_ability(current_team, pokemon_we_are_choosing_for):
    ability_list = list(data['pokemon'][pokemon_we_are_choosing_for['name']]['abilities'].keys())
    probabilities = []
    temp_pokemon = pokemon_we_are_choosing_for.copy()
    #print(move_list)

    normalizing_factor = 0

    for ability in ability_list:
        temp_pokemon['ability']= ability
        temp_team = create_temp_team(current_team, temp_pokemon)
        prob = (conventionality_factor(temp_team, temp_pokemon) * data['pokemon'][pokemon_we_are_choosing_for['name']]['abilities'][ability])
        normalizing_factor += prob
        #probabilities.append((ability, prob))
        #print(temp_pokemon['item'])

    for ability in ability_list:
        temp_pokemon['ability']= ability
        temp_team = create_temp_team(current_team, temp_pokemon)
        prob = (conventionality_factor(temp_team, temp_pokemon) * data['pokemon'][pokemon_we_are_choosing_for['name']]['abilities'][ability])
        probabilities.append((ability, prob/normalizing_factor))
        #print(temp_pokemon['item'])

    probabilities.sort(key=lambda x: x[1], reverse=True)
    top_abilities = probabilities
    individuals = [p[0] for p in top_abilities]
    individuals_p = [p[1] for p in top_abilities]

    return individuals, individuals_p

@app.route('/suggest_ability', methods=['POST'])
def suggest_ability():
    current_team = request.json.get('team', [])
    pokemon_we_are_choosing_for = request.json.get('pokemon', {})

    next_ability_suggestions, probabilities = predict_next_ability(current_team, pokemon_we_are_choosing_for)
    next_ability_suggestions = convert_numpy_types(next_ability_suggestions)
    probabilities = convert_numpy_types(probabilities)

    return jsonify({
        'suggestions': next_ability_suggestions,
        'probabilities': probabilities
    })

def predict_next_spread(current_team, pokemon_we_are_choosing_for):
    spread_list = list(data['pokemon'][pokemon_we_are_choosing_for['name']]['spreads'].keys())
    probabilities = []
    temp_pokemon = pokemon_we_are_choosing_for.copy()
    #print(spread_list)
    normalizing_factor = 0

    for spread in spread_list:
        #print(f"spread: {spread}")
        nature = spread[0:spread.index(":")]
        #print(f"{nature}: nature")

        temp_pokemon['nature']= nature

        ev_list = spread[spread.index(":")+1:].split("/")
        #print(ev_list)
        #print(temp_pokemon)
        temp_pokemon['evs']['HP'] = ev_list[0]
        temp_pokemon['evs']['Atk'] = ev_list[1]
        temp_pokemon['evs']['Def'] = ev_list[2]
        temp_pokemon['evs']['SpA'] = ev_list[3]
        temp_pokemon['evs']['SpD'] = ev_list[4]
        temp_pokemon['evs']['Spe'] = ev_list[5]

        temp_team = create_temp_team(current_team, temp_pokemon)
        prob = (conventionality_factor(temp_team, temp_pokemon) * data['pokemon'][pokemon_we_are_choosing_for['name']]['spreads'][spread])
        normalizing_factor += prob


    for spread in spread_list:
        nature = spread[0:spread.index(":")]
        temp_pokemon['nature']= nature
        ev_list = spread[spread.index(":")+1:].split("/")
        temp_pokemon['evs']['HP'] = ev_list[0]
        temp_pokemon['evs']['Atk'] = ev_list[1]
        temp_pokemon['evs']['Def'] = ev_list[2]
        temp_pokemon['evs']['SpA'] = ev_list[3]
        temp_pokemon['evs']['SpD'] = ev_list[4]
        temp_pokemon['evs']['Spe'] = ev_list[5]
        
        temp_team = create_temp_team(current_team, temp_pokemon)
        prob = (conventionality_factor(temp_team, temp_pokemon) * data['pokemon'][pokemon_we_are_choosing_for['name']]['spreads'][spread])
        probabilities.append((spread, prob/normalizing_factor))

    probabilities.sort(key=lambda x: x[1], reverse=True)
    top_spreads = probabilities
    individuals = [p[0] for p in top_spreads]
    individuals_p = [p[1] for p in top_spreads]

    return individuals, individuals_p

@app.route('/suggest_spread', methods=['POST'])
def suggest_spread():
    current_team = request.json.get('team', [])
    pokemon_we_are_choosing_for = request.json.get('pokemon', {})

    next_spread_suggestions, probabilities = predict_next_spread(current_team, pokemon_we_are_choosing_for)
    next_spread_suggestions = convert_numpy_types(next_spread_suggestions)
    probabilities = convert_numpy_types(probabilities)

    return jsonify({
        'suggestions': next_spread_suggestions,
        'probabilities': probabilities
    })


if __name__ == '__main__':
    app.run(debug=True)
