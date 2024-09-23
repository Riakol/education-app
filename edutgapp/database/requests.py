from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Button, Back, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)
from database import engine

levels = {
        "elementary": "Elementary",
        "preintermediate": "Pre-Intermediate",
        "intermediate": "Intermediate",
        "upperintermediate": "Upper-Intermediate",
        "advanced": "Advanced",
        "ielts": "IELTS",
    }

async def find_or_create_group(conn, selected_level):
    
    async with conn.transaction():
        level_id = await conn.fetchval("""
            SELECT id FROM level WHERE eng_lvl = $1
        """, levels[selected_level])

        # Получаем максимальный номер группы для выбранного уровня
        max_group_number = await conn.fetchval("""
            SELECT COALESCE(MAX(group_id), 0)
            FROM student_group
            WHERE eng_lvl_id = $1
        """, level_id)

        # Если группы с таким уровнем нет, то создаем первую группу
        if max_group_number == 0:
            new_group_number = 1  # Первая группа
            await conn.execute("""
                INSERT INTO student_group (group_id, eng_lvl_id)
                VALUES ($1, $2)
            """, new_group_number, level_id)
        else:
            # Если группа уже есть, добавляем новую группу с увеличенным номером
            new_group_number = max_group_number + 1
            await conn.execute("""
                INSERT INTO student_group (group_id, eng_lvl_id)
                VALUES ($1, $2)
            """, new_group_number, level_id)

        return new_group_number  # Возвращаем номер созданной группы
    

async def get_groups_for_level(selected_level):
    """ Получаем список групп для заданного уровня """

    conn = await engine.connect_to_db()

    level_id = await conn.fetchval("""
        SELECT id FROM level WHERE eng_lvl = $1
    """, levels[selected_level])

    groups = await conn.fetch("""
        SELECT group_id FROM student_group WHERE eng_lvl_id = $1
    """, level_id)
    
    return [record['group_id'] for record in groups]


