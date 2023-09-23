from dataclasses import dataclass
from typing import Tuple

@dataclass
class Dependency():
    compatible = True
    required = True
    
    # Parses these: https://wiki.factorio.com/Tutorial:Mod_structure#Dependency
    def __init__(self, info_dependency: str) -> None:
        parts = info_dependency.split()
        parts_l = len(parts)
        if parts_l == 1:
            self.mod_name = parts[0]
        elif parts_l == 2:
            self.compatible, self.required = self._parse_compatibility_operator(parts[0])
            self.mod_name = parts[1]
        elif parts_l == 3:
            self.mod_name = parts[0]
            self.equality = parts[1]
            self.version = parts[2]
        elif parts_l == 4:
            self.compatible, self.required = self._parse_compatibility_operator(parts[0])
            self.mod_name = parts[1]
            self.equality = parts[2]
            self.version = parts[3]
        else:
            raise NotImplementedError(f'Unknown depdendency string format: {info_dependency}')
    
    
    def _parse_compatibility_operator(self, operator: str) -> Tuple[bool, bool]:
        if operator == '!':
            return False, False
        elif operator == '?' or operator == '(?)':
            return True, False
        elif operator == '~':
            return True, True
        else:
            raise NotImplementedError(f'Unknown compatibility operator: {operator}')

# @dataclass
# class PlayerData(): # TODO - allow setting the values or loading from a file
#     username: str = ''
#     token: str = ''
#     def __init__(self) -> None:
#         pass