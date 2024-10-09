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
    

async def get_groups_for_level(selected_level):
    """ Получаем список групп для заданного уровня """

    conn = await engine.connect_to_db()
    groups = await conn.fetch("""
        SELECT g.id, g.group_number 
        FROM group_details gd
        JOIN "group" g ON gd.group_id = g.id
        WHERE gd.eng_lvl_id = $1
    """, selected_level)

    if groups:
        sorted_groups = sorted(groups, key=lambda x: x['group_number'])
        return sorted_groups

# async def get_teacher_id(tg_id):
#     conn = await engine.connect_to_db()

#     teacher_id = await conn.fetchval("""
#         SELECT id FROM teacher WHERE tg_id = $1
#     """, tg_id)

#     return teacher_id


# async def get_lvl_from_current_pos():
#     conn = await engine.connect_to_db()

#     lvl_id = await conn.fetchval("""
#         SELECT lvl_id FROM current_position WHERE teacher_id = 1
#     """)

#     return lvl_id

async def get_lvl_id(selected_level):
    conn = await engine.connect_to_db()
    level_id = await conn.fetchval("""
        SELECT id FROM level WHERE eng_lvl = $1
    """, selected_level)

    return level_id


async def get_group_number(group_id):
    conn = await engine.connect_to_db()
    group_number_not_id = await conn.fetchval("""
        SELECT group_number FROM "group" WHERE id = $1
    """, group_id)

    return group_number_not_id


# async def insert_lvl_teacher_current_pos(lvl_id, teacher_id):
#     conn = await engine.connect_to_db()
#     query = await conn.execute("""
#     INSERT INTO current_position (lvl_id, teacher_id)
#     VALUES ($1, $2)
#     ON CONFLICT (teacher_id) DO UPDATE
#     SET lvl_id = EXCLUDED.lvl_id;
#     """, lvl_id, teacher_id)


async def add_student(student_name):
    conn = await engine.connect_to_db()
    await conn.execute("""
            INSERT INTO student (name) VALUES ($1)
        """, student_name)
    
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
        SELECT id FROM group_details WHERE eng_lvl_id = $1 AND group_id = $2
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
            WHERE sd.group_details_id = $1;
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
            DO UPDATE SET status = EXCLUDED.status
        """, student_details_id, date, status)


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
            DELETE FROM student_details
            WHERE student_id = $1;
        """, student_id)

    await conn.execute("""
            DELETE FROM student
            WHERE id = $1;
        """, student_id)