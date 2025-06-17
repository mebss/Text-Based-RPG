import random
import json
import time

# ----------------------------
#   Class Definitions
# ----------------------------

class Enemy:
    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack

class Room:
    def __init__(self, name, data):
        self.name = name
        self.description = data["description"]
        self.items = data.get("items", []).copy()
        self.connections = data.get("connections", []).copy()
        self.hints = data.get("hints", "")
        self.visited = False   # Track if this room has been visited before

    def remove_item(self, item_name):
        if item_name in self.items:
            self.items.remove(item_name)

    def add_connection(self, new_room_name):
        if new_room_name not in self.connections:
            self.connections.append(new_room_name)

    def to_dict(self):
        """
        Serialize dynamic fields for saving.
        """
        return {
            "items": self.items,
            "connections": self.connections,
            "visited": self.visited
        }

    def load_dynamic(self, data):
        """
        Restore dynamic fields (items, connections, visited) from saved data.
        """
        self.items = data.get("items", []).copy()
        self.connections = data.get("connections", []).copy()
        self.visited = data.get("visited", False)


class Player:
    def __init__(self, start_location, hp=10):
        self.location = start_location
        self.hp = hp
        self.inventory = []

    def move_to(self, new_location):
        self.location = new_location

    def pick_up(self, item_name):
        self.inventory.append(item_name)

    def use_item(self, item_name, items_data):
        """
        Use an item from inventory. Now reads:
          - "heal_amount" for healing items
          - "type": "light"/"weapon"/"armor"/"mystical"/"unlock"/etc.
        """
        if item_name not in self.inventory:
            print("\n⚠️  You don’t have that item in your inventory.\n")
            return

        item = items_data.get(item_name)
        if not item:
            print("\n⚠️  You can’t use that item right now.\n")
            return

        item_type = item.get("type")
        description = item.get("description", "You use the item.")

        print(f"\n✨  {description}")

        # Healing logic now uses "heal_amount"
        if item_type == "healing":
            heal_amt = item.get("heal_amount", 0)
            self.hp += heal_amt
            self.inventory.remove(item_name)
            print(f"❤️  Your HP is now {self.hp}.\n")

        elif item_type == "light":
            # You could check "usable_in" here, but for now just print description
            print("💡  The light pushes back the darkness around you.\n")

        elif item_type == "weapon":
            # Already handled in combat; here just a flavor message
            print("⚔️  You feel ready to face any threats.\n")

        elif item_type == "armor":
            # Armor use is passive; here just a flavor message
            print("🛡️  You feel protected and confident.\n")

        elif item_type == "mystical":
            print("🔮  You feel a strange energy course through you.\n")

        elif item_type == "unlock":
            # Key or similar; maybe contextual logic elsewhere
            print("🗝️  Perhaps you can use this to open a door or chest.\n")

        else:
            print("❔  You’re not sure what effect this has…\n")

    def attack_power(self, items_data):
        """
        Calculate the player's total attack power based on inventory.
        Now reads "damage" from any weapon-type items.
        Base attack = 1.
        """
        base = 1
        for item_name in self.inventory:
            item = items_data.get(item_name)
            if item and item.get("type") == "weapon":
                base += item.get("damage", 0)
        return base

    def defense_bonus(self, items_data):
        """
        Calculate the player's defense bonus based on inventory.
        Now reads "defense" from any armor-type items.
        """
        bonus = 0
        for item_name in self.inventory:
            item = items_data.get(item_name)
            if item and item.get("type") == "armor":
                bonus += item.get("defense", 0)
        return bonus


# ----------------------------
#   Loading & Randomizing Rooms
# ----------------------------

def load_rooms_raw(filename):
    with open(filename, "r") as f:
        return json.load(f)

def load_items(filename):
    with open(filename, "r") as f:
        return json.load(f)

# 1. Load raw JSON data:
raw_rooms_data = load_rooms_raw("rooms.json")
items_data = load_items("items.json")

# 2. Extract all items into a single pool (preserve counts per room):
room_item_counts = { name: len(data.get("items", [])) for name, data in raw_rooms_data.items() }
all_items = []
for data in raw_rooms_data.values():
    all_items.extend(data.get("items", []))

# 3. Shuffle the pool:
random.shuffle(all_items)

# 4. Re-assign items back to each room based on original counts:
new_rooms_data = {}
idx = 0
for room_name, data in raw_rooms_data.items():
    count = room_item_counts[room_name]
    assigned = all_items[idx : idx + count]
    idx += count

    new_room_entry = {
        "description": data["description"],
        "items": assigned,
        "connections": data["connections"],
        "hints": data.get("hints", "")
    }
    new_rooms_data[room_name] = new_room_entry

# Convert to Room objects
rooms = { name: Room(name, info) for name, info in new_rooms_data.items() }


# ----------------------------
#   Game Functions
# ----------------------------

def show_room(player, rooms):
    """
    Display information about the player's current room.
    If the room was visited before, show a shorter message.
    """
    current = rooms[player.location]

    print("\n" + "=" * 40)
    if not current.visited:
        # First-time visit: full description
        print(f"📍  Location: {current.name}")
        print(f"📝  {current.description}")
        current.visited = True
    else:
        # Subsequent visits: shorter reminder
        print(f"📍  You return to: {current.name}")

    # Always show items and connections
    print(f"👜  You see: {', '.join(current.items) if current.items else 'Nothing here.'}")
    print(f"➡️  Paths: {', '.join(current.connections)}")
    print(f"❤️  Your HP: {player.hp}")
    print("=" * 40)
    print("🔎  Commands: 'view inventory', 'hint', 'save', 'load', 'use [item]', 'pick up [item]', 'fight', 'open chest', 'map', 'help', 'quit'")
    print()

def random_event(player):
    """
    Occasional random event that reduces HP by 1 (20% chance each turn).
    """
    if random.randint(1, 5) == 1:
        print("\n🌬️  A sudden gust of wind chills you to the bone!")
        player.hp -= 1
        print(f"❤️  Your HP is now {player.hp}.")
        if player.hp <= 0:
            print("\n💀  You have succumbed to the cold. Game over!")
            exit()
        time.sleep(1)

def save_game(player, rooms):
    """
    Save player state and dynamic room state (items, connections, visited) to a JSON file.
    """
    rooms_dynamic = { name: room.to_dict() for name, room in rooms.items() }

    data = {
        "player": {
            "location": player.location,
            "inventory": player.inventory,
            "hp": player.hp
        },
        "rooms": rooms_dynamic
    }
    with open("savegame.json", "w") as f:
        json.dump(data, f)
    print("\n💾  Game saved!\n")

def load_game(player, rooms):
    """
    Load player state and room dynamic state from savegame.json.
    """
    try:
        with open("savegame.json", "r") as f:
            data = json.load(f)

            # Restore player state
            player.location = data["player"]["location"]
            player.inventory.clear()
            player.inventory.extend(data["player"]["inventory"])
            player.hp = data["player"]["hp"]

            # Restore each room’s items, connections, and visited
            for name, ro_data in data["rooms"].items():
                if name in rooms:
                    rooms[name].load_dynamic(ro_data)

            print("\n💾  Game loaded!\n")
    except FileNotFoundError:
        print("\n⚠️  No save file found.\n")

def handle_pickup(player, rooms, item_name):
    """
    Player picks up an item from the current room if it exists there.
    """
    current = rooms[player.location]
    if item_name in current.items:
        player.pick_up(item_name)
        current.remove_item(item_name)
        print(f"\n✅  You picked up the {item_name}!\n")
    else:
        print("\n⚠️  There is no such item here.\n")

def handle_combat(player):
    """
    Turn-based combat system. The player may have weapons/armor that affect attack/defense.
    A small Goblin enemy appears with defined stats.
    """
    # Instantiate a basic enemy (Goblin)
    goblin = Enemy(name="Goblin", hp=5, attack=1)

    print("\n⚔️  A wild Goblin appears!")
    time.sleep(1)

    # Determine player's base attack and defense from inventory
    player_attack = player.attack_power(items_data)
    player_defense = player.defense_bonus(items_data)

    while player.hp > 0 and goblin.hp > 0:
        # Player’s choice
        choice = input("🗡️  Do you want to [attack], [defend], or [run]? ").strip().lower()

        if choice == "attack":
            # Player deals damage to Goblin
            goblin.hp -= player_attack
            print(f"✅  You strike the {goblin.name} for {player_attack} damage!")
            if goblin.hp > 0:
                print(f"   {goblin.name} HP is now {goblin.hp}.\n")
            else:
                print(f"   {goblin.name} is defeated!\n")

        elif choice == "defend":
            print("🛡️  You brace for the Goblin’s next attack, reducing incoming damage this round.")
            defending = True

        elif choice == "run":
            chance = random.random()
            if chance < 0.5:
                print("🏃  You managed to flee safely!\n")
                return
            else:
                print("⚠️  You couldn't escape!\n")
                defending = False

        else:
            print("⚠️  Invalid action. Please choose [attack], [defend], or [run].\n")
            continue  # Skip Goblin’s turn, prompt player again

        # Goblin’s turn (only if still alive)
        if goblin.hp > 0:
            dmg = goblin.attack
            if choice == "defend":
                dmg = max(dmg - 1, 0)     # Defending reduces damage by 1
            dmg = max(dmg - player_defense, 0)  # Armor reduces damage further

            player.hp -= dmg
            print(f"⚠️  The {goblin.name} hits you for {dmg} damage!")
            print(f"   Your HP is now {player.hp}.\n")

            if player.hp <= 0:
                print("💀  You have been defeated by the Goblin. Game over!")
                exit()

        time.sleep(1)

    # If loop exits because goblin.hp <= 0
    print("🎉  You have slain the Goblin!\n")

def handle_riddle(player, rooms):
    """
    If the player is in the Cave and the torch is still in the room,
    present the riddle. Correct answer unlocks Hidden Chamber.
    """
    if player.location == "Cave":
        current = rooms["Cave"]
        if "torch" in current.items:  # Riddle only if torch still there
            print("\n🧩  A voice whispers: 'I speak without a mouth and hear without ears. What am I?'")
            answer = input("📝  Your answer: ").lower()
            if answer == "echo":
                print("✅  Correct! A secret passage to the Hidden Chamber opens.\n")
                current.add_connection("Hidden Chamber")
            else:
                print("❌  That's not the right answer. Try again later.\n")

def show_map(rooms, player):
    """
    If the player has a map in inventory, display all rooms and their connections.
    """
    if "map" in player.inventory:
        print("\n🗺️  World Map:")
        for room_obj in rooms.values():
            print(f"  - {room_obj.name} → {', '.join(room_obj.connections)}")
        print()
    else:
        print("\n⚠️  You need to pick up a map first.\n")

def show_help():
    """
    Display a list of available commands.
    """
    print("\n📜  Available commands:")
    print("- view inventory        (shows your carried items)")
    print("- hint                  (shows a hint for this room)")
    print("- save                  (save your progress)")
    print("- load                  (load from last save)")
    print("- use [item]            (use an item from inventory)")
    print("- pick up [item]        (pick up an item in the room)")
    print("- fight                 (engage in combat if available)")
    print("- open chest            (only works in Hidden Chamber if you have a key)")
    print("- map                   (view world map if you have a map)")
    print("- help                  (show this list again)")
    print("- quit                  (exit the game)\n")

def handle_open_chest(player, rooms):
    """
    If the player is in Hidden Chamber and has a key, they win.
    """
    if player.location == "Hidden Chamber":
        if "key" in player.inventory:
            print("\n🎉  You use the key to unlock the chest and find the legendary treasure.")
            print("\n🎊  Congratulations! You completed your adventure!\n")
            exit()
        else:
            print("\n🗝️  The chest is locked. You need a key.\n")
    else:
        print("\n⚠️  There is no chest to open here.\n")

def handle_command(player, rooms, items_data, command):
    """
    Parse and execute the player's command.
    """
    cmd = command.strip().lower()

    if cmd == "quit":
        print("\n👋  Thanks for playing! Goodbye!\n")
        exit()

    elif cmd == "view inventory":
        inv = ", ".join(player.inventory) if player.inventory else "empty"
        print(f"\n🎒  Your inventory: {inv}\n")

    elif cmd == "save":
        save_game(player, rooms)

    elif cmd == "load":
        load_game(player, rooms)

    elif cmd == "hint":
        hint_text = rooms[player.location].hints
        print(f"\n💡  Hint: {hint_text}\n")

    elif cmd.startswith("use "):
        item_name = cmd[4:].strip()
        player.use_item(item_name, items_data)

    elif cmd.startswith("pick up "):
        item_name = cmd[8:].strip()
        handle_pickup(player, rooms, item_name)

    elif cmd == "fight":
        handle_combat(player)

    elif cmd == "open chest":
        handle_open_chest(player, rooms)

    elif cmd == "map":
        show_map(rooms, player)

    elif cmd == "help":
        show_help()

    else:
        # Attempt to move to a connected room
        current_room = rooms[player.location]
        if cmd in [r.lower() for r in current_room.connections]:
            for room_name in current_room.connections:
                if room_name.lower() == cmd:
                    print(f"\n🚶  Moving to {room_name}...\n")
                    player.move_to(room_name)
                    break
        else:
            # If in Cave, always check riddle prompt on any invalid input
            if player.location == "Cave":
                handle_riddle(player, rooms)
            else:
                print("\n⚠️  I don’t understand that command.\n")


# ----------------------------
#   Main Game Loop
# ----------------------------

def main_game_loop():
    # Initialize player
    player = Player(start_location="Forest Entrance", hp=10)
    print("\n✨  Welcome to the Mini Adventure Game! ✨")
    print("Type 'help' at any time to see available commands.\n")
    time.sleep(1)

    while True:
        show_room(player, rooms)
        random_event(player)
        command = input("👉  What do you want to do? ")
        handle_command(player, rooms, items_data, command)
        time.sleep(0.5)


if __name__ == "__main__":
    main_game_loop()
