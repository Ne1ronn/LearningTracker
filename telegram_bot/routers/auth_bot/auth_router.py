from aiogram import Router
from  .logout import logout_router

router = Router()
router.include_router(logout_router)

from . import login
from . import register