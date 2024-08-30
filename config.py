# config.py
import json
import os

class Config:
    def __init__(self, save_directory):
        self.config_file = os.path.join(save_directory, "config.json")

    def load_config(self):
        """Charge la configuration depuis un fichier JSON."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        """Sauvegarde la configuration dans un fichier JSON."""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)
