import FSM

from aiogram_dialog.widgets.kbd import (
    Back, Button, Select, SwitchTo, 
    Group, Multiselect, Cancel
    )
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, Window
)
from aiogram_dialog.widgets.input import TextInput
from dialogs.student.getters import get_data_student
from dialogs.student import handlers as action


async def student_window():
    back_to_group_menu = Cancel(text=Const("⬅️ Back"))

    dialog = Dialog(
        Window(
            Format("{selected_level}: {group_selected} ⤵️"),
            Group(
                Button(Const("Remove"), 
                    id="remove_student", on_click=SwitchTo(text=Const("remove student"), 
                                                           id="goto_remove_student", 
                                                           state=FSM.Student.remove_student)),
                Button(Const("Rename"), 
                    id="rename_student", on_click=SwitchTo(text=Const("rename student"), 
                                                           id="goto_rename_student", 
                                                           state=FSM.Student.rename_student)),
                
                width=2,
            ),
            back_to_group_menu,
            state=FSM.Student.editing_student_menu
        ),
        Window(
            Format("{selected_level}: {group_selected} ⤵️"),
            Group(
               Select(
                    Format("{item[0]}"),
                    id="st_names",
                    item_id_getter=lambda x: x[1].widget_id,
                    items="student_buttons",
                    on_click=action.remove_selected,
                ),
                width=1, 
            ),
            Back(text=Const("⬅️ Back")),
            state=FSM.Student.remove_student
        ),
        Window(
            Format("{selected_level}: {group_selected} ⤵️"),
            Group(
               Select(
                    Format("{item[0]}"),
                    id="s_names",
                    item_id_getter=lambda x: x[1].widget_id,
                    items="student_buttons",
                    on_click=action.rename_selected,
                ),
                width=1, 
            ),
            SwitchTo(text=Const("⬅️ Cancel"), 
                    id="goto_student_menu", 
                    state=FSM.Student.editing_student_menu),
            state=FSM.Student.rename_student
        ),
        Window(
            Const("Enter the student's new name:"),
            TextInput(id="new_student_name", 
                    on_success=Cancel(on_click=action.update_student_name)),
            Back(text=Const("⬅️ Back")),
            state=FSM.Student.update_student_name,
            ),
        getter=get_data_student,
    )

    return dialog