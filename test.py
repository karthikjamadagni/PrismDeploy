import sqlite3
# from docx import Document
conn = sqlite3.connect("ie_info.db")
cursor = conn.cursor()
# cursor.execute('''CREATE TABLE IF NOT EXISTS version_info (
#                             id INTEGER PRIMARY KEY AUTOINCREMENT,
#                             ver TEXT
#                          )''')

conn.commit()
# cursor.execute("select field_name from  field_descriptions")
# result = cursor.fetchall()
# print(result)
# and field = "requestedSIB-List"
cursor.execute("drop table ie_info")
cursor.execute("drop table version_info")
cursor.execute("drop table ie_structures")
# cursor.execute("Update ie_info set description = '', status = 0 ")
# cursor.execute("drop table version_info")
# versi = "17.1.0"
# cursor.execute("INSERT INTO version_info (ver) VALUES (?)", (versi,))
# conn.commit()
# cursor.execute("SELECT * from version_info")
conn.commit()
results = cursor.fetchall()
print(results)
conn.close()
# with open('output_results.txt', 'w', encoding='utf-8') as file:
#     for result in results:
#         file.write(f"{result[0]}\n")
