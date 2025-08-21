from typing import NamedTuple

from pydantic import BaseModel, Field

from datetime import datetime

from dataclasses import dataclass

from business.models.category import CategoryData


class ParsedJson(NamedTuple):
    data: list[dict]
    category: CategoryData


class UserData(BaseModel):
    wants_hired_percent: int
    wants_count: int


class User(BaseModel):
    username: str
    data: UserData


class File(BaseModel):
    fname: str
    size: int
    url: str


class Project(BaseModel):
    id: int
    name: str
    description: str
    price_limit: int = Field(alias="priceLimit")
    possible_price: int = Field(alias="possiblePriceLimit")
    date_active: datetime
    date_create: datetime
    date_expire: datetime
    time_left: str = Field(alias="timeLeft")
    kwork_count: int
    files: list[File] = []
    user: User
    category: CategoryData | None = None


@dataclass
class FileData:
    fname: str
    size: int
    url: str


@dataclass
class UserDataclass:
    username: str
    wants_hired_percent: int
    wants_count: int


@dataclass
class ProjectData:
    id: int
    name: str
    description: str
    price_limit: int
    possible_price: int
    date_active: datetime
    date_create: datetime
    date_expire: datetime
    time_left: str
    kwork_count: int
    user: UserDataclass
    category: CategoryData | None
    files: list[FileData]
