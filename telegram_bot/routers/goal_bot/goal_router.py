from aiogram import Router
from ...middleware import AuthMiddleware

from . import goal_add, goal_get, goal_delete, goal_patch

router = Router()

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())
