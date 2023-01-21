from datetime import datetime
from dateutil import rrule
from pprint import pprint


data = []

with open('Expenses.txt', 'r') as f:
    for line in f.readlines():
        x = line.rstrip('\n').split(", ")
        data.append((datetime.strptime(x[0], '%Y-%m-%d').date(), x[1], float(x[2].split()[-1]), x[3], x[4]))

data.sort()
#pprint(data, width=100)

headings = {
    'Income': ['Salary'],
    'Expenses': ['Accommodation', 'Telecom', 'Online services', 'Transport', 'Grocery', 'Household items', 'Restaurants', 'Laundry', 'Activities', 'Investment', 'Others']
}
col_width = max(max(len(y) for y in x) for x in headings.values())

start_date = data[0][0]
end_date = data[-1][0]

def write_top_heading_line(f):
    f.write(f"+-{'-' * col_width}-")
    f.write(f"+{'-' * ((col_width + 3) * (len(headings['Income']) + 1) - 1)}")
    f.write(f"+{'-' * ((col_width + 3) * (len(headings['Expenses']) + 1) - 1)}")
    f.write('+\n')

def write_top_heading(f):
    f.write(f"| {'':>{col_width}} ")
    f.write(f"|{'Income':^{(col_width + 3) * (len(headings['Income']) + 1) - 1}}")
    f.write(f"|{'Expenses':^{(col_width + 3) * (len(headings['Expenses']) + 1) - 1}}")
    f.write('|\n')

def write_item_heading(f, period):
    f.write(f"| {period:^{col_width}} ")
    for i in headings['Income']:
        f.write(f"| {i:^{col_width}} ")
    f.write(f"| {'Total':^{col_width}} ")
    for e in headings['Expenses']:
        f.write(f"| {e:^{col_width}} ")
    f.write(f"| {'Total':^{col_width}} |")
    f.write('\n')

def write_item_heading_line(f):
    f.write(f"+-{'-' * col_width}-")
    for _ in headings['Income']:
        f.write(f"+-{'-' * col_width}-")
    f.write(f"+-{'-' * col_width}-")
    for _ in headings['Expenses']:
        f.write(f"+-{'-' * col_width}-")
    f.write(f"+-{'-' * col_width}-+")
    f.write('\n')

def write_data(f, freq, dtstart, dtfmt, dtattr):
    for dt in rrule.rrule(freq=freq, dtstart=dtstart, until=end_date):
        f.write(f"| {dt.strftime(dtfmt):>{col_width}} ")
        ss = 0
        for i in headings['Income']:
            s = sum([x[2] for x in data if x[1] == i and getattr(x[0], dtattr) == getattr(dt, dtattr)])
            f.write(f"| {f'${s:.2f}':>{col_width}} ")
            ss += s
        f.write(f"| {f'${ss:.2f}':>{col_width}} ")
        ss = 0
        for e in headings['Expenses']:
            s = sum([x[2] for x in data if x[1] == e and getattr(x[0], dtattr) == getattr(dt, dtattr)])
            f.write(f"| {f'${s:.2f}':>{col_width}} ")
            ss += s
        f.write(f"| {f'${ss:.2f}':>{col_width}} ")
        f.write('|\n')

with open('Monthly Report.txt', 'w') as f:
    write_top_heading_line(f)
    write_top_heading(f)
    write_top_heading_line(f)
    write_item_heading(f, 'Month')
    write_item_heading_line(f)
    write_data(f, rrule.MONTHLY, start_date.replace(day=1), '%b-%y', 'month')
    write_item_heading_line(f)

with open('Yearly Report.txt', 'w') as f:
    write_top_heading_line(f)
    write_top_heading(f)
    write_top_heading_line(f)
    write_item_heading(f, 'Year')
    write_item_heading_line(f)
    write_data(f, rrule.YEARLY, start_date.replace(month=1).replace(day=1), '%Y', 'year')
    write_item_heading_line(f)
