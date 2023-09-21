import os
import pathlib
import shutil

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
    """Strip the source from a file and replace it with a new directory

    Args:
        file (str): The file to modify
        src (str): The root source of the file
        dst (str): New directory to replace the src

    Returns:
        str: Modified file string
    """
    new_src = strip_source(file, src)
    return os.path.join(dst, new_src)


def list_source_mod_files(trunk: str) -> list[str]:
    """List all files under a directory

    Args:
        trunk (str): Root directory to search for files

    Returns:
        list[str]: File list
    """
    all_files = []
    for root, _, files in os.walk(trunk):
        for f in files:
            all_files.append(os.path.join(root, f))
    return all_files


def delete_directory_contents(directory: str) -> None:
    """Delete everything INSIDE of a directory, leaving the directory in place

    Args:
        directory (str): Directory name
    """
    for root, dirs, files in os.walk(directory):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def create_dir_for_file(file: str) -> None:
    """Create the parent directory, recursively, for a file if it/they not exist

    Args:
        file (str): filename
    """
    dir = os.path.split(file)[0]
    if not os.path.exists(dir):
        pathlib.Path(dir).mkdir(parents=True)


def merge_mods(root_src_dir: str=MODS_SRC, dst_mod_dir: str=MODS_DST) -> None:
    """Merge all of the mod files in the source to the destination mod directory.
    
    The source directory is assumed to have multiple child directories, that each
    contain files like a Factorio mod directory. This function will merge zip files
    and all loose files under mod directories.
    
    Expected structure under root_src_dir:
        .
        ├── mod_source1
        │   ├── mod1_0.1
        │   │   └── info.json
        │   └── mod2_1.0.zip
        └── mod_source2
            ...
    
    The destination directory should be the Factorio mod directory.

    Args:
        root_src_dir (str, optional): Directory of mod directories. Defaults to MODS_SRC.
        dst_mod_dir (str, optional): Factorio mod directory. Defaults to MODS_DST.
    """
    delete_directory_contents(dst_mod_dir)
    for src_file in list_source_mod_files(root_src_dir):
        dst_file = replace_source(src_file, root_src_dir, dst_mod_dir)
        create_dir_for_file(dst_file)
        os.symlink(src_file, dst_file)
