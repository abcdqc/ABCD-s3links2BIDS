# ABCD-s3links2BIDS
This repository includes a set of python scripts that download raw format and minimally processed MRI files (s3 links) from the Adolescent Brain Cognitive Development study (ABCD) database and translates them to the BIDS format.
# Get Started:
Prerequisites for the download_raw.py script:
- Follow the NDAR tutorials (https://data-archive.nimh.nih.gov/training/training-modules) under the "Accessing files in the cloud" section. The information is also summarized below. It is tailored for this specific purpose (i.e. the ABCD study). You will want to download both the Annual Release Data (this is the pre-processed data that has the event files for the subjects) and the Fast Track Data (this is the purely raw data) from the ABCD dataset.
  - First you have to use the query tools to add a filter to your cart for download. Then, clicking Download/Add to Study will take you to a landing page. This is a page where you can view the data you currently have returned by your query. You can make various selections to specify which data you would like to utilize. For this purpose, no extra selections were made.
  - Once your selections are made, you can click Create Package to name and begin creating your download package.
  - Once your package is created, you can launch a miNDAR (you will then recieve an email specifying package's connection details). A miNDAR is a NDA-hosted Oracle database in the AWS cloud. Deploying your package to the miNDAR will help form each measure into a table. You can then connect to the database using NDA credentials and Oracle's SQLDeveloper. To download SQLDeveloper, you will need to register for an Oracle account.
  - Launch SQLDeveloper. Then use SQLDeveloper to make a new connection. In creating the connection, SQLDeveloper will need a Connection Name, a Username, a Password, a Hostname. The username should be the one specified on the package's page or the email you received. The password should be the password you created when you created your package. The hostname is also specified in the connection details on the package's page. Select ServiceName instead of SID and input ORCL. The port should be 1521. Test the connection. If it succeeds, save it.
  
