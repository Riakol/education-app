from aiogram_dialog import DialogManager 

async def get_data_group(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    start_data = dialog_manager.start_data

    return {
        "selected_level": start_data["selected_level"],
        "group_buttons": data.get("group_buttons", []),
        "group_selected_id": data.get("group_selected_id"),
        "group_selected_name": data.get("group_selected_name"),
        "show_group_students": data.get("show_group_students"),
        "absence_reason": data.get("other_check_saved"), 
        "student_buttons": data.get("student_buttons"),
        "studentid_absence_selected": data.get("studentid_absence_selected"),
    }