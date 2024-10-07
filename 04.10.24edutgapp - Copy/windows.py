import buttons
import operator
from database import requests
from FiniteStateMachine import StudentLevelGroup
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import (
    Back, Button, Select, SwitchTo, 
    Group, Next, Checkbox, ListGroup, Multiselect
    )
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window
)
from aiogram_dialog.widgets.input import TextInput



async def my_window():
    back_to_group_menu = SwitchTo(text=Const("⬅️ Cancel"), 
            id="back_to_group_menu", state=StudentLevelGroup.choose_group)
    back_to_inside_group_menu = SwitchTo(text=Const("⬅️ Cancel"), 
            id="back_to_inside_group_menu", state=StudentLevelGroup.inside_group)
 
    show_levels = await buttons.create_level_buttons()

    dialog = Dialog(
    # Window(
    #     Format("Main Menu ⤵️"),
    #     SwitchTo(text=Const("Choose a level"), 
    #             id="back_to_chooselvl", state=StudentLevelGroup.choose_level),
    #     state=StudentLevelGroup.main_menu,
    # ),
    Window(
        Format("Hello, {name} 💕"),
        Group(*show_levels, width=2),
        state=StudentLevelGroup.choose_level,
    ),
    Window(
        Format("{selected_level}: Menu ⤵️"),
        Group(
            Button(Const("Create a group"), id="cag", on_click=buttons.create_group_clicked),
            Button(Const("Select a group"), id="sag", on_click=buttons.get_groups_clicked),
            width=1,
        ),       
        Back(text=Const("Back")),
        state=StudentLevelGroup.choose_group,
    ),
    Window(
        Format("{selected_level}"),
        Group(
            back_to_group_menu,
            Button(Const("Create a group 🔧"), id="create_group", on_click=buttons.create_group),
            width=2,  
        ),     
        state=StudentLevelGroup.create_group,
    ),
    Window(
        Format("{selected_level}: Select a group ⤵️"),
        Select(
            Format("{item.widget_id}"),
            id="s_groups",
            item_id_getter=lambda x: x.widget_id,
            items="group_buttons",
            on_click=buttons.group_selected,
        ),
        back_to_group_menu,
        state=StudentLevelGroup.select_group,
    ),
    Window(
        Format("{selected_level}: {group_selected} ⤵️"),
        Group(
            Button(Const("❌ Remove a student"), 
                id="remove_student", on_click=buttons.remove_student_from_group),
            Button(Const("✅ Add a student"), 
                id="add_student", on_click=buttons.add_student_to_group),
            width=2,
        ),
        Group(
            Button(Const("🗓️ Attendance"), 
                id="view_attendance", on_click=buttons.show_attendance),
            Button(Const("✏️ Mark those present"), 
                id="viewgroup", on_click=buttons.show_students),
            width=2,
        ),
        Button(Const("⛔ Delete group"), 
                id="delgroup", on_click=buttons.delete_group_clicked),       
        Back(text=Const("Back")),
        state=StudentLevelGroup.inside_group,
    ),
    Window(
        Format("{selected_level}: {group_selected}"),
        Format("Are You Sure?"),
        Group(
            Button(Const("Delete ❌"), id="delete_group", on_click=buttons.delete_group),
            back_to_inside_group_menu,
            width=2,  
        ),     
        state=StudentLevelGroup.delete_group,
    ),
    Window(
        Const("Enter the student's name:"),
        TextInput(id="student_name", 
                on_success=SwitchTo(text=Const("stud name"), 
                id="stud_name_test", state=StudentLevelGroup.inside_group, 
                on_click=buttons.add_student)),
        Back(text=Const("⬅️ Cancel")),
        state=StudentLevelGroup.student_name,
    ),
    Window(
        Format("{selected_level}: {group_selected} ⤵️"),
        Group(
            Multiselect(
                Format("✅ {item}"),
                Format("{item}"),
                id="student_check",
                item_id_getter=str,
                items="students_view",
            ),
            width=3,
        ),
        Group(
            SwitchTo(text=Const("⬅️ Cancel"), 
                    id="back_to_inside_group", state=StudentLevelGroup.inside_group),
            Button(Const("Save 👌🏻"), id="save", on_click=buttons.check_saved),
            width=2,
        ), 
        state=StudentLevelGroup.student_group_view,
    ),
    getter=buttons.dialog_get_data,
)


    return dialog