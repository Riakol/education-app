import pandas as pd
from datetime import datetime



def create_attendance_excel(data, month_name, year):
    # Создаем словарь для хранения посещаемости
    attendance_dict = {}
    
    for row in data:
        name = row['student_name']
        day = int(row['day'])
        status = row['status']
        
        if name not in attendance_dict:
            attendance_dict[name] = {}
        
        attendance_dict[name][day] = status

    # Формируем сообщение
    message_lines = []
    days = list(range(1, 32))

    for name in attendance_dict:
        attendance_row = f"• {name}: "
        attendance_days = []
        for day in days:
            status = attendance_dict[name].get(day, '')
            if status == 'present':
                attendance_days.append(f"[{day} ✅]")
            elif status == 'absent':
                attendance_days.append(f"[{day} ❌]")
        
        attendance_row += ', '.join(attendance_days) + ';'
        message_lines.append(attendance_row)

    # Объединяем все строки в одно сообщение
    message = f"{month_name} {year}:\n" + '\n'.join(message_lines)
    return message
