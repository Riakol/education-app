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
            Button(Const("Create a group 🔧"), id="create_group", on_click=SwitchTo(text=Const("input group name"), 
            id="inp_group_name", state=FSM.Group.create_group_name)),
            width=2,  
        ),     
        state=FSM.Group.create_group,
    ),
    Window(
        Format("{selected_level}\nCome up with a name for the group"),
        TextInput(id="input_group_name", 
                on_success=action.create_group), 
        state=FSM.Group.create_group_name,
    ),
    Window(
        Format("{selected_level}: Select a group ⤵️"),
        Group(
            Select(
            Format("{item[0]}"),
            id="s_groups",
            item_id_getter=lambda x: x[1].widget_id,
            items="group_buttons",
            on_click=action.group_selected,
            ),
            width=1,
        ),
        back_to_group_menu,
        state=FSM.Group.select_group,
    ),
    Window(
        Format("{selected_level}: {group_selected_name} ⤵️"),
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
            Button(Const("🗓️ View Attendance"), 
                id="view_attendance", on_click=action.show_attendance),
            Button(Const("✏️ mark Attendance"), 
                id="viewgroupmenu", on_click=SwitchTo(text=Const("attendance menu"), 
                                                 id="goto_attendance_menu", 
                                                 state=FSM.Group.mark_group_attendance)),
            width=2,
        ),
        Group(
            Button(Const("⛔ Delete group"), 
                id="delgroup", on_click=SwitchTo(text=Const("Delete group"), 
                                                 id="goto_delete_group", 
                                                 state=FSM.Group.delete_group)),
            Button(Const("🔧 Rename group"), 
                id="rename_group", on_click=SwitchTo(text=Const("Rename group"), 
                                                 id="goto_rename_group", 
                                                 state=FSM.Group.rename_group)),
            width=2,
        ),    
        Back(text=Const("⬅️ Back")),
        state=FSM.Group.inside_group,
    ),
    Window(
        Format("From the beginning, it is worth noting those\nwho are present / absent and only then\nchoose for a good reason"),
        Group(
            Button(Const("❓ good reason"), 
                id="select_absence_student", on_click=action.absence_student_btns),
            Button(Const("✍🏻 mark"), 
                id="viewgroup", on_click=action.show_students),
            width=2,
        ),
        back_to_inside_group_menu,
        state=FSM.Group.mark_group_attendance,
    ),
    Window(
        Format("select student absence"),
        Group(
            Select(
                Format("{item[0]}"),
                id="absence_student",
                item_id_getter=lambda x: x[1].widget_id,
                items="student_buttons",
                on_click=action.student_absence_selected,
            ),
            width=1, 
        ),
        back_to_inside_group_menu,
        state=FSM.Group.absence_student_selected,
    ),
    Window(
        Const("Enter the reason for the absence:"),
        TextInput(id="absence_reason", 
                on_success=SwitchTo(text=Const("check students"), 
                id="check_students", state=FSM.Group.mark_group_attendance, 
                on_click=action.absence_reason)),
        back_to_inside_group_menu,
        state=FSM.Group.input_absence_reason,
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
        Format("Enter a new name for the group:"),
        TextInput(id="new_group_name", 
            on_success=action.rename_group),
        back_to_inside_group_menu,
        state=FSM.Group.rename_group,
    ),
    Window(
        Format("{selected_level}: {group_selected_name}"),
        Format("Are You Sure?"),
        Group(
            Button(Const("Delete ❌"), id="delete_group", on_click=action.delete_group),
            back_to_inside_group_menu,
            width=2,  
        ),     
        state=FSM.Group.delete_group,
    ),
    Window(
        Format("{selected_level}: {group_selected_name} ⤵️"),
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
            Button(Const("👌🏻 Save"), id="save", on_click=action.check_saved),
            width=2,
        ),
        state=FSM.Group.student_group_view,
    ),
    getter=get_data_group,
)


    return dialog