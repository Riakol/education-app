import FSM

from aiogram_dialog.widgets.kbd import (
    Back, Button, Select, SwitchTo, 
    Group, Multiselect
    )
from aiogram_dialog.widgets.text import Const, Format, Jinja
from aiogram_dialog import (
    Dialog, Window
)
from aiogram_dialog.widgets.input import TextInput
from dialogs.group.getters import get_data_group
from dialogs.group import handlers as action


async def groups():
    back_to_group_menu = SwitchTo(text=Const("⬅️ Cancel"), 
            id="back_to_group_menu", state=FSM.Group.choose_group)
    back_to_inside_group_menu = SwitchTo(text=Const("⬅️ Cancel"), 
            id="back_to_inside_group_menu", state=FSM.Group.inside_group)
    
    dialog = Dialog(
    Window(
        Format("{selected_level}: Menu ⤵️"),
        Group(
            SwitchTo(text=Const("Create a group"), 
            id="cag", state=FSM.Group.create_group),
            Button(Const("Select a group"), id="sag", on_click=action.get_groups_clicked),
            width=1,
        ),
        Button(Const("⬅️ Back"), id="back_to_level_menu", on_click=action.level_menu),       
        state=FSM.Group.choose_group,
    ),
    Window(
        Format("{selected_level}"),
        Group(
            back_to_group_menu,
            Button(Const("Create a group 🔧"), id="create_group", on_click=action.create_group),
            width=2,  
        ),     
        state=FSM.Group.create_group,
    ),
    Window(
        Format("{selected_level}: Select a group ⤵️"),
        Select(
            Format("{item[0]}"),
            id="s_groups",
            item_id_getter=lambda x: x[1].widget_id,
            items="group_buttons",
            on_click=action.group_selected,
        ),
        back_to_group_menu,
        state=FSM.Group.select_group,
    ),
    Window(
        Format("{selected_level}: {group_selected} ⤵️"),
        Group(
            Button(Const("🛠️ Editing"), 
                id="editing", on_click=action.editing_student),
            Button(Const("✅ Add a student"), 
                id="add_student", on_click=
                SwitchTo(text=Const("goto_input_name"), id="switchto_input_name", state=FSM.Group.input_student_name)
                ),
            width=2,
        ),
        Group(
            Button(Const("🗓️ Attendance"), 
                id="view_attendance", on_click=action.show_attendance),
            Button(Const("✏️ mark attendance"), 
                id="viewgroup", on_click=action.show_students),
            width=2,
        ),
        Button(Const("⛔ Delete group"), 
                id="delgroup", on_click=SwitchTo(text=Const("Delete group"), 
                                                 id="goto_delete_group", 
                                                 state=FSM.Group.delete_group)),       
        Back(text=Const("⬅️ Back")),
        state=FSM.Group.inside_group,
    ),
    Window(
        Const("Enter the student's name:"),
        TextInput(id="student_name", 
                on_success=SwitchTo(text=Const("student name"), 
                id="studentname", state=FSM.Group.inside_group, 
                on_click=action.add_student)),
        back_to_inside_group_menu,
        state=FSM.Group.input_student_name,
    ),
    Window(
        Format("{selected_level}: {group_selected}"),
        Format("Are You Sure?"),
        Group(
            Button(Const("Delete ❌"), id="delete_group", on_click=action.delete_group),
            back_to_inside_group_menu,
            width=2,  
        ),     
        state=FSM.Group.delete_group,
    ),
    Window(
        Format("{selected_level}: {group_selected} ⤵️"),
        Group(
            Multiselect(
                Format("✅ {item[0]}"),
                Format("{item[0]}"),
                id="student_check",
                item_id_getter=str,
                items="show_group_students",
            ),
            width=1,
        ),
        Group(
            back_to_inside_group_menu,
            Button(Const("Save 👌🏻"), id="save", on_click=action.check_saved),
            width=2,
        ), 
        state=FSM.Group.student_group_view,
    ),
    getter=get_data_group,
)


    return dialog