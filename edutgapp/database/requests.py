import logging
from database import engine

levels = {
        "elementary": "Elementary",
        "preintermediate": "Pre-Intermediate",
        "intermediate": "Intermediate",
        "upperintermediate": "Upper-Intermediate",
        "advanced": "Advanced",
        "ielts": "IELTS",
    }

months_dict = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

async def get_num_by_month(dct, value):
    return next((k for k, v in dct.items() if v == value), None)


async def access_start():
    conn = await engine.connect_to_db()
    access = await conn.fetch(
        """
        SELECT tg_id FROM teacher
        """)
    
    return [tg['tg_id'] for tg in access]

async def find_or_create_group(conn, selected_level):
    #OLD VERSION
     async with conn.transaction():
        level_id = await conn.fetchval("""
            SELECT id FROM level WHERE eng_lvl = $1
        """, selected_level)

        existing_groups = await conn.fetch("""
            SELECT group_id
            FROM group_details
            WHERE eng_lvl_id = $1
            ORDER BY group_id
        """, level_id)

        existing_group_numbers = [row['group_id'] for row in existing_groups]

        new_group_number = 1 
        for group_number in existing_group_numbers:
            if group_number == new_group_number:
                new_group_number += 1  
            else:
                break  

        await conn.execute("""
            INSERT INTO group_details (group_id, eng_lvl_id)
            VALUES ($1, $2)
        """, new_group_number, level_id)

        return new_group_number
     
async def create_group(selected_level, group_name):
    conn = await engine.connect_to_db()
    async with conn.transaction():
        level_id = await conn.fetchval("""
            SELECT id FROM level WHERE eng_lvl = $1
        """, selected_level)

        result = await conn.fetchrow("SELECT id FROM \"group\" WHERE group_name = $1;", group_name)
        if result:
            group_id = result['id']
            
            existing_group = await conn.fetchrow("""
                SELECT id FROM group_details 
                WHERE group_id = $1 AND eng_lvl_id = $2 AND status = 'active'
            """, group_id, level_id)

            if existing_group:
                return f"❗ A group named '{group_name}' already exists for the '{selected_level}' level. Please come up with another name."
        else:
            result = await conn.fetchrow("INSERT INTO \"group\" (group_name) VALUES ($1) RETURNING id;", group_name)
            group_id = result['id']

        await conn.execute("""
            INSERT INTO group_details (group_id, eng_lvl_id)
            VALUES ($1, $2)
        """, group_id, level_id)

        return f"✅ The group '{group_name}' has been successfully created for the level '{selected_level}'." 
    

async def rename_group(selected_level, group_name, group_details_id):
    conn = await engine.connect_to_db()
    async with conn.transaction():
        level_id = await conn.fetchval("""
            SELECT id FROM level WHERE eng_lvl = $1
        """, selected_level)

        result = await conn.fetchrow("SELECT id FROM \"group\" WHERE group_name = $1;", group_name)
        if result:
            group_id = result['id']
            
            existing_group = await conn.fetchrow("""
                SELECT id FROM group_details 
                WHERE group_id = $1 AND eng_lvl_id = $2 AND status = 'active'
            """, group_id, level_id)

            if existing_group:
                return f"❗ A group named '{group_name}' already exists for the '{selected_level}' level. Please come up with another name."
        else:
            result = await conn.fetchrow("INSERT INTO \"group\" (group_name) VALUES ($1) RETURNING id;", group_name)
            group_id = result['id']

        await conn.execute("""
            UPDATE group_details 
                SET group_id = $1 
                WHERE id = $2
        """, group_id, group_details_id)

        return f"✅ The group has been successfully renamed to '{group_name}'." 
        

async def get_groups_for_level(selected_level):
    """ Получаем список групп для заданного уровня """

    conn = await engine.connect_to_db()
    groups = await conn.fetch("""
        SELECT g.id, g.group_name 
        FROM group_details gd
        JOIN "group" g ON gd.group_id = g.id
        WHERE gd.eng_lvl_id = $1 AND gd.status = 'active'
    """, selected_level)

    if groups:
        sorted_groups = sorted(groups, key=lambda x: x['group_name'])
        return sorted_groups


async def get_lvl_id(selected_level):
    conn = await engine.connect_to_db()
    level_id = await conn.fetchval("""
        SELECT id FROM level WHERE eng_lvl = $1
    """, selected_level)

    return level_id


async def get_group_number(group_id):
    conn = await engine.connect_to_db()
    group_name_not_id = await conn.fetchval("""
        SELECT group_name FROM "group" WHERE id = $1
    """, group_id)

    return group_name_not_id

async def add_student(student_name):
    conn = await engine.connect_to_db()
    result = await conn.fetchrow("""
        INSERT INTO student (name) VALUES ($1) RETURNING id;
    """, student_name)
    return result['id']
    
async def get_student_id(student_name):
    try:
        conn = await engine.connect_to_db()
        return await conn.fetchval("""
            SELECT id FROM student WHERE name = $1""", 
            student_name)
    except Exception as e:
        print(f"Error fetching student ID: {e}")

async def get_student_id_from_group(group_details_id):
    try:
        conn = await engine.connect_to_db()
        return await conn.fetchval('''
        SELECT sd.student_id
        FROM student_details sd
        JOIN group_details gd ON sd.group_details_id = gd.id
        WHERE gd.id = $1
    ''', group_details_id)
    except Exception as e:
        print(f"Error fetching student ID: {e}")

    
async def get_group_details_id(eng_lvl_id, group_id):
    conn = await engine.connect_to_db()
    group_details_id = await conn.fetchval("""
        SELECT id FROM group_details WHERE eng_lvl_id = $1 AND group_id = $2 AND status = 'active'
    """, eng_lvl_id, group_id)

    return group_details_id

async def add_student_to_group(student_id, group_details_id):
    conn = await engine.connect_to_db()
    await conn.execute("""
            INSERT INTO student_details (student_id, group_details_id) 
            VALUES ($1, $2)
        """, student_id, group_details_id)


async def get_students_from_group(group_details_id):
    conn = await engine.connect_to_db()
    get_students = await conn.fetch("""
            SELECT s.name, s.id 
            FROM student s
            JOIN student_details sd ON s.id = sd.student_id
            WHERE sd.group_details_id = $1 AND sd.status = 'active';
        """, group_details_id)
        
    return [(record['name'], record['id']) for record in get_students]

async def get_student_details_id(student_id, group_details_id):
    conn = await engine.connect_to_db()
    student_details_id = await conn.fetchval("""
        SELECT id FROM student_details WHERE student_id = $1 AND group_details_id = $2
    """, student_id, group_details_id)

    return student_details_id


async def add_student_attendance(student_details_id, date, status="absent"):
    conn = await engine.connect_to_db()
    await conn.execute("""
            INSERT INTO attendance (student_details_id, date, status) 
            VALUES ($1, $2, $3)
            ON CONFLICT (student_details_id, date) 
            DO UPDATE SET 
                status = EXCLUDED.status,
                absence_reason = CASE 
                    WHEN EXCLUDED.status IN ('absent', 'present') THEN NULL
                    WHEN EXCLUDED.status = 'other' THEN NULL
                    ELSE attendance.absence_reason  -- Указываем, что это поле из таблицы attendance
                END
        """, student_details_id, date, status)

async def add_student_absence_reason(student_details_id, date, absence_reason=None):
    conn = await engine.connect_to_db()
    
    # Проверяем, существует ли запись с текущей датой
    existing_record = await conn.fetchrow("""
        SELECT status, absence_reason FROM attendance 
        WHERE student_details_id = $1 AND date = $2
    """, student_details_id, date)

    if existing_record:
        # Если статус уже установлен, очищаем его
        if existing_record['status'] is not None:
            await conn.execute("""
                UPDATE attendance 
                SET status = 'other'  -- Устанавливаем значение по умолчанию
                WHERE student_details_id = $1 AND date = $2
            """, student_details_id, date)

        # Обновляем absence_reason
        await conn.execute("""
            UPDATE attendance 
            SET absence_reason = $1 
            WHERE student_details_id = $2 AND date = $3
        """, absence_reason, student_details_id, date)
    else:
        # Если записи нет, вставляем новую с absence_reason
        await conn.execute("""
            INSERT INTO attendance (student_details_id, date, status, absence_reason) 
            VALUES ($1, $2, 'other', $3)  -- Устанавливаем значение по умолчанию
        """, student_details_id, date, absence_reason)


async def attendance_data(group_details_id, month, year):
    conn = await engine.connect_to_db()
    res = await conn.fetch("""
    SELECT s.name AS student_name, 
           EXTRACT(DAY FROM a.date) AS day, 
           a.status 
    FROM attendance a
    JOIN student_details sd ON a.student_details_id = sd.id
    JOIN student s ON sd.student_id = s.id
    JOIN group_details gd ON sd.group_details_id = gd.id
    WHERE sd.group_details_id = $1
      AND EXTRACT(MONTH FROM a.date) = $2
      AND EXTRACT(YEAR FROM a.date) = $3
    ORDER BY s.name, a.date;
    """, group_details_id, month, year)

    return res

# CUSTOM RANGE
# start_date = '2024-09-20'
# end_date = '2024-10-22'
 
async def attendance_custom(group_details_id, start_date, end_date):
    conn = await engine.connect_to_db()
    res = await conn.fetch("""
    SELECT s.name AS student_name,
            sd.student_id, 
           a.date,  -- Добавлено поле date
           EXTRACT(DAY FROM a.date) AS day, 
           a.status,
           a.absence_reason 
    FROM attendance a
    JOIN student_details sd ON a.student_details_id = sd.id
    JOIN student s ON sd.student_id = s.id
    JOIN group_details gd ON sd.group_details_id = gd.id
    WHERE sd.group_details_id = $1
      AND a.date BETWEEN $2 AND $3
    ORDER BY s.name, a.date;
    """, group_details_id, start_date, end_date)

    return res


async def attendance_alltime_data(group_details_id):
    conn = await engine.connect_to_db()
    res = await conn.fetch("""
    SELECT s.name AS student_name,
            sd.student_id, 
           EXTRACT(DAY FROM a.date) AS day, 
           a.status, 
           a.date,
           a.absence_reason
    FROM attendance a
    JOIN student_details sd ON a.student_details_id = sd.id
    JOIN student s ON sd.student_id = s.id
    JOIN group_details gd ON sd.group_details_id = gd.id
    WHERE sd.group_details_id = $1
    ORDER BY s.name, a.date;
    """, group_details_id)

    return res


async def get_month_year_from_attendace(group_details_id) -> dict:
    conn = await engine.connect_to_db()

    date = await conn.fetch("""
    SELECT DISTINCT EXTRACT(MONTH FROM a.date) AS month, EXTRACT(YEAR FROM a.date) AS year
    FROM attendance a
    JOIN student_details sd ON a.student_details_id = sd.id
    WHERE sd.group_details_id = $1
    ORDER BY year, month;
    """, group_details_id)

    month_year_dict = {
        'month': [],
        'year': []
    }

    for row in date:
        month_year_dict['month'].append(int(row['month']))
        month_year_dict['year'].append(int(row['year']))

    return month_year_dict


async def get_months_by_year(group_details_id, selected_year) -> dict:
    conn = await engine.connect_to_db()

    months = await conn.fetch("""
    SELECT DISTINCT EXTRACT(MONTH FROM a.date) AS month
    FROM attendance a
    JOIN student_details sd ON a.student_details_id = sd.id
    WHERE sd.group_details_id = $1 AND EXTRACT(YEAR FROM a.date) = $2
    ORDER BY month;
    """, group_details_id, selected_year)

    return [int(row['month']) for row in months]

async def update_student_name(new_name, student_id):
    conn = await engine.connect_to_db()
    await conn.execute("""
            UPDATE student
            SET name = $1
            WHERE id = $2;
        """, new_name, student_id)
 
async def remove_student(student_id):
    conn = await engine.connect_to_db()
    await conn.execute("""
        UPDATE student_details
        SET status = 'inactive'
        WHERE student_id = $1;
    """, student_id)
    
    '''
    await conn.execute("""
            DELETE FROM student_details
            WHERE student_id = $1;
        """, student_id)

    await conn.execute("""
            DELETE FROM student
            WHERE id = $1;
        """, student_id)
    '''
    

async def get_transfer_info(student_ids):
    # SQL-запрос для получения данных о переводе студентов, включая уровень и группу
    conn = await engine.connect_to_db()
    transfer_data = await conn.fetch("""
    SELECT s.id AS student_id, l.eng_lvl, g.group_name, sah.date, sah.status, sah.absence_reason
    FROM student_attendance_history sah
    JOIN student s ON sah.student_id = s.id  
    JOIN level l ON sah.eng_lvl_id = l.id
    JOIN "group" g ON sah.group_id = g.id
    WHERE sah.student_id = ANY($1)
    ORDER BY sah.date;
    """, student_ids)

    return transfer_data


async def get_transfer_info_custom(student_ids, start_date, end_date):
    # SQL-запрос для получения данных о переводе студентов, включая уровень и группу
    conn = await engine.connect_to_db()
    transfer_data = await conn.fetch("""
    SELECT s.id AS student_id, l.eng_lvl, g.group_name, sah.date, sah.status, sah.absence_reason
    FROM student_attendance_history sah
    JOIN student s ON sah.student_id = s.id 
    JOIN level l ON sah.eng_lvl_id = l.id
    JOIN "group" g ON sah.group_id = g.id
    WHERE sah.student_id = ANY($1)
      AND sah.date BETWEEN $2 AND $3
    ORDER BY sah.date;
    """, student_ids, start_date, end_date)

    return transfer_data


async def get_attendance_remainder(student_details_id):
    conn = await engine.connect_to_db()
    student_reminder = await conn.fetchrow("""
            SELECT 
                COUNT(*) FILTER (WHERE status IN ('present', 'absent')) AS total_classes,
                COUNT(*) FILTER (WHERE status = 'other') AS other_days,
                COUNT(*) FILTER (WHERE status IN ('present', 'absent')) % 12 AS remainder
            FROM 
                attendance
            WHERE 
                student_details_id = $1
            GROUP BY 
                student_details_id;
        """, student_details_id)
    # student_remainder = await conn.fetchrow("""
    #         SELECT 
    #             student_details_id,
    #             COUNT(*) AS total_classes,
    #             COUNT(*) % 12 AS remainder
    #         FROM 
    #             attendance
    #         WHERE 
    #             student_details_id = $1
    #             AND status IN ('present', 'absent')
    #         GROUP BY 
    #             student_details_id;
    #     """, (student_details_id))
   

    return student_reminder