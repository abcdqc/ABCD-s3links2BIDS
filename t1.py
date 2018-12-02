import os, shutil, fnmatch, argparse
import subprocess
from input_python_program import download_a_link

dcm2niidir = '/home/kondylisjg/temp/dcm2niix_3-Jan-2018_lnx'
dcm2niix = dcm2niidir+'/dcm2niix'
niidir = '/data/MBDU/ABCD/BIDS/NKI_script/rest'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to download a T1 link and tranlate from dcm to niix format..')
    parser.add_argument('--input_file', required=True, help='Link Input File')
    parser.add_argument('--line', type=int, default=0, help='Line to process')
    parser.add_argument('--t', default='T1', required=True, help='Generate T1 or T2')
    args = parser.parse_args()
    target = '/data/MBDU/ABCD/BIDS/NKI_script/Dicom/'+args.t

    with open(args.input_file, 'r') as f:
        for i, link in enumerate(f):
            if i == args.line:
                link = link.strip()
                break
            else:
                link = None
    if link is None:
        print("No link found exiting\n")
        exit(0)

    download_a_link(link, target)
    tgz_file = link.split('/')[-1]
    subject = tgz_file[0:15]
    sub_subject = 'sub-'+subject
    os.chdir(target)
    try:
        subprocess.check_call(['/usr/bin/tar', '-xvzf', tgz_file])
    except:
        print ("Error! Cannot untar file %s" % tgz_file)
        subprocess.check_call(['/bin/rm', '-rf', tgz_file])
        exit(1)
    subprocess.check_call(['/bin/rm', '-rf', tgz_file])

    # Directory where processed files go
    if not os.path.exists(niidir + '/' + sub_subject):
        os.makedirs(niidir + '/' + sub_subject + '/ses-1/anat')

    # cd to the un-tarred directory and run dcm2niix
    os.chdir(target+'/'+sub_subject+'/ses-baselineYear1Arm1/anat')
    for files in os.listdir('.'):
        if files.endswith('.json'):
            continue
        try:
            subprocess.check_call([dcm2niix, '-o', niidir+'/'+sub_subject, '-f', subject+'_%f_%p', target+'/'+sub_subject+'/ses-baselineYear1Arm1/anat/'+files])
        except:
            print ("Error...running dcm2niix on subject %s\n" % subject)
            shutil.rmtree(target+'/'+sub_subject)
            shutil.rmtree(niidir+'/'+sub_subject)
            exit(1)
        os.chdir(niidir+'/'+sub_subject)
        for files in os.listdir('.'):
            if os.path.isdir(files):
                continue
            _, ext = os.path.splitext(files)
            os.rename(files, 'ses-1/anat/'+sub_subject+'_ses-1_run-1_'+args.t+'w'+ext)
        break
    shutil.rmtree(target+'/'+sub_subject)
