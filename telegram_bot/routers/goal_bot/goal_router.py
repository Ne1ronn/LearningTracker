from aiogram import Router
from ...middleware import AuthMiddleware

router = Router()

from . import goal_add, goal_get, goal_delete, goal_patch

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())
