import os
import pathlib
import shutil

from collections.abc import Callable

MODS_SRC='/opt/headless_factorio/mods'
MODS_DST='/opt/headless_factorio/game/mods'


def strip_source(file: str, src: str) -> str:
    """Strip the source of a file from the file path, plus 1 additional directory

    Args:
        file (str): The file to modify
        src (str): The root source of the file

    Returns:
        str: Modified file string
    
    Example:
        file: '/opt/headless_factorio/mods/source/mod_1/info.json'
        src: '/opt/headless_factorio/mods'
        
        return: 'mod_1/info.json'
    """
    temp = file.removeprefix(src)
    part_split = 1 if src.endswith('/') else 2
    return os.sep.join(temp.split(os.sep)[part_split:])


def replace_source(file: str, src: str, dst: str) -> str:
    new_src = strip_source(file, src)
    return os.path.join(dst, new_src)


def list_source_mod_files(trunk: str) -> list[str]:
    all_files = []
    for root, _, files in os.walk(trunk):
        for f in files:
            all_files.append(os.path.join(root, f))
    return all_files


def delete_directory_contents(directory: str) -> None:
    for root, dirs, files in os.walk(directory):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def merge_mods(root_src_dir=MODS_SRC, dst_mod_dir=MODS_DST) -> None:
    delete_directory_contents(dst_mod_dir)
    for src_file in list_source_mod_files(root_src_dir):
        dst_file = replace_source(src_file, root_src_dir, dst_mod_dir)
        dst_dir = os.path.split(dst_file)[0]
        if not os.path.exists(dst_dir):
            pathlib.Path(dst_dir).mkdir(parents=True)
        os.symlink(src_file, dst_file)
