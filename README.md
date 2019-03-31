# ABCD-s3links2BIDS
This repository includes a set of python scripts that download raw format and minimally processed MRI files (s3 links) from the Adolescent Brain Cognitive Development study (ABCD) database and translates them to the BIDS format.
# Get Started:
Prerequisites for the download_raw.py script:
- Follow the NDAR tutorials (https://data-archive.nimh.nih.gov/training/training-modules) under the "Accessing files in the cloud" section. The information is also summarized below. It is tailored for this specific purpose (i.e. the ABCD study).
  - First you have to use the query tools to add a filter to your cart for download. Then, clicking Download/Add to Study will take you to a landing page. This is a page where you can view the data you currently have returned by your query. You can make various selections to specify which data you would like to utilize. For this purpose, no extra selections were made.
  - Once your selections are made, you can click Create Package to name and begin creating your download package.
  - Once your package is created, you can launch a miNDAR. A miNDAR is a NDA-hosted Oracle database in the AWS cloud. Deploying your package to the miNDAR will help form each measure into a table. You can then connect to the database using NDA credentials and Oracle's SQLDeveloper.
