import os
import pathlib
import shutil

MODS_TEMP_ROOT = os.path.abspath('./tests/resources/.temp/')

class TestResources():
    mods_root = os.path.abspath('./tests/resources/mods')
    
    def __init__(self, mod_name) -> None:
        self.temp_dir = os.path.join(MODS_TEMP_ROOT, mod_name)
        pathlib.Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
    
    def build_test_dir(self, test_name) -> None:
        test_dir = os.path.join(self.temp_dir, test_name)
        if not os.path.exists(test_dir):
            os.mkdir(test_dir)
    
    def cleanup(self) -> None:
        shutil.rmtree(self.temp_dir)
