import os
from nda_aws_token_generator import *
import getpass
from ConfigParser import ConfigParser
def gen_token():
    web_service_url = 'https://ndar.nih.gov/DataManager/dataManager'
    #username  = input('Enter your NIMH Data Archives username:')
    #password  = getpass.getpass('Enter your NIMH Data Archives password:')

    generator = NDATokenGenerator(web_service_url)
    username='joakond'
    password='l0^eyoupooch'
    token = generator.generate_token(username, password)

    # Read .aws/credentials from the user's HOME directory, add a NDA profile, and update with credentials
    parser = ConfigParser()
    parser.read(os.path.expanduser('/home/kondylisjg/.aws/credentials'))

    if not parser.has_section('NDA'):
        parser.add_section('NDA')
    parser.set('default', 'aws_access_key_id', token.access_key)
    parser.set('default', 'aws_secret_access_key', token.secret_key)
    parser.set('default', 'aws_session_token', token.session)

    with open (os.path.expanduser('/home/kondylisjg/.aws/credentials'), 'wb') as configfile:
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

