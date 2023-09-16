import os

from collections.abc import Callable

MODS_ROOT='/opt/headless_factorio/mods'


def apply_to_leaves(trunk: str, func: Callable[[str], None]):
    for root, _, files in os.walk(trunk):
        for f in files:
            func(os.path.join(root, f))

# def merge_mods(root_dir=MODS_ROOT):