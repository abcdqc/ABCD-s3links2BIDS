# This script generates temporary AWS credentials and updates the AWS credentials file.
# Once a connection with AWS has been established, s3 links for the ABCD database can be downloaded.
import os
from nda_aws_token_generator import *
import getpass
from ConfigParser import ConfigParser
def gen_token():
    web_service_url = 'https://ndar.nih.gov/DataManager/dataManager'

    generator = NDATokenGenerator(web_service_url)
    username='inset username here'
    password='inset password here'
    token = generator.generate_token(username, password)

    # Read .aws/credentials from the user's HOME directory, add a NDA profile, and update with credentials
    parser = ConfigParser()
    parser.read(os.path.expanduser('/insert/path/to/.aws/credentials'))

    if not parser.has_section('NDA'):
        parser.add_section('NDA')
    parser.set('default', 'aws_access_key_id', token.access_key)
    parser.set('default', 'aws_secret_access_key', token.secret_key)
    parser.set('default', 'aws_session_token', token.session)

    with open (os.path.expanduser('/insert/path/to/.aws/credentials'), 'wb') as configfile:
        parser.write(configfile)
    '''
    print('aws_access_key_id=%s\n'
        'aws_secret_access_key=%s\n'
        'security_token=%s\n'
        'expiration=%s\n'
        %(token.access_key,
            token.secret_key,
            token.session,
            token.expiration)
        )
    '''

