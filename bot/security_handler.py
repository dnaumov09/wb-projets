from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject

from db.user import get_user


class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if get_user(event.chat.id):
            return await handler(event, data)
        else:
            return None
        
        # if not isinstance(event, Message):
        #     return await handler(event, data)

        # authorization = get_flag(data, "authorization")
        # if authorization is not None:
        #     if authorization["is_authorized"]:
        #         if get_user(event.chat.id):
        #             return await handler(event, data)
        #         else:
        #             return None
        # else:
        #     return await handler(event, data)
        


# Antiflood middleware
# https://docs.aiogram.dev/en/v2.25.1/examples/middleware_and_antiflood.html