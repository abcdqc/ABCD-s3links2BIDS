import argparse
import os
import csv
from input_python_program import download_a_link
from directory_dictionary import directory_dictionary
import tarfile
import shutil

'''
   This set of functions is used to download various raw MRI files to a set of pre-specified
   directories. The existence of the following files is assumed:
   - A .csv file that contains all MID, nBack, SST, rest, T1 and T2 raw data links
   - A .csv file that contains all the events raw data links
   - A text file that contains a unique subject list of all subjects in the first .csv file above
   - A test file that contains a unique subject list of all subjects in the second .csv file above
   The unique subject text files can be generated from the .csv files using the proc below..
'''

target_base_dir = '/data/MBDU/ABCDraw/'
epi_list = ['MID', 'nBack', 'SST', 'rs', 'T1', 'T2']

image03_subjects = 'image03.txt'
events_subjects = 'fmri_results.txt'

'''
   Use this function to generate the subject text files..
'''
def gen_unique_subject_keys(csv_in, subjkey_out):
    subject_list = []
    with open(csv_in, 'r') as csv_f:
        csv_r = csv.reader(csv_f, delimiter=',')
        # Skip the header..
        next(csv_r)
        for idx, row in enumerate(csv_r):
            subject_list.append(row[2])

    # Make the list unique involving the set function
    unique_subject_list = list(set(subject_list))
    with open(subjkey_out, 'w') as write_file:
        for subject in unique_subject_list:
            write_file.write(subject+'\n')


def get_target_dir(dir):
    return target_base_dir + dir


def find_epi_from_subject(subject, epi):
    link_list = []
    manuf = None
    description = 'ABCD-'+epi
    if epi == "MID" or epi == "nBack" or epi == "SST":
        description += "-"
    if epi != "T1" and epi != "T2":
        description += "fMRI"
    with open("IMAGE03_DATA_TABLE.csv", 'r') as csv_f:
        csv_r = csv.DictReader(csv_f, delimiter=',')
        for row in csv_r:
            if subject == row['SUBJECTKEY'] and description == row['IMAGE_DESCRIPTION']:
                link_list.append(row['IMAGE_FILE'])
                if manuf is None:
                    manuf = row['SCANNER_MANUFACTURER_PD']
                    if manuf == "Philips Medical Systems":
                        manuf = "Philips"
                    elif manuf == "GE MEDICAL SYSTEMS":
                        manuf = "GE"
    link_list = sorted(list(set(link_list)))
    return manuf, link_list


def find_events_from_subject(subject, epi):
    link_list = []
    with open("FMRIRESULTS01_DATA_TABLE.csv", 'r') as csv_f:
        csv_r = csv.DictReader(csv_f, delimiter=',')
        for row in csv_r:
            if row['SUBJECTKEY'] == subject and \
               row['SESSION_DET'].lower() == "abcd-mproc-" + epi.lower():
                link_list.append(row['DERIVED_FILES'])
    link_list = sorted(list(set(link_list)))
    return link_list


def find_closest_time(link, ap):
    link = link.split('/')[-1]
    mid_subj = link[0:15]
    mid_time = int(link[-18:-4])
    min_dt = 100000
    good_link = None
    with open("IMAGE03_DATA_TABLE.csv", 'r') as csv_f:
        csv_r = csv.DictReader(csv_f, delimiter=',')
        for row in csv_r:
            if ap is None:
                description = "ABCD-fMRI-FM"
            else:
                description = "ABCD-fMRI-FM-" + ap
            if (mid_subj in row['IMAGE_FILE']) and (row['IMAGE_DESCRIPTION'] == description):
                flink = row['IMAGE_FILE'] # s3 link for fmap
                fmri = flink.split('/')[-1]
                if (ap == fmri[-21:-19]) or (ap is None):
                    fmap_time = int(fmri[-18:-4])
                    if abs(fmap_time - mid_time) < min_dt:
                        min_dt = abs(fmap_time - mid_time)
                        good_link = flink
    return good_link

def filter_links_by_number(epi, link_list):
    if epi == 'T1' or epi == 'T2':
        return link_list[0:1]
    elif epi != 'rs':
        if len(link_list) < 2:
            return []
        else:
            return link_list[0:2]
    else:
        if len(link_list) < 4:
            return []
        else:
            return link_list[0:4]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to download raw files to pre-specified directories')
    parser.add_argument('--line', type=int, default=0, help='Line to process from subject files')
    args = parser.parse_args()

    # Pick the subject on the line given as input to the script
    with open(image03_subjects, 'r') as f:
        for i, line in enumerate(f):
            if i == args.line:
                subject = line.strip()
                break

    # Download all MID, nBack etc..first:
    for epis in epi_list:
        manuf, link_list = find_epi_from_subject(subject, epis)
        link_list = filter_links_by_number(epis, link_list)
        if not link_list:
            continue
        # print("manuf: %s length: %d" % (manuf, len(link_list)))
        i = 1
        for links in link_list:
            key = epis + str(i)
            # print("epi key: %s" % key)
            download_a_link(links, get_target_dir(directory_dictionary[key]))
            # For T1 and T2 there are no fmaps to download
            if epis == "T1" or epis == "T2":
                continue
            if manuf != "GE":
                for ap in ['AP', 'PA']:
                    fmap_link = find_closest_time(links, ap)
                    # print("fmap_link: %s" % fmap_link)
                    key_fmap = key + '_' + manuf + '_' + ap
                    # print("key_fmap: %s" % key_fmap)
                    download_a_link(fmap_link, get_target_dir(directory_dictionary[key_fmap]))
            else:
                fmap_link = find_closest_time(links, None)
                # print("fmap_link: %s" % fmap_link)
                key_fmap = key + "_GE"
                download_a_link(fmap_link, get_target_dir(directory_dictionary[key_fmap]))
            i += 1


    # Pick the subject on the line given as input to the script
    with open(events_subjects, 'r') as f:
        for i, line in enumerate(f):
            if i == args.line:
                subject = line.strip()
                break

    # Download the events files from the other .csv master file..
    current_dir = os.getcwd()
    for epis in epi_list[0:3]:
        link_list = find_events_from_subject(subject, epis)
        # print("events list")
        # print(link_list)
        i = 1
        for links in link_list:
            key = epis + str(i) + '_mproc'
            download_a_link(links, get_target_dir(directory_dictionary[key]))
            # File name is last part of the link..
            tgz_file = links.split('/')[-1]
            os.chdir(get_target_dir(directory_dictionary[key]))
            tar = tarfile.open(tgz_file, 'r:gz')
            tar.extractall()
            for files in tar.getnames():
                if "events" in files:
                    break
            '''
		Move the "events" file to target directory
                files has the full path + filename, so splitting it and keeping
                the last part moves the filename into current directory...
            '''
            os.rename(files, files.split('/')[-1])
            tar.close()
            # Remove tgz_file and extracted directory...
            os.remove(tgz_file)
            # The first part of files is the top directory we want to remove
            shutil.rmtree(files.split('/')[0])
            os.chdir(current_dir)
            i += 1
