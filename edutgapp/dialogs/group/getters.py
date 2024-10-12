from aiogram_dialog import DialogManager 

async def get_data_group(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    start_data = dialog_manager.start_data

    return {
        "selected_level": start_data["selected_level"],
        "group_buttons": data.get("group_buttons", []),
        "group_selected": data.get("group_selected"),
        "show_group_students": data.get("show_group_students"), 
    }