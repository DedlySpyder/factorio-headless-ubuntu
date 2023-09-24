import os
import pathlib
import requests

from datetime import datetime

from .data_objects import Dependency
from .mod_handling import MODS_SRC

MANAGED_MODS_DIR = os.path.join(MODS_SRC, '__managed_mods')


def parse_dependency_list(dependencies: list[str], keep_optional: bool = False) -> list[str]:
    needed_dependencies = []
    for d in dependencies:
        dep = Dependency(d)
        if dep.required or (dep.compatible and keep_optional):
            needed_dependencies.append(dep.mod_name)
    return needed_dependencies


# def get_latest_version(mod_data: dict) -> dict:
#     latest_version = {"released_at": datetime.fromisoformat('1970-01-01')}
#     for release in mod_data['releases']:
#         release['released_at'] = datetime.fromisoformat(release['released_at'][:-1]) # Need to remove "Z" from the end
#         if latest_version['released_at'] < release['released_at']:
#             latest_version = release
#     return latest_version


# def find_mod_dependencies(mod_data: dict) -> list[str]:
#     latest_version = get_latest_version(mod_data)
#     dependencies = latest_version['info_json']['dependencies']
#     return parse_dependency_list(dependencies)


# # player_data: PlayerData, 
# def download_mods(mods: set[str], dst_dir: str = MANAGED_MODS_DIR):
#     pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)
#     dependencies = set()
#     for m in mods:
#         mod_data = requests.get(f'https://mods.factorio.com/api/mods/{m}/full').json()
#         dependencies.update(find_mod_dependencies(mod_data))
#         print('find dependencies and merge into mods')
#     mods.extend(dependencies) # TODO - need to remove "base"
#     return mods
    
#     for m in mods:
#         print('actually download the mods to the dst dir')
#     pass
