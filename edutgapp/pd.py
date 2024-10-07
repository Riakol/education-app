import pandas as pd


async def create_attendance_table(group_details_id, month, year):
    # Получаем данные о посещаемости
    attendance_records = await attendance_data(group_details_id, month, year)
    
    # Преобразуем записи в DataFrame
    df = pd.DataFrame(attendance_records)
    
    # Получаем информацию о группе и уровне языка
    group_info = await get_student_group_info(group_details_id)
    
    if group_info:
        group_number = group_info['group_number']
        eng_lvl = group_info['eng_lvl']
        
        # Заменяем статус на символы
        df['status'] = df['status'].replace({
            'present': '✔️',  # Знак галочки для присутствия
            'absent': '❌'     # Знак крестика для отсутствия
        })
        
        # Создаем сводную таблицу
        pivot_table = df.pivot_table(index='student_name', 
                                      columns='day', 
                                      values='status', 
                                      fill_value='')  # Заполняем пустые значения
        
        # Добавляем месяц в заголовок
        pivot_table.columns = [f"{month}_{day}" for day in pivot_table.columns]
        
        # Сохраняем в Excel
        file_name = f"{eng_lvl}_{group_number}_{month}_{year}.xlsx"
        pivot_table.to_excel(file_name, sheet_name=f"{eng_lvl} {group_number}")
        
        print(f"Файл сохранен: {file_name}")
    else:
        print("Информация о группе не найдена.")

# Пример вызова функции
# await create_attendance_table(group_details_id=1, month=10, year=2023)
