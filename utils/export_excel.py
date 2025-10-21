from openpyxl import Workbook

def export_to_excel(records, filename="attendance_export.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    headers = ["ID", "Student Name", "Batch", "IP Address", "Location", "Date", "Time", "Status"]
    ws.append(headers)

    for row in records:
        ws.append([
            row["id"],
            row["student_name"],
            row["batch_name"],
            row["ip_address"],
            row["location"],
            str(row["date"]),
            str(row["checkin_time"]),
            row["status"]
        ])
    
    wb.save(filename)
    return filename
