import os
import time
import datetime

start_time = time.time()

from File import *
import sql

cursor = sql.cursor
# Get teacher record
drop_table_query = "SELECT * FROM teacher"
cursor.execute(drop_table_query)
result = cursor.fetchall()
# Get building records
select_all_building = "SELECT * FROM building"
cursor.execute(select_all_building)
buildings = cursor.fetchall()

# Get room records
select_all_rooms = "SELECT * FROM room"
cursor.execute(select_all_rooms)
rooms = cursor.fetchall()

# Get schedule_has_student_group records
select_all_schedule_has_student_group = "SELECT * FROM schedule_has_student_group"
cursor.execute(select_all_schedule_has_student_group)
schedule_has_student_group = cursor.fetchall()

# Get schedule records
select_all_schedule = "SELECT * FROM schedule"
cursor.execute(select_all_schedule)
schedules = cursor.fetchall()

select_all_disciplines = "SELECT * FROM discipline"
cursor.execute(select_all_disciplines)
disciplines = cursor.fetchall()

# Get group records
select_all_student_group = "SELECT * FROM student_group"
cursor.execute(select_all_student_group)
student_groups = cursor.fetchall()

select_file_query = "SELECT * FROM file where is_done= false"
cursor.execute(select_file_query)
files_in_db = cursor.fetchall()

for file_in_db in files_in_db:
    print("load file", os.path.abspath(os.getcwd()) + '/' + file_in_db["path"])
    file = ExcelFile(os.path.abspath(os.getcwd()) + '/' + file_in_db["path"])
    data = file.get_object()

    for item in data:
        """
        TEACHERS
        """
        for k in result:
            if item['teacher'] == k['name']:
                item['teacher_id'] = k['id']
        if 'teacher_id' not in item:
            cursor.execute("INSERT INTO `teacher` "
                           "(`id`, `name`) "
                           "VALUES (NULL, '{}')".format(item['teacher']))
            result.append({"id": cursor.lastrowid, "name": item['teacher']})
            item['teacher_id'] = cursor.lastrowid
        """
        LESSONS
        """
        for lesson in item['teacher_lessons']:
            """
            BUILDINGS
            """
            for building in buildings:
                if lesson['lesson']['building'] == building['name']:
                    lesson['lesson']['building_id'] = building['id']
            if 'building_id' not in lesson['lesson']:
                cursor.execute("INSERT INTO `building` "
                               "(`id`, `name`) "
                               "VALUES (NULL, '{}')".format(lesson['lesson']['building']))
                buildings.append({"id": cursor.lastrowid, "name": lesson['lesson']['building']})
                lesson['lesson']['building_id'] = cursor.lastrowid

            """
            ROOMS
            """
            for room in rooms:
                if lesson['lesson']['room'] == room['name']:
                    lesson['lesson']['room_id'] = room['id']
            if 'room_id' not in lesson['lesson']:
                cursor.execute("INSERT INTO `room` "
                               "(`id`, `name`,`building_id`) "
                               "VALUES (NULL, '{}', {})".format(lesson['lesson']['room'],
                                                                int(lesson['lesson']['building_id'])))
                rooms.append({"id": cursor.lastrowid, "name": lesson['lesson']['room'],
                              "building_id": int(lesson['lesson']['building_id'])})
                lesson['lesson']['room_id'] = cursor.lastrowid

            """
            GROUPS{"group": group_name, "year": year, "course": course}
            """
            student_group_ids = []
            for group in student_groups:
                for group_item in lesson['lesson']['groups']:
                    if group_item["group"] == group['name']:
                        if 'student_group_ids' not in lesson['lesson']:
                            lesson['lesson']['student_group_ids'] = []
                        lesson['lesson']['student_group_ids'].append(group['id'])
            if 'student_group_ids' not in lesson['lesson']:
                for group_item in lesson['lesson']['groups']:
                    cursor.execute("INSERT INTO `student_group`"
                                   "(`id`, `name`, `course`, `year`) "
                                   "VALUES (NULL, '{}','{}','{}')".format(group_item["group"],
                                                                          int(group_item["course"]),
                                                                          int(group_item["year"])))
                    student_groups.append({"id": cursor.lastrowid, "name": group_item["group"]})
                    if 'student_group_ids' not in lesson['lesson']:
                        lesson['lesson']['student_group_ids'] = []
                    lesson['lesson']['student_group_ids'].append(cursor.lastrowid)
            """
            DISCIPLINE
            """
            for discipline in disciplines:
                if lesson['lesson']['discipline'] == discipline['name']:
                    lesson['lesson']['discipline_id'] = discipline['id']
            if 'discipline_id' not in lesson['lesson']:
                cursor.execute("INSERT INTO `discipline` "
                               "(`id`, `name`,`is_dop`) "
                               "VALUES (NULL, '{}', {})".format(lesson['lesson']['discipline'],
                                                                lesson['lesson']['is_dop']))
                disciplines.append({"id": cursor.lastrowid, "name": lesson['lesson']['discipline'],
                                    "is_dop": lesson['lesson']['is_dop']})
                lesson['lesson']['discipline_id'] = cursor.lastrowid

            """
            SCHEDULE
            """
            for schedule in schedules:
                if item['teacher_id'] == schedule['teacher_id'] and lesson['lesson']['discipline_id'] == \
                        schedule['discipline_id'] and lesson['lesson']['room_id'] == schedule['room_id']:
                    item['schedule_id'] = schedule['id']

            if 'schedule_id' not in lesson['lesson']:
                cursor.execute("INSERT INTO `schedule` "
                               "(`id`, `teacher_id`,`discipline_id`,`room_id`,`subgroup`,`number_of_lesson`, `date_lesson`) "
                               "VALUES (NULL, {}, {},{}, {}, {}, '{}')".format(
                    int(item['teacher_id']),
                    int(lesson['lesson']['discipline_id']),
                    int(lesson['lesson']['room_id']),
                    int(lesson['lesson']['subgroup']),
                    int(lesson['number_of_lesson']),
                    lesson['date_lesson'].strftime("%Y-%m-%d")
                ))
                schedules.append({
                    "id": cursor.lastrowid,
                    "teacher_id": item['teacher_id'],
                    "discipline_id": lesson['lesson']['discipline_id'],
                    "room_id": lesson['lesson']['room_id'],
                    "subgroup": lesson['lesson']['subgroup'],
                    "number_of_lesson": lesson['number_of_lesson'],
                    "date_lesson": lesson['date_lesson'],
                })
                item['schedule_id'] = cursor.lastrowid
            """
            SCHEDULE STUDENT
            """
            for schedule_student in schedule_has_student_group:
                if item['schedule_id'] == schedule_student['schedule_id'] \
                        and schedule_student['student_group_id'] in lesson['lesson']['student_group_ids']:
                    lesson['lesson']['schedule_student_id'] = schedule_student['id']
            if 'schedule_student_id' not in lesson['lesson']:
                for group_id in lesson['lesson']['student_group_ids']:
                    cursor.execute("INSERT INTO `schedule_has_student_group` "
                                   "(`id`, `schedule_id`,`student_group_id`) "
                                   "VALUES (NULL, {}, {})".format(
                        int(item['schedule_id']),
                        group_id,
                    ))

                schedule_has_student_group.append({
                    "id": cursor.lastrowid,
                    "schedule_id": item['schedule_id'],
                    "student_group_id": group_id,

                })
                item['schedule_has_student_group_id'] = cursor.lastrowid
    now = datetime.now()
    cursor.execute("""
    UPDATE `file` SET `is_done`=%s, `date_done` = %s WHERE `file`.`id` = %s;
    """, (1, now.strftime("%Y-%m-%d"), file_in_db["id"]))
    sql.cnx.commit()
    print("file" + file_in_db["path"] + " done in %s seconds " % (time.time() - start_time))
