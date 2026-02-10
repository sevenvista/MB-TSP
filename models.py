from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class EType(str, Enum):
    OBSTACLE = "OBSTACLE"
    PATH = "PATH"
    START = "START"
    END = "END"
    SHELF = "SHELF"


class Cell(BaseModel):
    type: EType
    id: Optional[str] = None


class MapProcessRequest(BaseModel):
    map: List[List[Cell]]
    mapid: str


class MapProcessResponse(BaseModel):
    jobid: str
    status: str  # "complete" or "error"
    errormessage: Optional[str] = None


class Distance(BaseModel):
    from_id: str
    to_id: str
    distance: int


class TSPRequest(BaseModel):
    jobid: str
    mapid: str
    point_of_interest: List[str]


class TSPResponse(BaseModel):
    point_of_interest: Optional[List[str]] = None
    jobid: str
    errormessage: Optional[str] = None
    status: str  # "complete" or "error"
