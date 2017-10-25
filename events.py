from __future__ import unicode_literals

import json
import time
import urllib
from datetime import datetime, timedelta
from pycf.utils import get_redis_db, write_stdout
import pycf.event_callbacks as callbacks


CF_EVENT_TYPES = {
    'audit.service_instance.create': 0,
    'audit.service_instance.delete': 1,
    'audit.service_key.create': 2,
    'audit.service_key.delete': 3
}


def params_from_query_string(q):
    return {k: v for k, v in [param.split('=') for param in q.split('&')] if k != 'order-by'}


def collection_loop(cf, event_types, dbs, interval, key_expire_seconds):
    write_stdout("Starting events collection for event types {}...".format(', '.join(event_types)))
    while True:
        timestamp = datetime.utcnow() - timedelta(seconds=int(key_expire_seconds))  # cutoff time for listing events

        events_json = cf.events.list(
            params={
                'q': 'timestamp>{}'.format(datetime.strftime(timestamp, '%Y-%m-%dT%H:%M:%SZ'))
            },
        ).json()
        events_resources = events_json['resources']

        while events_json['next_url']:
            params = params_from_query_string(
                urllib.unquote(
                    events_json['next_url']
                ).split('?')[-1]
            )
            events_json = cf.events.list(params=params).json()
            events_resources.extend(events_json['resources'])

        write_stdout("Found {} total events!".format(str(len(events_resources))))
        for e in events_resources:
            write_stdout("Found event type '{}'".format(e['entity']['type']))
            if e['entity']['type'] in event_types:
                try:
                    if not dbs[e['entity']['type']].exists(e['metadata']['guid']):
                        write_stdout("EVENT RECEIVED: {}".format(str(e)))

                        dbs[e['entity']['type']].set(e['metadata']['guid'], json.dumps(e))
                        dbs[e['entity']['type']].expire(e['metadata']['guid'], key_expire_seconds)

                except Exception as e:
                    raise e

        time.sleep(float(interval))


def format_log_entry(**data):
    return '\t'.join(["{}:{}".format(k, v) for k, v in data.iteritems()])


def listen_loop(cf, event_type, db, callback, **callback_args):
    pubsub = db.pubsub()

    write_stdout('Listening for {} events ...'.format(event_type))
    pubsub.subscribe('__keyevent@{}__:set'.format(CF_EVENT_TYPES[event_type]))  # subscribe to keyevent events

    while True:
        event = pubsub.get_message()

        if event and event['type'] != 'subscribe':
            write_stdout('Received an event! ({})'.format(event['type']))
            write_stdout('Event key: {}'.format(event['data']))

            event_data = json.loads(db.get(event['data']))

            try:
                write_stdout(format_log_entry(**event_data))

            except Exception as e:
                write_stdout('{} raised!'.format(type(e).__name__))

            if callback:
                try:
                    getattr(callbacks, callback)(cf, event_data, **callback_args)

                except Exception as e:
                    write_stdout("WARNING: callback '{}' failed: {} raised! Message: {}".format(callback, type(e).__name__, e.message))

                else:
                    write_stdout("Callback '{}' succeeded!".format(callback))

        time.sleep(float(1))