import pandas as pd
# from openpyxl.utils import get_column_letter
from datetime import datetime

async def create_attendance_excel(data, eng_level, group_number):
    attendance_dict = {}
    total_attendance = {}

    for row in data:
        name = row['student_name']
        day = int(row['day'])
        status = row['status']
        absence_reason = row.get('absence_reason', '') 
        date = pd.to_datetime(row['date'])  

        month_year = date.to_period('M')  

        if month_year not in attendance_dict:
            attendance_dict[month_year] = {}

        if name not in attendance_dict[month_year]:
            attendance_dict[month_year][name] = {}

        attendance_dict[month_year][name][day] = status

        if name not in total_attendance:
            total_attendance[name] = {'Present': 0, 'Absent': 0, 'Absence Reason': 0}

        if status == 'present':
            total_attendance[name]['Present'] += 1
        elif status == 'absent':
            total_attendance[name]['Absent'] += 1
            if absence_reason: 
                total_attendance[name]['Absence Reason'] += 1

    # today = datetime.now()
    today = datetime.now().strftime("%d.%m.%y")
    file_name = f"{eng_level}_{group_number}_attendance_{today}.xlsx"

    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        
        for month_year in sorted(attendance_dict.keys()):
            unique_days = sorted({day for days in attendance_dict[month_year].values() for day in days.keys()})

            attendance_rows = []

            for name, days in attendance_dict[month_year].items():
                attendance_row = {'Name': name}
                for day in unique_days:
                    status = days.get(day, '')
                    if status == 'present':
                        attendance_row[day] = '✅'  
                    elif status == 'absent':
                        attendance_row[day] = '❌' 
                    else:
                        attendance_row[day] = ''  # Пустое значение для отсутствующих дней
                
                attendance_rows.append(attendance_row)

            attendance_df = pd.DataFrame(attendance_rows)
            
            sheet_name = month_year.strftime('%B %Y')
      
            header_df = pd.DataFrame([[f"{eng_level}: {group_number}"]])
            header_df.to_excel(writer, index=False, header=False, sheet_name=sheet_name)
            attendance_df.to_excel(writer, index=False, sheet_name=sheet_name, startrow=2)

            
            worksheet = writer.sheets[sheet_name]
            column_widths = {
                'A': 20,  
            }

            for column, width in column_widths.items():
                worksheet.column_dimensions[column].width = width

        total_rows = []
        for name, counts in total_attendance.items():
            total_row = {
                'Name': name,
                'Present': counts['Present'],
                'Absent': counts['Absent'],
                'Absence Reason': counts['Absence Reason']
            }
            total_rows.append(total_row)

        total_df = pd.DataFrame(total_rows)

        total_header_df = pd.DataFrame([[f"{eng_level}: {group_number}"]])
        total_header_df.to_excel(writer, index=False, header=False, sheet_name='Total')
        total_df.to_excel(writer, index=False, sheet_name='Total', startrow=2)


        worksheet = writer.sheets['Total']
        column_widths = {
            'A': 20,  
            'B': 15,  
            'C': 15,  
            'D': 20 
        }

        for column, width in column_widths.items():
            worksheet.column_dimensions[column].width = width

    return file_name
