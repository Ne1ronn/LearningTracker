import os
import httpx
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from telegram_bot.keyboards import create_quiz_answer_buttons
from telegram_bot.middleware import AuthMiddleware

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_GET_URL = f"{API_BASE_URL}/quizzes/{{quiz_id}}"
API_ANSWER_URL = f"{API_BASE_URL}/quizzes/status/{{quiz_id}}"

router = Router()
router.callback_query.middleware(AuthMiddleware())


class AnswerState(StatesGroup):
    answer = State()


@router.callback_query(F.data.startswith("show_answer:"))
async def show_answer(cb: CallbackQuery, state: FSMContext, token: str):
    await state.clear()
    quiz_id = int(cb.data.split(":")[1])
    await state.update_data(quiz_id=quiz_id)

    async with httpx.AsyncClient() as client:
        quiz_response = await client.get(
            API_GET_URL.format(quiz_id=quiz_id),
            headers={"Authorization": f"Bearer {token}"},
        )

    if quiz_response.status_code != 200:
        await cb.message.answer(f"Error:{quiz_response.text}")
        await state.clear()
        return

    answer = quiz_response.json()["answer"]
    await cb.message.answer(
        f"Answer is: {answer}", reply_markup=create_quiz_answer_buttons()
    )
    await state.set_state(AnswerState.answer)

    await cb.answer()


@router.callback_query(AnswerState.answer)
async def answer_handler(cb: CallbackQuery, state: FSMContext, token: str):
    user_answer = cb.data

    if user_answer not in {"know", "do_not_know"}:
        await cb.message.answer(f"Error: wrong state")
        await state.clear()
        return

    data = await state.get_data()
    quiz_id = data["quiz_id"]

    async with httpx.AsyncClient() as client:
        quiz_response = await client.patch(
            API_ANSWER_URL.format(quiz_id=quiz_id),
            json={"result": user_answer},
            headers={"Authorization": f"Bearer {token}"},
        )

    if quiz_response.status_code != 200:
        await cb.message.answer(f"Error:{quiz_response.text}")
        await state.clear()
        return

    await cb.message.answer("Quiz updated")

    await cb.answer()
    await state.clear()
