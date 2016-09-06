import ucwa.actions as actions
from ucwa.config import load_config
from ucwa.events import process_events

from contextlib import closing
import time
import yaml

import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


with open('instance.yml', 'r') as instance_f:
    instance_config = yaml.load(instance_f)

config = load_config()

resource = instance_config['resource']
token = instance_config['token']

logging.info('registering application against UCWA api')
app = actions.register_application(resource, token, config)

logging.info('Registered app %s' % app['id'])
logging.info('listening for events')

event_url = resource + app['_links']['events']['href']
logging.info('setting status to available')

available = actions.set_available(resource, app['id'], token, config)

events_stream = actions.oauth_stream_request(event_url, token, config['redirect_uri'])

event_list = {}

while True:
    with closing(events_stream) as r:
        # Do things with the response here.
        event_response = events_stream.json()
    time.sleep(1)

    # get communication events
    comm_evt = [e for e in event_response['sender'] if e['rel'] == 'communication']

    if len(comm_evt) > 0:
        event_list = comm_evt[0]['events']
        process_events(event_list, resource, token, config)

    events_stream = actions.oauth_stream_request(
        resource + event_response['_links']['next']['href'],
        token,
        config['redirect_uri'])
