import os
import sqlite3
import sys
from docx import Document

def extract_fields_and_descriptions(doc_path):
    doc = Document(doc_path)
    field_descriptions = []

    current_field = None
    current_description = []
    sub_ie = ""
    checknextline = False
    for line in doc.element.body.iter():
        # Check if the line is a text element
        if line.text is not None:
            text = line.text.strip()
            if text == "<start>":
                print("Found <start>")
                checknextline = True
                # Start of a new field and description block
                current_field = None
                current_description = []
            elif checknextline:
                sub_ie = text
                checknextline = False
            elif text == "<endl>":
                print("Found <endl>")
                # End of the current field and description block
                if current_field is not None:
                    field_descriptions.append((sub_ie, current_field, '\n'.join(current_description)))
                    current_field = None
                    current_description = []
            elif current_field is None:
                # First non-empty line after <start> is the field name
                current_field = text
                print(f"Field Name: {current_field}")
            else:
                # Non-empty lines after the field name before <endl> are part of the description
                current_description.append(text)

    return field_descriptions


def store_field_descriptions_in_db(field_descriptions, db_path, version):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    conn.commit()
    not_found_entries = []
    for sub_ie, field_name, description in field_descriptions:
        cursor.execute(
            "SELECT rowid FROM ie_info WHERE LOWER(sub_ie) = LOWER(?) AND LOWER(field) = LOWER(?) AND status == 0"
            " AND ver = (?) LIMIT 1", (sub_ie, field_name, version))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                (description, row[0]))
            continue
        else:
            cursor.execute(
                "SELECT rowid FROM ie_info WHERE LOWER(sub_ie) LIKE LOWER(?) AND LOWER(field) LIKE LOWER(?) AND "
                "status == 0 AND ver = (?) LIMIT 1", (f"{sub_ie}%", f"{field_name}%", version))
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                    (description, row[0]))
                continue
            else:
                s = sub_ie[:-4]
                f = field_name[:-4]
                cursor.execute(
                    "SELECT rowid FROM ie_info WHERE LOWER(sub_ie) LIKE LOWER(?) AND LOWER(field) LIKE LOWER(?) AND "
                    "status == 0 AND ver = (?) LIMIT 1", (f"{s}%", f"{f}%", version))
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                        (description, row[0]))
                    continue
                else:
                    cursor.execute(
                        "SELECT rowid FROM ie_info WHERE LOWER(ie_name) LIKE LOWER(?) AND LOWER(field) LIKE LOWER(?) AND "
                        "status == 0 AND ver = (?) LIMIT 1", (f"{sub_ie}%", f"{field_name}%", version))
                    row = cursor.fetchone()
                    if row:
                        cursor.execute(
                            "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                            (description, row[0]))
                        continue
                    else:
                        s = sub_ie[:-4]
                        cursor.execute(
                            "SELECT rowid FROM ie_info WHERE LOWER(ie_name) LIKE LOWER(?) AND LOWER(field) LIKE LOWER(?) AND "
                            "status == 0 AND ver = (?) LIMIT 1", (f"{s}%", f"{field_name}%", version))
                        row = cursor.fetchone()
                        if row:
                            cursor.execute(
                                "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                                (description, row[0]))
                            continue
                        else:
                            f = field_name.rsplit('-', 1)[0]

                            cursor.execute(
                                "SELECT rowid FROM ie_info WHERE LOWER(ie_name) LIKE LOWER(?) AND LOWER(field) LIKE "
                                "LOWER(?) AND status == 0 AND ver = (?) LIMIT 1", (f"{sub_ie}", f"{f}%", version))
                            row = cursor.fetchone()
                            if row:
                                cursor.execute(
                                    "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                                    (description, row[0]))
                                continue
                            else:
                                cursor.execute(
                                    "SELECT rowid FROM ie_info WHERE LOWER(field) = LOWER(?) AND status == (?) "
                                    " AND ver = (?) LIMIT 1", (field_name, 0, version))
                                row = cursor.fetchone()
                                if row:
                                    cursor.execute(
                                        "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                                        (description, row[0]))
                                    continue
                                else:
                                    cursor.execute(
                                        "SELECT rowid FROM ie_info WHERE LOWER(field) LIKE LOWER(?) AND status == (?) "
                                        " AND ver = (?) LIMIT 1", (f"{field_name}%", 0, version))
                                    row = cursor.fetchone()
                                    if row:
                                        cursor.execute(
                                            "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                                            (description, row[0]))
                                        continue
                                    else:
                                        if ',' in field_name:
                                            # Split field_name
                                            parts = field_name.split(',')
                                            parts.reverse()  # Because otherwise there maybe errors in the flow
                                            for part in parts:
                                                f_part = part.strip()
                                                cursor.execute(
                                                    "SELECT rowid FROM ie_info WHERE LOWER(field) LIKE LOWER(?) AND "
                                                    "status == (?) AND ver = (?) LIMIT 1", (f"{f_part}%", 0, version))
                                                row = cursor.fetchone()
                                                if row:
                                                    cursor.execute(
                                                        "UPDATE ie_info SET description = ?, status = 1 WHERE rowid = ?",
                                                        (description, row[0]))
                                                else:
                                                    not_found_entries.append((f_part, field_name, description))
                                        else:
                                            not_found_entries.append((sub_ie, field_name, description))

    # Write not found entries to a text file with utf-8 encoding
    with open('not_found_entries.txt', 'w', encoding='utf-8') as file:
        for entry in not_found_entries:
            file.write(f"No matching sub_ie: {entry[0]}, field: {entry[1]}, description: {entry[2]}\n")

    conn.commit()
    conn.close()


def main(docx_filename, version):
    input_document_path = "extracted_tables_with_heading.docx"
    database_path = "ie_info.db"
    fields_and_descriptions = extract_fields_and_descriptions(input_document_path)
    store_field_descriptions_in_db(fields_and_descriptions, database_path, version)


if __name__ == "__main__":
    # print("Hello world")
    if len(sys.argv) != 3:
        print("Usage: python storingTableData.py <docx_filename>")
        # sys.exit(1)
    docx_filename = sys.argv[1]
    version = sys.argv[2]
    main(docx_filename, version)
    os.remove(docx_filename)