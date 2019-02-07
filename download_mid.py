import os, subprocess
import shutil


niidir = '/data/MBDU/ABCD/BIDS/NKI_script/MID/'
raw_location = '/data/MBDU/ABCDraw'

dcm2niidir = '/home/kondylisjg/temp/dcm2niix_3-Jan-2018_lnx'
dcm2niix = dcm2niidir + '/dcm2niix'

def gen_directories(subject):
    os.makedirs(niidir + '/sub-' + subject + '/ses-1/func')
    os.mkdir(niidir + '/sub-' + subject + '/ses-1/anat')
    os.mkdir(niidir + '/sub-' + subject + '/ses-1/rest')
    os.mkdir(niidir + '/sub-' + subject + '/tmp')
    os.mkdir(niidir + '/sub-' + subject + '/tmp/niix')


def get_niix_directory(subject, epi):
    if epi == "MID" or epi == "NBack" or epi == "SST":
        return niidir + '/sub-' + subject + '/ses-1/func'
    elif epi == "T1" or epi == "T2":
        return niidir + '/sub-' + subject + '/ses-1/anat'
    elif epi == "Rest":
        return niidir + '/sub-' + subject + '/ses-1/rest'
    else:
        print ("ERROR for niix directory!! wrong epi: %s" % epi)


def copy_events(subject, epi, run):
    this_run = '_Run'+str(run)+'_'
    source = raw_location + '/' + epi + this_run + 'events/'
    if not os.path.isdir(source):
        return
    event_file = [f for f in os.listdir(source) if subject in f]
    if not event_file:
        return
    output_dir = get_niix_directory(subject, epi)
    shutil.copy2(source + event_file[0], output_dir)

def call_dcm2niix(subject, epi, run):
    target = niidir + '/sub-' + subject + '/tmp'
    curr_dir = os.getcwd()
    if epi == "T":
        epi += str(run)
        source = raw_location + '/' + epi
        tar_ext = 'anat'
    else:
        this_run = '_Run'+str(run)+'_'
        source = raw_location + '/' + epi + this_run + 'EPI'
        tar_ext = 'func'
    if not os.path.isdir(source):
        return

    # Untar files..
    tgz_file = [f for f in os.listdir(source) if subject in f]
    if not tgz_file:
        return
    subprocess.check_call(['/usr/bin/tar', '-xvzf', source + '/' + tgz_file[0], '-C', target])
    # Source of dcm2niix is target of untar, place nii files in new target
    source = target + '/sub-' + subject + '/ses-baselineYear1Arm1/' + tar_ext
    subprocess.check_call([dcm2niix, '-o', target + '/niix', '-f', subject + '_func_%p', source])
    # Remove raw files
    shutil.rmtree(target + '/sub-' + subject)
    # Rename files
    os.chdir(target + '/niix')
    output_dir = get_niix_directory(subject, epi)
    for files in os.listdir('.'):
        _, ext = os.path.splitext(files)
        if epi != "T1" and epi != "T2":
            os.rename(files,
                      output_dir + '/sub-' + subject + '_ses-1_task-'+epi.lower()+'_run-'+str(run)+'_bold' + ext)
        else:
            os.rename(files,
                      output_dir + '/sub-' + subject + '_ses-1_' + epi + 'w' + ext)
    # Switch back to original directory
    os.chdir(curr_dir)


def json_fixup(json_file, ap):
    '''
    jq '. |= . + {"PhaseEncodingDirection": "j"}'
    NDARINV2HYAENE6_ABCD - fMRI - FM - PA_run - 20161121131802
    _WIP_MB2_fMRI_Fieldmap_P.json > temp.json
    '''
    if ap == "AP":
        subprocess.check_call(['jq', ])
    pass


# subject = "NDAR_INV007W6H7B"
# Siemens:
# subject = "NDARINVPKD1XX0E"
subject = "NDARINVPNUJ3TUX"
# subject = "NDAR_INVUGKWA479"
# GE:
# subject = "NDAR_INV0191C80U"
epis = ['MID', 'NBack', 'SST', 'Rest', 'T']


if __name__ == '__main__':
    gen_directories(subject)
    for epi in epis:
        for run in range(1, 5):
            call_dcm2niix(subject, epi, run)
            copy_events(subject, epi, run)
