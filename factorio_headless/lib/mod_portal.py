import os
import pathlib
import requests

from datetime import datetime

from .data_objects import Dependency, PlayerData
from .mod_handling import MODS_SRC

MANAGED_MODS_DIR = os.path.join(MODS_SRC, '__managed_mods')


def parse_dependency_list(dependencies: list[str], keep_optional: bool = False) -> list[str]:
    needed_dependencies = []
    for d in dependencies:
        dep = Dependency(d)
        if dep.required or (dep.compatible and keep_optional):
            needed_dependencies.append(dep.mod_name)
    return needed_dependencies


def get_latest_version(mod_data: dict) -> dict:
    latest_version = {"released_at": datetime.fromisoformat('1970-01-01')}
    for release in mod_data['releases']:
        release['released_at'] = datetime.fromisoformat(release['released_at'][:-1]) # Need to remove "Z" from the end
        if latest_version['released_at'] < release['released_at']:
            latest_version = release
    return latest_version


def find_mod_dependencies(mod_data: dict) -> list[str]:
    latest_version = get_latest_version(mod_data)
    dependencies = latest_version['info_json']['dependencies']
    return parse_dependency_list(dependencies)


def get_download_list(mods: set[str]) -> set[str]:
    download_names = set()
    for m in mods:
        mod_data = requests.get(f'https://mods.factorio.com/api/mods/{m}/full').json()
        download_names.add(m)
        download_names.update(find_mod_dependencies(mod_data))
    download_names.discard('base')
    return download_names


def download_single_mod(mod: str, player_data: PlayerData, dst_dir: str, chunk_size: int = 8192) -> None:
    mod_data = requests.get(f'https://mods.factorio.com/api/mods/{mod}/full').json()
    release = get_latest_version(mod_data)
    dst_file = os.path.join(dst_dir, release['file_name'])
    url = f'https://mods.factorio.com{release["download_url"]}'
    with requests.get(url, params=player_data.as_params(), stream=True) as r:
        r.raise_for_status()
        if 'Content-Type' in r.headers and r.headers['Content-Type'] == 'application/octet-stream':
            with open(dst_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
        else:
            h = str(dict(r.headers))
            raise RuntimeError(f'Unexpected Content-Type returned for {mod}, headers: {h}')


def download_mods(mods: set[str], player_data: PlayerData, dst_dir: str = MANAGED_MODS_DIR):
    pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)
    for mod in get_download_list(mods):
        download_single_mod(mod, player_data, dst_dir)

