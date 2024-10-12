from aiogram_dialog import DialogManager 

async def get_data_attendance(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    start_data = dialog_manager.start_data

    has_from_value = data.get("selected_year_from") is not None and data.get("selected_month_from") is not None
    has_to_value = data.get("selected_year_to") is not None and data.get("selected_month_to") is not None

    extended = has_from_value and has_to_value

    return {
        "extended": extended,

        "get_years": data.get("get_years"),
        "get_months": data.get("get_months"),
        "selected_year": data.get("selected_year"),

        "selected_year_from": data.get("selected_year_from"),
        "selected_month_from": data.get("selected_month_from"),

        "selected_year_to": data.get("selected_year_to"),
        "selected_month_to": data.get("selected_month_to"),

        "days_from": data.get("days_from"),
        "days_to": data.get("days_to"),

        "selected_day_from": data.get("selected_day_from"),
        "selected_day_to": data.get("selected_day_to"),

        "year_start": data.get("year_start"),
        "year_end": data.get("year_end"),
    }

