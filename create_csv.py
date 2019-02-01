import os, csv

raw_data_dir = '/data/MBDU/ABCDraw/'

# Create the first row of the CSV file
first_row = sorted(os.listdir(raw_data_dir))
first_row.insert(0, 'SUBJECTKEY')

# Scan all directories and collect all subject IDs
subject_keys = []
for directory in first_row:
    abspath = raw_data_dir + directory
    if not os.path.isdir(abspath):
        continue
    temp_list = os.listdir(abspath)
    temp_keys = [x.split('_')[0].strip('sub-') for x in temp_list]
    subject_keys += temp_keys

# Make subject keys unique
subject_keys = set(subject_keys)

# Start constructing each line of the CSV file...
with open('summary_csv.csv', 'w') as wf:
    writer = csv.writer(wf, delimiter=',')
    # First line containing description
    writer.writerow(first_row)
    ''' For each subject cd into each directory and try to find
        a file with matching subject ID. If a file is found append
        to the subject row and go to next directory (i.e. a single file per
        subject per directory is expected)...'''
    for subject in subject_keys:
        row = [subject]
        for directory in first_row:
            abspath = raw_data_dir + directory
            if not os.path.isdir(abspath):
                continue
            file_exists = False
            for files in os.listdir(abspath):
                if subject in files:
                    row.append(files)
                    file_exists = True
                    break
            if not file_exists:
                row.append('N/A')
        writer.writerow(row)
