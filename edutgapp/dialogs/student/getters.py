from aiogram_dialog import DialogManager 

async def get_data_student(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    start_data = dialog_manager.start_data

    return {
        "selected_level": start_data["selected_level"],
        "group_selected": start_data["group_selected"],
        "student_buttons": start_data["student_buttons"],
        "rename_student_id_selected": data.get("rename_student_id_selected"),
    }