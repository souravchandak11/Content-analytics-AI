
import os
import sys
import src
print(f"src file: {src.__file__}")
from src.database import check_database_connection
print("Successfully imported check_database_connection")
