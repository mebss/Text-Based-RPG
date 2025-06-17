# Text-Based RPG Engine

A Python-powered adventure engine where rooms and items are defined in external JSON files. Players explore a world, manage an inventory, engage in turn-based combat, face random hazards, unlock treasure chests, and save/load their progress. A simple Tkinter GUI wraps the console core for an optional graphical experience.

---

## Features

- **JSON-driven content**  
  Rooms and items are loaded at runtime from `rooms.json` and `items.json`.
- **Exploration**  
  Full and return-visit descriptions for each room.
- **Inventory management**  
  Pick up, drop, and examine items.
- **Turn-based combat**  
  Fight enemies with weapon and armor modifiers.
- **Random hazards & events**  
  Chance encounters, traps, and puzzles.
- **Treasure chest unlock**  
  Find keys and open locked containers.
- **Save / Load**  
  Persist progress to `savegame.json`.
- **Console & GUI**  
  Play in the terminal or via a Tkinter window (`gui.py`).

---

## 📦 Prerequisites

- Python 3.7 or higher  
- Built-in modules: `json`, `tkinter`, `random`, `sys`  
- (Optional) [colorama](https://pypi.org/project/colorama/) for colored console output  
  ```bash
  pip install colorama
  ```

---

## 🛠 Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/text-rpg-engine.git
   cd text-rpg-engine
   ```
2. **Verify files**  
   ```
   ├── gui.py
   ├── main.py
   ├── items.json
   ├── rooms.json
   ├── savegame.json
   └── README.md
   ```

---

## 🚀 Usage

### Console Version

```bash
python main.py
```

When prompted, enter commands like:

- `north`, `south`, `east`, `west` to move
- `look` to reprint the room description
- `take <item>` / `drop <item>`
- `inventory` to view your items
- `attack <enemy>` to fight
- `save` / `load` to persist or resume

### GUI Version

```bash
python gui.py
```

Use the on-screen buttons and text entry to navigate, battle, and manage inventory.

---

## ⚙️ Configuration Files

### `rooms.json`

Defines all rooms:
```json
[
  {
    "id": "entrance",
    "name": "Cavern Entrance",
    "description": {
      "first": "A dark cave mouth yawns before you...",
      "return": "You stand again at the cave entrance."
    },
    "exits": { "north": "hallway" },
    "items": ["torch"],
    "hazards": ["slippery_floor"]
  },
  ...
]
```

### `items.json`

Defines items and stats:
```json
[
  {
    "id": "torch",
    "name": "Wooden Torch",
    "type": "tool",
    "description": "Lights up dark areas.",
    "value": 0
  },
  {
    "id": "rusty_sword",
    "name": "Rusty Sword",
    "type": "weapon",
    "attack": 4,
    "durability": 10
  },
  ...
]
```

### `savegame.json`

Automatically created when you `save`. Holds your current room, inventory, HP, etc.

---

## 🛠 Development

- **Add new rooms/items** by editing the JSON files.
- **Adjust combat mechanics** in `main.py` under `CombatEngine`.
- **Extend GUI** by updating `gui.py`—it wraps the same core functions as the console.

---

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/X`)  
3. Commit your changes (`git commit -m "Add X"`)  
4. Push to the branch (`git push origin feature/X`)  
5. Open a Pull Request

---

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

---

> Built as an interactive coding exercise for Year 12 Computer Science students at Enrich Academy, teaching data-driven design, OOP principles, and user interaction in Python.
