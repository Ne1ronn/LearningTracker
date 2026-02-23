from aiogram import Router

from ...middleware import AuthMiddleware, RoleMiddleware

router = Router()

from . import topic_add
from . import topic_get
from . import topic_delete
from . import topic_update
from . import topic_patch

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())
router.message.middleware(RoleMiddleware())
router.callback_query.middleware(RoleMiddleware())