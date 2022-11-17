from datetime import datetime
import SharePoint
import sql

share_point = SharePoint.SharePoint('login', 'pass')
SCHEDULE_LINK = r"https://portal.petrocollege.ru/_api/Web/Lists(guid'9c095153-274d-4c73-9b8b-4e3dd6af89e5')/Items"
checkerboard_links = share_point.get_data_from_lists_type(share_point.get_request_json(SCHEDULE_LINK))
cursor = sql.cursor
select_file_query = "SELECT * FROM file"
cursor.execute(select_file_query)
files_in_db = cursor.fetchall()


def parse_filename(filename):
    """
    Format data from filename
    :param filename: string, name of file
    :return:
    {
        'name': '01_преп_текущие_01.09-11.09',
        'date_begin': '2022-09-01',
        'date_end': '2022-09-11',
        'num': 1
    }
    """
    today = datetime.now()
    year = today.year
    data = filename.split("_")
    num = int(data[0])
    # dates
    dates = data[-1][:-5]
    date_begin, date_end = dates.split("-")
    date_begin = date_begin + "." + str(year)
    date_end = date_end + "." + str(year)
    date_begin = datetime.strptime(date_begin, "%d.%m.%Y")
    date_end = datetime.strptime(date_end, "%d.%m.%Y")
    # name
    name = filename[:-5]
    return {
        "name": name,
        "date_begin": date_begin.strftime("%Y-%m-%d"),
        "date_end": date_end.strftime("%Y-%m-%d"),
        "num": num

    }


def save_to_db(cursor, name, path, date_begin, date_end, num):
    """
    Save data to file table
    :param cursor:  sql.cursor
    :param name:  string
    :param path:  string ex. files/some.xlsx
    :param date_begin: string ex. 2022-03-23
    :param date_end: string  ex. 2022-03-23
    :param num: int
    :return: int id
    """
    cursor.execute("INSERT INTO `file` "
                   "(`id`, `name`, `path`, `date_begin`, `date_end`, `num`, `created_at`) "
                   "VALUES "
                   "(NULL, '{}','{}','{}','{}','{}',CURRENT_TIMESTAMP)".format(name, path, date_begin,
                                                                               date_end, num))
    return cursor.lastrowid


def chek_exist_in_db(files_in_db, full_path):
    """
    Check existing in db
    :param files_in_db: list
    :param full_path: full path ex. files/some.xlsx
    :return: bool
    """
    for row in files_in_db:
        if row["path"] == full_path:
            return True
    return False


'''
Поиск нужного пукта меню
В данном случае - шахматка преподавателей
'''
for item in checkerboard_links:
    if 'Архив шахматок ПРЕПОДАВАТЕЛЕЙ' in item['title']:
        # проучаем файлы, которые в рвзделе
        files = share_point.get_data_from_attachment_files_type(
            share_point.get_request_json("https://portal.petrocollege.ru/_api/" + item['link'] + "/AttachmentFiles"))
        # сохраняем файлы в папку
        for file in files:
            file_attr = parse_filename(file['FileName'])
            is_save = share_point.save_file_by_url("https://portal.petrocollege.ru/_api/web", file['ServerRelativeUrl'],
                                                   file['FileName'], 'files')
            if is_save:
                full_path = 'files/' + file['FileName']
                if not chek_exist_in_db(files_in_db, full_path):
                    save_to_db(cursor, file_attr["name"], full_path, file_attr["date_begin"], file_attr["date_end"],
                               file_attr["num"])
        sql.cnx.commit()
