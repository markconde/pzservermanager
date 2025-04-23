commands = {
    "additem": {
        "description": "Give an item to a player.",
        "usage": 'additem "username" "module.item" [count]',
        "params": ["username", "item", "count"]
    },
    "adduser": {
        "description": "Add a new user to a whitelisted server.",
        "usage": 'adduser "username" "password"',
        "params": ["username", "password"]
    },
    # ... add additional commands following the help output details ...
    "help": {
        "description": "List all available commands.",
        "usage": "help",
        "params": []
    }
}