
from dataclasses import dataclass
from pathlib import Path
from json import load, dump


def load_json(
    path: Path,
)-> dict:
    with open(path, 'r') as f:
        return load(f)


def dump_json(
    obj: dict,
    path: Path,
) -> None:
    with open(path, 'x') as f:
        return dump(
            obj, 
            f, 
            indent=4,
        )


def safer_convert_to_int(
    x,
):
    assert x.is_integer()
    return int(x)


@dataclass
class Interval:
    left:float
    right:float
    
    def __post_init__(
        self
    ):
        if self.left > self.right:
            raise ValueError(
                "Interval left bound must be greater" 
                " than or equal to right bound."
            )
        
    def __iter__(
        self,
    ):
        return (
            self.left, 
            self.right,
        ).__iter__()
    

def append_to_path_stem(
    path:Path, 
    s,
):
    return path.with_stem(f"{path.stem}{s}")