def create_attendance_report(data, month_name, year):
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
    
    # Получаем уникальные дни из данных
    unique_days = sorted(set(int(row['day']) for row in data))

    for name in attendance_dict:
        attendance_row = f"• {name}: "
        attendance_days = []
        for day in unique_days:
            status = attendance_dict[name].get(day, None)
            if status == 'present':
                attendance_days.append(f"[{day} ✅]")
            elif status == 'absent':
                attendance_days.append(f"[{day} ❌]")
            else:
                attendance_days.append(f"[{day} ❓]")  # Если статус не определен

        attendance_row += ', '.join(attendance_days) + ';'
        message_lines.append(attendance_row)

    # Объединяем все строки в одно сообщение
    message = f"{month_name} {year}:\n" + '\n'.join(message_lines)
    return message