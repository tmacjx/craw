"""
# @Author  wk
# @Time 2019/12/22 19:09

"""

# todo  找出重复的cate，然后找出cate下的usernam

import sqlite3
import os
import datetime
import xlsxwriter


def execute_sql(sql):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print('error ', e)
        conn.rollback()
    conn.close()


def query_category():
    result = []
    sql = "select distinct category_name from category_user"
    row_list = execute_sql(sql)
    for row in row_list:
        result.append(row[0])
    print(result)
    return result


def query_category_user(cate_name):
    result = []
    sql = "select userid from category_user where userid = '%s' " % cate_name
    row_list = execute_sql(sql)
    for row in row_list:
        result.append(row[0])
    print(result)
    return result


def query_user(userid):
    sql = "select * from post_user where userid = '%s' " % userid
    result = execute_sql(sql)
    print(result)
    return result


# todo 展示能auto_fit width宽度自动计算
def main():
    cate_list = query_category()
    for cate_name in cate_list:
        user_list = query_category_user(cate_name)
        cate_name = cate_name.replace('/', '&')
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        file_name = '%s_%s-%s.xls' % (cate_name, month, day)
        file_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".") + '/' + file_name
        _file = open(file_path, 'w')
        _file.close()

        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet('sheet')
        head_list = ['序号', 'ID', '姓名', '地址', '电话(固话)', '手机1', '手机2', '交易等级', '信用积分', '评分次数',
                     '发帖次数', '发帖积分', '注册日期', '认证员注', '警告原因']
        line = row = 0
        for head in head_list:
            worksheet.write(line, row, head)
            row += 1
        line = 1
        for userid in user_list:
                row = 0
                user_info = query_user(userid)
                if len(user_info) == 0:
                    break
                else:
                    user_info = user_info[0]
                user_id = user_info[0]
                user_name = user_info[1].strip()
                address = user_info[2].strip()
                fix_phone = user_info[3]
                phone1 = user_info[4]
                phone2 = user_info[5]
                trade_level = user_info[6]
                credit_score = user_info[7]
                score_count = user_info[8]
                post_count = user_info[9]
                post_score = user_info[10]
                register_time = user_info[11]
                remark = user_info[12].strip()
                warning_reason = user_info[-1].strip()
                info_list = [line, user_id, user_name, address, fix_phone, phone1, phone2, trade_level,
                             credit_score, score_count, post_count, post_score, register_time, remark, warning_reason]
                c = 0
                for val in info_list:
                    worksheet.set_column('{0}:{0}'.format(chr(c + ord('A'))), len(str(val)) + 2)
                    c += 1
                    worksheet.set_column(line, row, len(str(val)) + 2)
                    worksheet.write(line, row, val)
                    row += 1
                line += 1
        workbook.close()


if __name__ == '__main__':
    main()

