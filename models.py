from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel


class EType(str, Enum):
    OBSTACLE = "OBSTACLE"
    PATH = "PATH"
    START = "START"
    END = "END"
    SHELF = "SHELF"


class Cell(BaseModel):
    type: EType
    id: Union[str, None, int] = None


class MapProcessRequest(BaseModel):
    map: List[List[Cell]]
    mapid: Union[str, int]
    jobid: Union[str, int]


class MapProcessResponse(BaseModel):
    jobid: Union[str, int]
    status: str  # "complete" or "error"
    errormessage: Optional[str] = None


class Distance(BaseModel):
    from_id: str
    to_id: str
    distance: int


class TSPRequest(BaseModel):
    jobid: str
    mapid: Union[str, int]
    point_of_interest: List[Union[str, int]]


class TSPResponse(BaseModel):
    point_of_interest: Optional[List[str]] = None  # Always strings (matches stored distances)
    jobid: str
    errormessage: Optional[str] = None
    status: str  # "complete" or "error"
