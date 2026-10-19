from enum import Enum

from pydantic import BaseModel, Field


class LockerStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class CompartmentSize(str, Enum):
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"


class CompartmentStatus(str, Enum):
    FREE = "free"
    RESERVED = "reserved"
    OCCUPIED = "occupied"
    OUT_OF_SERVICE = "out_of_service"


class LockerCreate(BaseModel):
    id: str = Field(min_length=3, max_length=32)
    name: str = Field(min_length=2, max_length=100)
    address: str = Field(min_length=3, max_length=200)
    city: str = Field(min_length=2, max_length=80)
    status: LockerStatus = LockerStatus.ONLINE


class Locker(LockerCreate):
    pass


class CompartmentCreate(BaseModel):
    id: str = Field(min_length=1, max_length=32)
    size: CompartmentSize


class Compartment(CompartmentCreate):
    locker_id: str
    status: CompartmentStatus = CompartmentStatus.FREE


class CompartmentStatusUpdate(BaseModel):
    status: CompartmentStatus
