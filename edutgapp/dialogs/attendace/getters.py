from aiogram_dialog import DialogManager 

async def get_data_attendance(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    start_data = dialog_manager.start_data


    return {
        "get_start_years": data.get("get_start_years"),
        "get_end_years": data.get("get_end_years"),

        "get_starting_days": data.get("get_starting_days"),
        "get_end_days": data.get("get_end_days"),
        
        "get_start_months": data.get("get_start_months"),
        "get_end_months": data.get("get_end_months"),
        
        "starting_year": data.get("starting_year"),
        "starting_month": data.get("starting_month"),
        "starting_day": data.get("starting_day"),
        
        "end_year": data.get("end_year"),
        "end_month": data.get("end_month"),
        "end_day": data.get("end_day"),
    }

