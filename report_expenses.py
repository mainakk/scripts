from datetime import datetime
from pathlib import Path
from dateutil import rrule


data_CA = []
data_IN = []

for filename in sorted(Path(".").glob("Expense_*.txt")):
    if filename.stem.endswith("_CA"):
        data = data_CA
    elif filename.stem.endswith("_IN"):
        data = data_IN
    with open(filename, "r") as f:
        for line in f.readlines():
            x = line.rstrip("\n").split(", ")
            #print(x)
            data.append(
                (
                    datetime.strptime(x[0], "%Y-%m-%d").date(),
                    x[1],
                    float(x[2].split()[-1]),
                    x[3],
                    x[4] if len(x) > 4 else "",
                )
            )

data_CA.sort()
data_IN.sort()

headings = {
    "Income": ["Salary", "Reimbursement"],
    "Expense": [
        "Tax",
        "Accommodation",
        "Utilities",
        "Telecom",
        "Health",
        "Online services",
        "Transport",
        "Grocery",
        "Household items",
        "Restaurants",
        "Laundry",
        "Activities",
        "Others",
    ],
    "Saving": ["Total", "(%) of Income"],
}
col_width = max(max(len(y) for y in x) for x in headings.values())

start_date_CA = data_CA[0][0]
end_date_CA = data_CA[-1][0]
start_date_IN = data_IN[0][0]
end_date_IN = data_IN[-1][0]


def write_top_heading_line(f):
    f.write(f"+-{'-' * col_width}-")
    f.write(f"+{'-' * ((col_width + 3) * (len(headings['Income']) + 1) - 1)}")
    f.write(f"+{'-' * ((col_width + 3) * (len(headings['Expense']) + 1) - 1)}")
    f.write(f"+{'-' * ((col_width + 3) * len(headings['Saving']) - 1)}")
    f.write("+\n")


def write_top_heading(f, location):
    currency = "CAD" if location == "CA" else "INR"
    f.write(f"| {'':>{col_width}} ")
    f.write(f"|{f'Income ({currency})':^{(col_width + 3) * (len(headings['Income']) + 1) - 1}}")
    f.write(f"|{f'Expense ({currency})':^{(col_width + 3) * (len(headings['Expense']) + 1) - 1}}")
    f.write(f"|{f'Saving ({currency})':^{(col_width + 3) * len(headings['Saving']) - 1}}")
    f.write("|\n")


def write_item_heading(f, period):
    f.write(f"| {period:^{col_width}} ")
    for i in headings["Income"]:
        f.write(f"| {i:^{col_width}} ")
    f.write(f"| {'Total':^{col_width}} ")
    for e in headings["Expense"]:
        f.write(f"| {e:^{col_width}} ")
    f.write(f"| {'Total':^{col_width}} ")
    for e in headings["Saving"]:
        f.write(f"| {e:^{col_width}} ")
    f.write("|\n")


def write_item_heading_line(f):
    f.write(f"+-{'-' * col_width}-")
    for _ in headings["Income"]:
        f.write(f"+-{'-' * col_width}-")
    f.write(f"+-{'-' * col_width}-")
    for _ in headings["Expense"]:
        f.write(f"+-{'-' * col_width}-")
    f.write(f"+-{'-' * col_width}-")
    for _ in headings["Saving"]:
        f.write(f"+-{'-' * col_width}-")
    f.write("+\n")


def write_month_heading(f, location):
    write_top_heading_line(f)
    write_top_heading(f, location)
    write_top_heading_line(f)
    write_item_heading(f, "Month")
    write_item_heading_line(f)


def write_data(f, freq, dtstart, until, dtfmt, dtattrs, location):
    print(f"Writing data for {location} from {dtstart} to {until}")
    data = globals()[f"data_{location}"]
    for dt in rrule.rrule(freq=freq, dtstart=dtstart, until=until):
        f.write(f"| {dt.strftime(dtfmt):>{col_width}} ")
        ss_i = 0
        for i in headings["Income"]:
            s = sum(
                [
                    x[2]
                    for x in data
                    if x[1] == i
                    and all(
                        getattr(x[0], attr) == getattr(dt, attr) for attr in dtattrs
                    )
                ]
            )
            f.write(f"| {f'{s:.2f}':>{col_width}} ")
            ss_i += s
        f.write(f"| {f'{ss_i:.2f}':>{col_width}} ")
        ss_e = 0
        for e in headings["Expense"]:
            s = sum(
                [
                    x[2]
                    for x in data
                    if x[1] == e
                    and all(
                        getattr(x[0], attr) == getattr(dt, attr) for attr in dtattrs
                    )
                ]
            )
            f.write(f"| {f'{s:.2f}':>{col_width}} ")
            ss_e += s
        f.write(f"| {f'{ss_e:.2f}':>{col_width}} ")
        ss_s = ss_i - ss_e
        f.write(f"| {f'{ss_s:.2f}':>{col_width}} ")
        r = ss_s / ss_i * 100 if ss_i > 0 else 0.0
        f.write(f"| {f'{r:.2f}':>{col_width}} ")
        f.write("|\n")


for location in ("CA", "IN"):
    with open(f"Monthly_Report_{location}.txt", "w", encoding="utf-8") as f:
        start_date = globals()[f"start_date_{location}"]
        end_date = globals()[f"end_date_{location}"]
        if end_date.year > start_date.year:
            write_month_heading(f, location)
            write_data(
                f,
                rrule.MONTHLY,
                start_date.replace(day=1),
                start_date.replace(month=12).replace(day=31),
                "%b-%y",
                ("month", "year"),
                location,
            )
        for until in rrule.rrule(
            freq=rrule.YEARLY,
            dtstart=start_date.replace(year=start_date.year+1).replace(month=12).replace(day=31),
            until=end_date,
        ):
            write_month_heading(f, location)
            write_data(
                f,
                rrule.MONTHLY,
                until.replace(month=1).replace(day=1),
                until,
                "%b-%y",
                ("month", "year"),
                location,
            )
        write_month_heading(f, location)
        write_data(
            f,
            rrule.MONTHLY,
            end_date.replace(month=1).replace(day=1),
            end_date,
            "%b-%y",
            ("month", "year"),
            location,
        )
        write_item_heading_line(f)

for location in ("CA", "IN"):
    with open(f"Yearly_Report_{location}.txt", "w", encoding="utf-8") as f:
        start_date = globals()[f"start_date_{location}"]
        write_top_heading_line(f)
        write_top_heading(f, location)
        write_top_heading_line(f)
        write_item_heading(f, "Year")
        write_item_heading_line(f)
        write_data(
            f,
            rrule.YEARLY,
            start_date.replace(month=1).replace(day=1),
            end_date,
            "%Y",
            ("year",),
            location,
        )
        write_item_heading_line(f)
