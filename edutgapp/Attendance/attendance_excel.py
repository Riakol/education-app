import pandas as pd
from database import requests


async def create_attendance_excel(data, month_name, year, eng_level, group_number):
    # Создаем словарь для хранения посещаемости
    attendance_dict = {}
    
    for row in data:
        name = row['student_name']
        day = int(row['day'])
        status = row['status']
        
        if name not in attendance_dict:
            attendance_dict[name] = {}
        
        attendance_dict[name][day] = status

    # Получаем уникальные дни из данных
    unique_days = sorted({day for days in attendance_dict.values() for day in days.keys()})

    # Создаем список для хранения строк DataFrame
    attendance_rows = []

    for name, days in attendance_dict.items():
        attendance_row = {'Name': name}
        for day in unique_days:
            status = days.get(day, '')
            if status == 'present':
                attendance_row[day] = '✅'  # Знак галочки для присутствия
            elif status == 'absent':
                attendance_row[day] = '❌'  # Знак крестика для отсутствия
            else:
                attendance_row[day] = ''    # Пустое значение для отсутствующих дней
        
        attendance_rows.append(attendance_row)

    # Создаем DataFrame из списка строк
    attendance_df = pd.DataFrame(attendance_rows)

    # Создаем DataFrame для заголовка уровня и группы
    header_df = pd.DataFrame([[f"{eng_level}: {group_number}"]])

    # Сохраняем DataFrame в Excel
    file_name = f"attendance_{month_name}_{year}.xlsx"
    
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        # Записываем заголовок уровня и группы в первую строку
        header_df.to_excel(writer, index=False, header=False, sheet_name=f"{requests.months_dict[month_name]} {year}")
        
        # Записываем основной DataFrame, начиная со второй строки
        attendance_df.to_excel(writer, index=False, sheet_name=f"{requests.months_dict[month_name]} {year}", startrow=2)


    return file_name