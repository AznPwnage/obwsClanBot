import csv


def read_score_file(file_path, sort_by, reverse, col_type):
    members = []
    with open(file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        headers = next(csv_reader)
        for row in csv_reader:
            members.append(row)
    mem_list = []
    for member in members:
        mem_as_json = {}
        for i in range(len(headers)):
            mem_as_json[headers[i]] = member[i]
        mem_list.append(mem_as_json)
    if sort_by is not None:
        reverse = reverse is not None
        if sort_by == 'inactive':
            reverse = not reverse

        if sort_by == 'clan_xp':
            reverse = not reverse
            mem_list = sorted(mem_list, key=lambda item: (int(item[sort_by + '_hunter']) + int(item[sort_by + '_warlock']) + int(item[sort_by + '_titan'])), reverse=reverse)
        elif col_type == 'int':
            mem_list = sorted(mem_list, key=lambda item: int(item[sort_by]), reverse=reverse)
        elif col_type == 'date':
            mem_list = sorted(mem_list, key=lambda item: item[sort_by][:10], reverse=reverse)
        elif col_type == 'str':
            mem_list = sorted(mem_list, key=lambda item: item[sort_by].lower(), reverse=reverse)
    return mem_list