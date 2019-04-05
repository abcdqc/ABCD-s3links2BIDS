# ABCD-s3links2BIDS

# Purpose
This repository includes a set of python scripts that download raw format and minimally processed MRI files from the Adolescent Brain Cognitive Development study (ABCD) database and converts them to BIDS format. These scripts can download both the annual release data (preprocessed with event files) and raw fast track data.

# Requirements To Get Started
1. DATA: ABCD data are available to researchers for legitimate research purposes upon request and application. 
Instructions for access are here (valid as of 4/2/2019): https://data-archive.nimh.nih.gov/abcd 
2. SQLDEVELOPER: Download assistance is provided by Oracle's SQLDeveloper. Register for a (free) Oracle account and download SQLDeveloper here (as of 4/2/2019): https://www.oracle.com/technetwork/developer-tools/sql-developer/downloads/index.html
3. AWS: Amazon Web Service (AWS) command line interface tool will assist with S3link download. Install this tool from the AWS website (valid as of 4/2/2019): https://aws.amazon.com/cli/ 
4. DCM2NIIX: Install with conda, instructions found here (valid 4/2/2019): https://github.com/rordenlab/dcm2niix
5. JQ: Command line JSON processor, found here (valid 4/2/2019): https://stedolan.github.io/jq/
For those working on the NIH Biowulf server, jq is already installed ("module load jq"). For more information about the formating of json files for BIDS format please see this pdf: https://bids.neuroimaging.io/bids_spec.pdf.

# Create Download Package 
For more detailed instructions of creating the download package, follow the NDAR tutorials (availabe here as of 4/2/2019: https://data-archive.nimh.nih.gov/training/training-modules) under the "Accessing files in the cloud" section. Use the query tools to add a filter to your cart for download. Click Download/Add to Study and review the data returned by the query. There are options to specify data sub-groupings; for the abcdqc project, all available data were included. Click "Create Package" to name and create your download package.

# Launch miNDAR
Once your package is created, you can launch a miNDAR (you will then recieve an email specifying package's connection details). A miNDAR is a NDA-hosted Oracle database in the Amazon Web Service (AWS) cloud. Deploying your package to the miNDAR will form a table. Connect to the database using NDA credentials and Oracle's SQLDeveloper. 

Open SQLDeveloper and create a new connection. Connection set up requires a Connection Name, Username, Password and Hostname. The username and hostname are specified on the package's page or the email you received. The password should be the password you created when you created your package. Select ServiceName instead of SID and input ORCL. The port should be 1521. Test the connection. If it succeeds, save it.

Use the export bar at the top of the SQLDeveloper page to export the datatables to csv files. fmriresults01 (annual release data) and image03 (fast track data) are the relevant tables.

# Set up s3links to download 
Raw and processed associated files are all in Amazon’s S3 object-based storage and can be accessed through s3links. fmriresults01 and image03 csv tables contain the s3links. 

Use get_token_example.py , found on this GitHub page, to automatically generate temporary AWS credentials. Input your own NDA username and password and edit with the correct file path. AWS credential keys expire after 24hrs, but can be renewed. 

 # download_raw.py
This file downloads all of the raw data for all subjects, runs, etc., credentials are generated externally (outside of the swarm).

# do_dcm.py 
Run after download_raw.py script, it opens the raw and pre-processed .tgz files, uses DCM2NIIX to convert the raw dicoms to nii files, and then places the data in the Brain Imaging Data Structure (BIDS).
