from aiogram import Router, types
from aiogram.filters import Command

router = Router()

from . import login
from . import register