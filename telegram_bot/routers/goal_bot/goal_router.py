from aiogram import Router
from ...middleware import AuthMiddleware

router = Router()

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())
