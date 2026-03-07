from aiogram import Router
from ...middleware import AuthMiddleware

router = Router()

from . import entry_add
from . import entry_get
from .get_all_entries import entry_get_all, filters, sorting, pagination
from . import entry_delete
from . import entry_update
from . import entry_patch
from . import summary
from . import entry_stats
from . import entry_streak

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())