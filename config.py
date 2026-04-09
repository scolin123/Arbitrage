import os
from dataclasses import dataclass,field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BookCredentials:
    username: str
    password: str


