from aiogram import Router, types
from aiogram.filters import Command

from ...middleware import AuthMiddleware

router = Router()

from . import topic_add
from . import topic_get
from . import topic_delete
from . import topic_update
from . import topic_patch

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())