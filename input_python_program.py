# This script downloads the processed and raw MID s3 links. The processed files contain information about run type
# (run 1 or run 2) while the raw files contain the dicoms. The script downloads the raw and processed links
# into a single folder and then completes dcm2niix. Finally, the script places the generated nii and json files into BIDS
# format along with the events file (from the processed links).
# This script can be altered to process SST, nBACK, and rest links.
import os, shutil, fnmatch, argparse
import re, subprocess
import time

''' Downloads link using aws
    Sometimes downloads fail, hence try up to 5 times...
'''
def download_a_link(link, target):
    program = '/home/kondylisjg/conda/envs/BIDS/bin/aws'
    done = False
    for i in range(5):
        try:
            subprocess.check_call([program, 's3', 'cp', link, target])
            done = True
        except:
            print("Error! attempt %u: link %s could not be downloaded\n" % (i, link))
        if done:
            break
        else:
            time.sleep(30)
    return done

def rename_files(filelist):
    print("entering rename_files from: %s" % os.getcwd())
    dirname = filelist[0][0:15]
    os.mkdir(dirname)
    for f in filelist:
        os.rename(f, dirname+'/'+f)


def dcm2niix_one_run(dcm2niix, dcmdir, niidir, subj_id, run):
    # Regenerate file names (remove "sub" prefix)
    sub_0_15 = subj_id[4:]
    new_name = sub_0_15+'-'+run
    os.chdir(dcmdir + 'MID/' + new_name + '/' + subj_id + '/ses-baselineYear1Arm1/func')
    for materials2 in os.listdir('.'):
        filename = subj_id + '_ses-baselineYear1Arm1_task-mid_run-0'+run+'_events.tsv'
        if os.path.isfile(filename):
            target_filename = niidir + subj_id + '/ses-1/func/' + subj_id + '_ses-1_task-mid_run-'+run+'_events.tsv'
            print("one_run renaming %s to %s" % (filename, target_filename))
            os.rename(filename, target_filename)
                      
        if materials2.endswith('.json') or materials2.endswith('.txt') or \
                materials2.startswith('.D') or materials2.endswith('.nii') or \
                materials2.endswith('.tsv'):
            continue
        dcmstring = dcm2niix + ' -o ' + niidir + subj_id + ' -f ' + sub_0_15 + '_func_%p ' + dcmdir + 'MID/' + new_name + '/' + subj_id + '/ses-baselineYear1Arm1/func/' + materials2
        os.system(dcmstring)
        os.chdir(niidir + subj_id)
        for renamingfiles in os.listdir('.'):
            if renamingfiles.endswith('ses-1'):
                continue
            _, ext = os.path.splitext(renamingfiles)
            os.rename(renamingfiles, 'ses-1/func/' + subj_id + '_ses-1_task-mid_run-'+run+'_bold' + ext)
    '''
    os.chdir(dcmdir + 'MID/' + new_name + '/' + subj_id + '/ses-baselineYear1Arm1/func')
    for filezip in os.listdir('.'):
        if filezip.startswith('.D'):
            continue
        if filezip.endswith('.txt') or filezip.endswith('.tsv') or filezip.endswith('.nii') \
           or filezip.endswith('.json') or filezip.endswith('.csv'):
            os.remove(filezip)
        else:
            os.system('tar -cvzf ' + filezip + '.tgz' + ' ' + dcmdir + 'MID/' + new_name + '/' + subj_id + '/ses-baselineYear1Arm1/func/' + filezip)
            shutil.rmtree(filezip)
    '''

def dmc2niix_one_subject(target, dcm2niix, dcmdir, niidir, filelist):
    print ("Entering dcm2niix_one_subject from directory: %s" % os.getcwd())
    os.chdir(target)
    rename = filelist[0][0:15]
    os.makedirs(niidir + 'sub-' + rename + '/ses-1/' + 'func')
    os.mkdir(niidir + 'sub-' + rename + '/ses-1/' + 'anat')
    while filelist:
        os.chdir(target)
        first_file = filelist[0]
        last18 = first_file[-18:]
        for next_file in filelist:
            if first_file == next_file:
                continue
            if last18 == next_file[-18:]:
                break
        pair_of_files = [first_file, next_file]
        print("first_file: %s next_file: %s" % (first_file, next_file))
        rename_files(pair_of_files)
        sub_0_15 = pair_of_files[0][0:15]
        os.chdir(sub_0_15)
        for f in os.listdir("."):
            os_string = '/usr/bin/tar -xvzf ' + f
            os.system(os_string)
            os.remove(f)
        sub_0_15_str = ''.join(sub_0_15)
        subj_id = "sub-" + sub_0_15
        baseline = "ses-baselineYear1Arm1"
        os.chdir(subj_id)
        os.chdir(baseline)
        os.chdir("func")
        # Scan the files in the directory in search for the run..
        run = -1
        for filename in os.listdir('.'):
            print("Searching for run in file %s in directory %s\n" % (filename, os.getcwd()))
            if os.path.isfile(filename):
                if fnmatch.fnmatch(filename, '*_run-02_*'):
                    run = '2'
                    break
                elif fnmatch.fnmatch(filename, '*_run-01_*'):
                    run = '1'
                    break
        if run == -1:
            print ("Error!! could not find run 1 or 2 in directory: %s" % os.getcwd())
            exit(1)
        os.chdir("../../../../")
        new_name = sub_0_15_str + '-' + run
        print ("sub_0_15: %s, new_name: %s\n" % (sub_0_15, new_name))
        os.rename(sub_0_15, new_name)
        dcm2niix_one_run(dcm2niix, dcmdir, niidir, subj_id, run)
        filelist.remove(first_file)
        filelist.remove(next_file)
        if os.path.isdir(target + '/' + rename + '-1'):
            shutil.rmtree(target + '/' +  rename + '-1')
        if os.path.isdir(target + '/' + rename + '-2'):
            shutil.rmtree(target + '/' + rename + '-2')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to unzip an xxx file and tranlate from dcm to niix format..')
    parser.add_argument('--input_file1', required=True, help='First input file')
    parser.add_argument('--input_file2', required=True, help='Second input file')
    parser.add_argument('--line', type=int, default=0, help='Line to process, this one plus the next..')

    args = parser.parse_args()

    toplvl = '/data/MBDU/ABCD/BIDS/NKI_script'
    dcmdir = '/data/MBDU/ABCD/BIDS/NKI_script/Dicom/'
    dcm2niidir = '/home/kondylisjg/temp/dcm2niix_3-Jan-2018_lnx'
    target = '/data/MBDU/ABCD/BIDS/NKI_script/Dicom/MID'

#    niidir = '/data/MBDU/ABCD/BIDS/NKI_script/Nifti/'
    niidir = '/data/MBDU/ABCD/BIDS/NKI_script/MID/'
    dcm2niix = dcm2niidir + '/dcm2niix'

    zipped_file_list = []
    with open(args.input_file1, 'r') as f:
        for i, link in enumerate(f):
            if i == args.line or i == args.line + 1:
                link = link.strip()
                subject = link.split('/')[-1][0:15]
                print ("About to download subject %s\n" % subject)
                if os.path.isdir(niidir+'sub-'+subject):
                    print ("Subject exists bailing\n")
                    exit(0)
                if not download_a_link(link, target):
                    exit(1)
                zipped_file_list.append(link.split('/')[-1])
    with open(args.input_file2, 'r') as f:
        for i, link in enumerate(f):
            if i == args.line or i == args.line + 1:
                link = link.strip()
                if not download_a_link(link, target):
                    exit(1)
                zipped_file_list.append(link.split('/')[-1])
    if len(zipped_file_list) == 4:
        dmc2niix_one_subject(target, dcm2niix, dcmdir, niidir, zipped_file_list)
    
    # Patch the .json files..
    os.chdir(niidir+'sub-'+subject+'/ses-1/func')
    for jsons in os.listdir('.'):
        if not jsons.endswith('.json'):
            continue
        cat = subprocess.Popen(('cat', jsons), stdout = subprocess.PIPE)
        output = subprocess.check_output(('jq', '.TaskName'), stdin = cat.stdout)
        if output.strip() == 'null':
            ses = re.search('ses', jsons).start() + 4
            oneortwo = jsons[ses] #square brackets for a string
            os.system('jq \'. |= . + {"TaskName": \"\'' + oneortwo + '\'\"}\' ' + jsons + ' > temp.json')
            os.remove(jsons)
            os.rename('temp.json', jsons)

    # Remove original downloads
    for files in os.listdir(target):
        if fnmatch.fnmatch(files, subject+'*'):
            shutil.rmtree(target+'/'+files)
