import inspect
import os
import pathlib
import shutil

MODS_TEMP_ROOT = os.path.abspath('./tests/.temp/')

class TestResources():
    mods_root = os.path.abspath('./tests/resources/mods')
    
    def __init__(self, mod_name: str) -> None:
        self.temp_dir = os.path.join(MODS_TEMP_ROOT, mod_name)
        pathlib.Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
    
    def build_test_dir(self) -> str:
        test_name = inspect.stack()[1][3] # Get the calling function's name
        test_dir = os.path.join(self.temp_dir, test_name)
        pathlib.Path(test_dir).mkdir(exist_ok=True)
        return test_dir
    
    def cleanup(self) -> None:
        shutil.rmtree(self.temp_dir)
