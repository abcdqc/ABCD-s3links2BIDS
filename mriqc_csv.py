import argparse
import os
import csv
import subprocess

mriqc_html_dir = '/data/ABCD_DSST/bids_20190215/derivatives/mriqc'

# Create the first row of the CSV wit
first_row = ['subjeckey', 'aqi', 'dvars_nstd', 'fd_mean', 'fd_num', 'fd_perc', 'snr', 'tsnr', 'aor']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to transfer MRIQC results to an xcel sheet')
    parser.add_argument('--task', required=True, help='Task including run')
    args = parser.parse_args()

    # Start constructing each line of the CSV file...
    mriqc_csv = args.task + '_mriqc.csv'
    with open(mriqc_csv, 'w') as wf:
        writer = csv.writer(wf, delimiter=',')
        writer.writerow(first_row)
        current_dir = os.getcwd()
        os.chdir(mriqc_html_dir)
        for dirs in os.listdir('.'):
            if not os.path.isdir(dirs):
                continue
            subject = dirs.strip('sub-')
            row = [subject]
            if not os.path.isdir(dirs + '/ses-1/func'):
                continue
            for jsons in os.listdir(dirs + '/ses-1/func'):
                if args.task in jsons and jsons.endswith('.json'):
                    json_dir = dirs + '/ses-1/func/' + jsons
                    for iqms in first_row[1:]:
                        iqm_value = subprocess.check_output(['jq', '.' + iqms, json_dir])
                        if iqm_value.strip() == 'null':
                            row.append('NA')
                        else:
                            row.append(float(iqm_value.strip()))
                    writer.writerow(row)
        os.chdir(current_dir)
