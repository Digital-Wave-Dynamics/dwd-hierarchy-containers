from waapi import WaapiClient, CannotConnectToWaapiException
from pprint import pprint
import sys

# Testing values
#  '{6A980152-785A-4303-B16B-18FE2B343E33}', 
#  'New Actor-Mixer', 
#  'I am a note!', 
#  'ActorMixer']

# WAAPI

id = '{6A980152-785A-4303-B16B-18FE2B343E33}'
# Get ID from command argument list
# head_object_id = sys.argv[1]
# head_object_name = sys.argv[2]
# head_object_note = sys.argv[3]

try:
    # Connect to WAAPI
    with WaapiClient() as client:

        waql_query = f'$ from object "{id}" select descendants'
        args = {"waql" : waql_query}
        options = { "return": ["name", "type"]}
        result = client.call("ak.wwise.core.object.get", args, options=options)
        pprint(result)
except CannotConnectToWaapiException:
    print("Could not connect to WAAPI")

print ("Digital Wave Dynamics - Hierarchy Container Command/Script ran successfully!")