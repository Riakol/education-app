import action
import FSM

from aiogram import Router
from aiogram_dialog.widgets.kbd import (
    Back, Button, Select, SwitchTo, 
    Group, Multiselect, Start
    )
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import (
    Dialog, Window, DialogManager
)
from aiogram_dialog.widgets.input import TextInput



async def my_window():
    back_to_group_menu = SwitchTo(text=Const("⬅️ Cancel"), 
            id="back_to_group_menu", state=FSM.StudentWorkflow.choose_group)
    back_to_inside_group_menu = SwitchTo(text=Const("⬅️ Cancel"), 
            id="back_to_inside_group_menu", state=FSM.StudentWorkflow.inside_group)
 
    show_levels = await action.create_level_buttons()
    # show_years = await action.get_attendance_year()
    # show_months = await action.get_attendance_month()

    dialog = Dialog(
    Window(
        Format("Hello, {name} 💕"),
        Group(*show_levels, width=2),
        state=FSM.StudentWorkflow.choose_level,
    ),
    Window(
        Format("{selected_level}: Menu ⤵️"),
        Group(
            Button(Const("Create a group"), id="cag", on_click=action.create_group_clicked),
            Button(Const("Select a group"), id="sag", on_click=action.get_groups_clicked),
            width=1,
        ),       
        Back(text=Const("Back")),
        state=FSM.StudentWorkflow.choose_group,
    ),
    Window(
        Format("{selected_level}"),
        Group(
            back_to_group_menu,
            Button(Const("Create a group 🔧"), id="create_group", on_click=action.create_group),
            width=2,  
        ),     
        state=FSM.StudentWorkflow.create_group,
    ),
    Window(
        Format("{selected_level}: Select a group ⤵️"),
        Select(
            Format("{item.widget_id}"),
            id="s_groups",
            item_id_getter=lambda x: x.widget_id,
            items="group_buttons",
            on_click=action.group_selected,
        ),
        back_to_group_menu,
        state=FSM.StudentWorkflow.select_group,
    ),
    Window(
        Format("{selected_level}: {group_selected} ⤵️"),
        Group(
            Button(Const("❌ Remove a student"), 
                id="remove_student", on_click=action.remove_student_from_group),
            Button(Const("✅ Add a student"), 
                id="add_student", on_click=action.add_student_to_group),
            width=2,
        ),
        Group(
            Button(Const("🗓️ Attendance"), 
                id="view_attendance", on_click=action.attendance),
            # Button(Const("🗓️ Attendance"), 
            #     id="view_attendance", on_click=action.attendance_year_month_selecting),
            Button(Const("✏️ Mark those present"), 
                id="viewgroup", on_click=action.show_students),
            width=2,
        ),
        Button(Const("⛔ Delete group"), 
                id="delgroup", on_click=action.delete_group_clicked),       
        Back(text=Const("Back")),
        state=FSM.StudentWorkflow.inside_group,
    ),
    # Window(
    #     Format("{selected_level}: {group_selected}"),
    #     Format("Are You Sure?"),
    #     Group(
    #         Button(Const("remove student ❌"), id="remove_student", on_click=action.delete_group),
    #         back_to_inside_group_menu,
    #         width=2,  
    #     ),
    #     back_to_inside_group_menu,     
    #     state=FSM.StudentWorkflow.remove_student,
    # ),
    Window(
        Format("{selected_level}: {group_selected}"),
        Format("Are You Sure?"),
        Group(
            Button(Const("Delete ❌"), id="delete_group", on_click=action.delete_group),
            back_to_inside_group_menu,
            width=2,  
        ),     
        state=FSM.StudentWorkflow.delete_group,
    ),
    Window(
        Const("Enter the student's name:"),
        TextInput(id="student_name", 
                on_success=SwitchTo(text=Const("stud name"), 
                id="stud_name_test", state=FSM.StudentWorkflow.inside_group, 
                on_click=action.add_student)),
        back_to_inside_group_menu,
        state=FSM.StudentWorkflow.student_name,
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
            back_to_inside_group_menu,
            Button(Const("Save 👌🏻"), id="save", on_click=action.check_saved),
            width=2,
        ), 
        state=FSM.StudentWorkflow.student_group_view,
    ),
    Window(
        Format("Select an option ⤵️"),
        Group(
            # Button(Const("By message"), id="attendance_msg", on_click=action.get_attendance_msg), 
            Button(Const("Excel"), id="attendance_excel", on_click=action.attendance_year_month_selecting), 
            width=2,
        ),
        back_to_inside_group_menu,
        state=FSM.StudentWorkflow.attendance,
    ),
    Window(
        Format("Choose a year ⤵️"),
        Select(
            Format("{item.widget_id}"),
            id="year",
            item_id_getter=lambda x: x.widget_id,
            items="get_years",
            on_click=action.year_button_clicked,
        ),
        back_to_inside_group_menu,
        state=FSM.StudentWorkflow.attendance_year,
    ),
    Window(
        Format("Choose a month of {selected_year} year ⤵️"),
        Select(
            Format("{item.widget_id}"),
            id="month",
            item_id_getter=lambda x: x.widget_id,
            items="get_months",
            on_click=action.month_button_clicked,
        ),
        SwitchTo(text=Const("⬅️ Back"), 
                    id="back_to_attendance_year", state=FSM.StudentWorkflow.attendance_year),
        state=FSM.StudentWorkflow.attendance_month,
    ),
    getter=action.dialog_get_data,
)


    return dialog





# async def level_window():

#     show_levels = await action.create_level_buttons()

#     dialog = Dialog(
#     Window(
#         Format("Hello, {name} 💕"),
#         Group(*show_levels, width=2),
#         Start(Const("Start 1"), id="start", state=FSM.StudentWorkflow.choose_group),
#         state=FSM.Level.choose_level,
#     ),
#     getter=action.dialog_get_data,
#     )

#     return dialog
