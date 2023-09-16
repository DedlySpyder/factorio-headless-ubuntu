import os

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
    

def list_source_mod_files(trunk: str, dst: str) -> list[tuple[str, str]]:
    all_files = []
    for root, _, files in os.walk(trunk):
        for f in files:
            src_f = os.path.join(root, f)
            dst_f = os.path.join(dst, strip_source(src_f, trunk))
            all_files.append((src_f, dst_f))
    return all_files


# def link_file(src: str, dst_root: str):
    
    

# def merge_mods(root_src_dir=MODS_SRC, root_dst_dir=MODS_DST) -> None:

    