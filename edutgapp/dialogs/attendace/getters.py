from aiogram_dialog import DialogManager 

async def get_data_attendance(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    start_data = dialog_manager.start_data
    # selected_level = (
    #         data.get("selected_level", None) or dialog_manager.start_data["selected_level"]
    #     )
    return {
        "get_years": data.get("get_years"),
        "get_months": data.get("get_months"),
        "selected_year": data.get("selected_year"),

    }

