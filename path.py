import os
import sys
from pathlib import Path

from kivy.core.window import Window

os.environ["KIVY_PROFILE_LANG"] = "1"

if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["ENTITY_CLIENT_ROOT"] = sys._MEIPASS

else:
    sys.path.append(os.path.abspath(__file__).split("client_entity")[0])
    os.environ["ENTITY_CLIENT_ROOT"] = str(Path(__file__).parent)

os.environ["ENTITY_CLIENT_ASSETS"] = os.path.join(os.environ["ENTITY_CLIENT_ROOT"], f"assets{os.sep}")

Window.softinput_mode = "below_target"
dir_settings_file = f"{os.environ['ENTITY_CLIENT_ROOT']}/assets/resource_files/settings/GLOBAL_VAR.json"
dir_language = f"{os.environ['ENTITY_CLIENT_ROOT']}/assets/resource_files/language/spanish_after_login.json"
assets = f"{os.environ['ENTITY_CLIENT_ROOT']}/assets"