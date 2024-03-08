from flask import Flask, render_template, request, redirect, flash, url_for
from difflib import ndiff
import sqlite3
import re

def remove_whitespace(s):
    return re.sub(r'\s+', '', s)

# flag = True
app = Flask(__name__)
@app.route('/')
def index():
    conn = sqlite3.connect("ie_info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ver FROM version_info")  # Fetch unique items for dropdown from "version" table
    filters = [row[0] for row in cursor.fetchall()]
    conn.close()
    # flag = True
    return render_template('index.html', filters=filters)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query').strip()
    filter_value = request.args.get('filter') # Use get() method to retrieve filter_value

    conn = sqlite3.connect("ie_info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ver FROM version_info")  # Fetch unique items for dropdown from "version" table
    filters = [row[0] for row in cursor.fetchall()]  # Fetch filters here
    if filter_value:
        cursor.execute("SELECT I.ie_name, I.sub_ie, I.field, I.type, I.description, S.structure, I.ver FROM ie_info i, ie_structures S WHERE I.ie_name = S.ie_name and I.ver = S.ver and field LIKE ? AND I.ver = ?", ('%' + query + '%', filter_value))
    else:
        cursor.execute("SELECT I.ie_name, I.sub_ie, I.field, I.type, I.description, S.structure, I.ver FROM ie_info i, ie_structures S WHERE I.ie_name = S.ie_name and I.ver = S.ver and field LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()
    # flag = True
    return render_template('results.html', results=results, filters=filters)  # Pass filters to the template

@app.route('/compare', methods=['GET'])
def compare():
    conn = sqlite3.connect("ie_info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ver FROM version_info")
    filters = [row[0] for row in cursor.fetchall()]
    filter1 = request.args.get('version1')
    filter2 = request.args.get('version2')

    # global flag
    # if flag:
    #     results2=()
        # flag = False
        # return render_template('compare.html', filters=filters, results2=results2)
    # else:
    cursor.execute("SELECT ie_name, structure FROM ie_structures WHERE ver = ?", (filter1,))
    version1_data = cursor.fetchall()

    cursor.execute("SELECT ie_name, structure FROM ie_structures WHERE ver = ?", (filter2,))
    version2_data = cursor.fetchall()

    conn.close()

    # Extract ie_names and structures separately
    version1_names = [row[0].strip() for row in version1_data]
    version1_structures = [row[1] for row in version1_data]

    version2_names = [row[0].strip() for row in version2_data]
    version2_structures = [row[1] for row in version2_data]

    # Find names missing from each version
    ver1 = set(version1_names) - set(version2_names)
    ver2 = set(version2_names) - set(version1_names)

    # Construct list of tuples with name, structure, and filter version it's missing from
    results2 = [(name, "Missing from version ", filter2, '', '', structure) for name, structure in
                zip(version1_names, version1_structures) if name in ver1] + \
               [(name, "Missing from version ", filter1, '', '', structure) for name, structure in
                zip(version2_names, version2_structures) if name in ver2]



    # for name1, structure1 in zip(version1_names, version1_structures):
    #     if name1 in version2_names:
    #         idx = version2_names.index(name1)
    #         structure2 = version2_structures[idx]
    #         # s2 = structure2
    #         # Compare structures using ndiff
    #         diff = list(ndiff(structure1.splitlines(keepends=True), structure2.splitlines(keepends=True)))
    #         if any(line.startswith('+') or line.startswith('-') for line in diff):
    #             # If differences found, append to results with highlighting
    #             results2.append((name1, "Different in both versions", filter1, filter2, structure1, structure2))
    for name1, structure1 in zip(version1_names, version1_structures):
        if name1 in version2_names:
            idx = version2_names.index(name1)
            structure2 = version2_structures[idx]
            # Remove whitespace from both structures
            structure1_clean = remove_whitespace(structure1)
            structure2_clean = remove_whitespace(structure2)
            # Compare structures using ndiff
            diff = list(ndiff(structure1_clean.splitlines(keepends=True), structure2_clean.splitlines(keepends=True)))
            if any(line.startswith('+') or line.startswith('-') for line in diff):
                # If differences found, append to results with highlighting
                results2.append((name1, "Different in both versions", filter1, filter2, structure1, structure2))
    # flag = True
    return render_template('compare.html', filters=filters, results2=results2)


if __name__ == '__main__':
    app.run(debug=True)
