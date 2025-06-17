import random
import json
import time
import tkinter as tk
from tkinter import messagebox, simpledialog

# ----------------------------
#   Game Logic (same as before)
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
        self.visited = False

    def remove_item(self, item_name):
        if item_name in self.items:
            self.items.remove(item_name)

    def add_connection(self, new_room_name):
        if new_room_name not in self.connections:
            self.connections.append(new_room_name)

    def to_dict(self):
        return {
            "items": self.items,
            "connections": self.connections,
            "visited": self.visited
        }

    def load_dynamic(self, data):
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
        if item_name not in self.inventory:
            return f"⚠️ You don’t have {item_name} in your inventory."

        item = items_data.get(item_name)
        if not item:
            return f"⚠️ You can’t use {item_name} now."

        item_type = item.get("type")
        desc = item.get("description", "You use the item.")

        if item_type == "healing":
            heal_amt = item.get("heal_amount", 0)
            self.hp += heal_amt
            self.inventory.remove(item_name)
            return f"✨ {desc}\n❤️ Your HP is now {self.hp}."
        elif item_type == "light":
            return f"✨ {desc}"
        elif item_type == "weapon":
            return f"✨ {desc}"
        elif item_type == "armor":
            return f"✨ {desc}"
        elif item_type == "mystical":
            return f"✨ {desc}"
        elif item_type == "unlock":
            return f"✨ {desc}"
        else:
            return "❔ You’re not sure what effect this has…"

    def attack_power(self, items_data):
        base = 1
        for item_name in self.inventory:
            item = items_data.get(item_name)
            if item and item.get("type") == "weapon":
                base += item.get("damage", 0)
        return base

    def defense_bonus(self, items_data):
        bonus = 0
        for item_name in self.inventory:
            item = items_data.get(item_name)
            if item and item.get("type") == "armor":
                bonus += item.get("defense", 0)
        return bonus


# ----------------------------
#   Load & Randomize Rooms
# ----------------------------

def load_rooms_raw(filename):
    with open(filename, "r") as f:
        return json.load(f)

def load_items(filename):
    with open(filename, "r") as f:
        return json.load(f)

raw_rooms_data = load_rooms_raw("rooms.json")
items_data = load_items("items.json")

# Preserve item counts per room, then shuffle pool
room_item_counts = { name: len(d.get("items", [])) for name, d in raw_rooms_data.items() }
all_items = []
for d in raw_rooms_data.values():
    all_items.extend(d.get("items", []))
random.shuffle(all_items)

new_rooms_data = {}
idx = 0
for room_name, data in raw_rooms_data.items():
    count = room_item_counts[room_name]
    assigned = all_items[idx: idx + count]
    idx += count
    new_rooms_data[room_name] = {
        "description": data["description"],
        "items": assigned,
        "connections": data["connections"],
        "hints": data.get("hints", "")
    }

rooms = { name: Room(name, info) for name, info in new_rooms_data.items() }


# ----------------------------
#   Turn-Based Combat (returns a string)
# ----------------------------

def handle_combat(player):
    goblin = Enemy(name="Goblin", hp=5, attack=1)
    log = ["⚔️ A wild Goblin appears!"]
    time.sleep(0.5)

    while player.hp > 0 and goblin.hp > 0:
        # For GUI, we ask the player via a simple dialog prompt:
        action = simpledialog.askstring(
            "Combat",
            "Choose: [attack], [defend], or [run]:"
        )
        if action is None:
            return "\n⚠️ Combat canceled."
        action = action.strip().lower()

        if action == "attack":
            pa = player.attack_power(items_data)
            goblin.hp -= pa
            log.append(f"✅ You strike the Goblin for {pa} damage!")
            if goblin.hp > 0:
                log.append(f"   Goblin HP now {goblin.hp}.")
            else:
                log.append("   Goblin is defeated!")
        elif action == "defend":
            log.append("🛡️ You brace for the Goblin’s next attack (–1 dmg).")
            defending = True
        elif action == "run":
            if random.random() < 0.5:
                log.append("🏃 You managed to flee safely!")
                return "\n".join(log)
            else:
                log.append("⚠️ You couldn't escape!")
                defending = False
        else:
            log.append("⚠️ Invalid choice; try attack/defend/run.")
            continue  # Skip Goblin’s turn

        # Goblin’s turn
        if goblin.hp > 0:
            dmg = goblin.attack
            if action == "defend":
                dmg = max(dmg - 1, 0)
            dmg = max(dmg - player.defense_bonus(items_data), 0)
            player.hp -= dmg
            log.append(f"⚠️ Goblin hits you for {dmg} damage (Your HP: {player.hp})")
            if player.hp <= 0:
                log.append("💀 You were defeated by the Goblin. Game over!")
                return "\n".join(log)
        time.sleep(0.2)

    log.append("🎉 You have slain the Goblin!")
    return "\n".join(log)


# ----------------------------
#   GUI / Tkinter View
# ----------------------------

class AdventureGUI(tk.Tk):
    def __init__(self, player, rooms, items_data):
        super().__init__()
        self.title("Mini Adventure Game")
        self.geometry("800x600")
        self.player = player
        self.rooms = rooms
        self.items_data = items_data

        # ----- Top Frame: Room Description -----
        self.desc_frame = tk.Frame(self)
        self.desc_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=(10,0))

        self.room_label = tk.Label(self.desc_frame, text="", font=("Helvetica", 16, "bold"))
        self.room_label.pack(anchor="w")

        self.text_widget = tk.Text(self.desc_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.text_widget.pack(fill=tk.X)

        # ----- Middle Frame: Items & Inventory -----
        self.mid_frame = tk.Frame(self)
        self.mid_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        # Items in Room Listbox
        tk.Label(self.mid_frame, text="Items in Room:", font=("Helvetica", 12, "underline")).grid(row=0, column=0, sticky="w")
        self.room_items_list = tk.Listbox(self.mid_frame, height=6)
        self.room_items_list.grid(row=1, column=0, padx=5, sticky="nsew")

        # Inventory Listbox
        tk.Label(self.mid_frame, text="Your Inventory:", font=("Helvetica", 12, "underline")).grid(row=0, column=1, sticky="w")
        self.inv_list = tk.Listbox(self.mid_frame, height=6)
        self.inv_list.grid(row=1, column=1, padx=5, sticky="nsew")

        # ----- Right Frame: Buttons & Map -----
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        # Movement Buttons container
        self.move_frame = tk.LabelFrame(self.right_frame, text="Move To", padx=5, pady=5)
        self.move_frame.pack(fill=tk.X, pady=(0,10))

        # Hint & Map Buttons
        self.hint_button = tk.Button(self.right_frame, text="Hint", command=self.show_hint)
        self.hint_button.pack(fill=tk.X, pady=3)

        self.map_button = tk.Button(self.right_frame, text="Map", command=self.show_map)
        self.map_button.pack(fill=tk.X, pady=3)

        # Save / Load Buttons
        self.save_button = tk.Button(self.right_frame, text="Save", command=self.save_game)
        self.save_button.pack(fill=tk.X, pady=3)

        self.load_button = tk.Button(self.right_frame, text="Load", command=self.load_game)
        self.load_button.pack(fill=tk.X, pady=3)

        # Quit Button
        self.quit_button = tk.Button(self.right_frame, text="Quit", command=self.quit_game)
        self.quit_button.pack(fill=tk.X, pady=3)

        # ----- Bottom Frame: Action Buttons & Combat Log -----
        self.bottom_frame = tk.LabelFrame(self, text="Actions / Console", padx=5, pady=5)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        # Action Buttons (Pick Up, Use, Fight, Open Chest)
        self.pick_button = tk.Button(self.bottom_frame, text="Pick Up", command=self.pick_up_item)
        self.pick_button.grid(row=0, column=0, padx=5, pady=5)

        self.use_button = tk.Button(self.bottom_frame, text="Use", command=self.use_item)
        self.use_button.grid(row=0, column=1, padx=5, pady=5)

        self.fight_button = tk.Button(self.bottom_frame, text="Fight", command=self.fight_enemy)
        self.fight_button.grid(row=0, column=2, padx=5, pady=5)

        self.open_button = tk.Button(self.bottom_frame, text="Open Chest", command=self.open_chest)
        self.open_button.grid(row=0, column=3, padx=5, pady=5)

        # Combat / Console Log (Text widget)
        self.log_widget = tk.Text(self.bottom_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_widget.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=5)

        # Configure grid weights for bottom_frame
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_columnconfigure(2, weight=1)
        self.bottom_frame.grid_columnconfigure(3, weight=1)
        self.bottom_frame.grid_rowconfigure(1, weight=1)

        # Make mid_frame columns expand
        self.mid_frame.grid_columnconfigure(0, weight=1)
        self.mid_frame.grid_columnconfigure(1, weight=1)

        # Finally, draw the initial room state
        self.refresh_ui()


    def refresh_ui(self):
        """
        Update all widgets (description, room items, inventory, move buttons, etc.)
        to reflect the player's current state.
        """
        current_room = self.rooms[self.player.location]

        # — Update Room Name & Description —
        self.room_label.config(text=current_room.name)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)

        if not current_room.visited:
            self.text_widget.insert(tk.END, current_room.description + "\n")
            current_room.visited = True
        else:
            self.text_widget.insert(tk.END, f"You return to the {current_room.name}.\n")

        self.text_widget.config(state=tk.DISABLED)

        # — Update Room's Items Listbox —
        self.room_items_list.delete(0, tk.END)
        for itm in current_room.items:
            self.room_items_list.insert(tk.END, itm)

        # — Update Player Inventory Listbox —
        self.inv_list.delete(0, tk.END)
        for itm in self.player.inventory:
            self.inv_list.insert(tk.END, itm)

        # — Update Move-To Buttons —
        for widget in self.move_frame.winfo_children():
            widget.destroy()

        for target in current_room.connections:
            btn = tk.Button(self.move_frame, text=target, command=lambda t=target: self.move_player(t))
            btn.pack(side=tk.LEFT, padx=2, pady=2)


    def move_player(self, room_name):
        self.player.move_to(room_name)
        self.refresh_ui()


    def pick_up_item(self):
        """
        Called when “Pick Up” is clicked.
        We look at the selected item in room_items_list, then move it to inventory.
        """
        sel = self.room_items_list.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select an item in the room to pick up.")
            return
        item_name = self.room_items_list.get(sel[0])
        self.player.pick_up(item_name)
        self.rooms[self.player.location].remove_item(item_name)
        self.log(f"✅ Picked up {item_name}.")
        self.refresh_ui()


    def use_item(self):
        """
        Called when “Use” is clicked.
        We prompt a simple dialog for which item to use.
        """
        if not self.player.inventory:
            messagebox.showwarning("Inventory empty", "You have no items to use.")
            return

        # Ask which item to use:
        item_name = simpledialog.askstring("Use Item", "Type item name:")
        if not item_name:
            return

        item_name = item_name.strip().lower()
        # Find exact match in inventory (case‐insensitive)
        match = None
        for itm in self.player.inventory:
            if itm.lower() == item_name:
                match = itm
                break
        if not match:
            messagebox.showwarning("Not in inventory", f"You don't have '{item_name}'.")
            return

        result = self.player.use_item(match, self.items_data)
        self.log(result)
        self.refresh_ui()


    def fight_enemy(self):
        """
        Called when “Fight” is clicked.
        Runs the turn‐based combat and prints the log.
        """
        combat_log = handle_combat(self.player)
        self.log(combat_log)
        self.refresh_ui()


    def open_chest(self):
        """
        Called when “Open Chest” is clicked.
        Checks if in Hidden Chamber and if player has a key.
        """
        if self.player.location == "Hidden Chamber":
            if "key" in self.player.inventory:
                messagebox.showinfo("Victory", "🎉 You use the key and claim the treasure!\n\nCongratulations—you win!")
                self.quit()
            else:
                self.log("⚠️ The chest is locked; you need a key.")
        else:
            self.log("⚠️ There is no chest here.")


    def show_hint(self):
        """
        Show the hint for the current room.
        """
        hint_text = self.rooms[self.player.location].hints
        if hint_text:
            messagebox.showinfo("Hint", hint_text)
        else:
            messagebox.showinfo("Hint", "No hint for this room.")


    def show_map(self):
        """
        Display a simple text map if player has a 'map'.
        """
        if "map" in self.player.inventory:
            lines = ["🗺️  World Map:"]
            for r in self.rooms.values():
                lines.append(f"  - {r.name} → {', '.join(r.connections)}")
            messagebox.showinfo("World Map", "\n".join(lines))
        else:
            messagebox.showwarning("No Map", "⚠️ You need to pick up the map first.")


    def save_game(self):
        """
        Save player and room dynamic state.
        """
        rooms_dynamic = { name: room.to_dict() for name, room in self.rooms.items() }
        data = {
            "player": {
                "location": self.player.location,
                "inventory": self.player.inventory,
                "hp": self.player.hp
            },
            "rooms": rooms_dynamic
        }
        with open("savegame.json", "w") as f:
            json.dump(data, f)
        self.log("💾 Game saved.")


    def load_game(self):
        """
        Load player and room dynamic state.
        """
        try:
            with open("savegame.json", "r") as f:
                data = json.load(f)

                # Restore player
                self.player.location = data["player"]["location"]
                self.player.inventory = data["player"]["inventory"]
                self.player.hp = data["player"]["hp"]

                # Restore rooms
                for name, rd in data["rooms"].items():
                    if name in self.rooms:
                        self.rooms[name].load_dynamic(rd)

            self.log("💾 Game loaded.")
            self.refresh_ui()
        except FileNotFoundError:
            messagebox.showwarning("No Save", "⚠️ No save file found.")


    def quit_game(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.destroy()


    def log(self, text):
        """
        Append a line (or multiple lines) to the bottom “console” Text widget.
        """
        self.log_widget.config(state=tk.NORMAL)
        self.log_widget.insert(tk.END, text + "\n")
        self.log_widget.see(tk.END)
        self.log_widget.config(state=tk.DISABLED)


# ----------------------------
#   Main Game Loop (GUI launch)
# ----------------------------

if __name__ == "__main__":
    player = Player(start_location="Forest Entrance", hp=10)
    app = AdventureGUI(player, rooms, items_data)
    app.mainloop()
