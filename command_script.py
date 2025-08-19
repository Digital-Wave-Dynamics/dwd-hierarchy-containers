import os
import debugpy
import sys
import platform
import json
import argparse
from waapi import WaapiClient, CannotConnectToWaapiException

#9E1B41BF-6671-49D2-A9F1-9573E58871B8

# Arguments
parser = argparse.ArgumentParser(description="Digital Wave Dynamics Hierarchy Container script")
parser.add_argument("-i", "--instruction", help="The operation to be performed by the script")
parser.add_argument("-id", help="The id that represents the root object for the hierarchy")
parser.add_argument("-name", help="The id that represents the name of the template")
parser.add_argument("-u", "--user", help="Whether or not the container was created by the user", action="store_true")

args = parser.parse_args()
print(args)

instruction = args.instruction
if instruction == None:
    instruction = "create"
head_object_id = args.id
container_name = args.name
container_owner = args.user

# recursive function for retrieving children
def get_object_info(head_object_id, wappi_client):  
    waql_query = f'$ from object "{head_object_id}"'
    args = {"waql" : waql_query}
    options = { "return": ["name", "type", "notes"]}
    result = wappi_client.call("ak.wwise.core.object.get", args, options=options)
    if result == None:
        print("Result returned as None. Cannot continue")
        exit(1)
    
    object = {
            "name" : result["return"][0]["name"],
            "type" : result["return"][0]["type"],
            "notes": result["return"][0]["notes"],
            "children" : []
        }
    print(object)
    result = waql_query = f'$ from object "{head_object_id}" select children'
    args = {"waql" : waql_query}
    options = { "return": ["id", "name", "type", "notes"]}
    result = wappi_client.call("ak.wwise.core.object.get", args, options=options)
    for descendant in result["return"]:
        if descendant["type"] == "Sound":
            continue
        child = get_object_info(descendant["id"], wappi_client)
        object["children"].append(child)
        
    return object
        
#recursive function for adding the children
def create_object_with_info(head_object, parent_object_id, json_data, waapi_client):
    object = None
    return object

print("HelloWorld!")

# Write to a log on non-windows machines. Command will route to the Wwise Log on Windows
if platform.system() != 'Windows':
    log_file = open("dwd_command.log", "w")
    sys.stdout = log_file
    sys.stderr = log_file
    
# Make sure we're in the right place
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

commands_filepath = 'commands.json'                             
user_containers_dir = 'containers'

# Commands
if instruction == "create":
    #recursively assemble the tree from the root object
    try:
        client = WaapiClient()
    except CannotConnectToWaapiException:
        print("Couldn't connect to WAAPI. Terminating program")
        exit()
    print(head_object_id)
    head_object = get_object_info(head_object_id, client)
    print(head_object)

    with open(f"containers\\user_{head_object["name"]}.json", 'w') as user_containers_file:
            json.dump(head_object, user_containers_file, indent=4)
    
    # Assemble new commands 
    command_id_child = f"user.insert.{ ''.join(head_object["name"].split()) }.child"     # Command ID used for when the hierarchy is inserted as a child object
    command_id_parent = f"user.insert.{ ''.join(head_object["name"].split()) }.parent"   # Command ID used for when the hierarchy is inserted as a parent object
    command_display_name = head_object["name"] # Leave white space for the name as presented in Wwise
    command_program = "python"
    command_startUpMode = "SingleSelectionSingleProcess"
    command_arguments = f"\"${{CurrentCommandDirectory}}\\DigitalWaveDynamics\\dwd-hierarchy-containers\\command_script.py\" -i insert -name {head_object["name"]} -id ${{id}} --user"
    command_redirectOutputs = True
    command_contextMenu_NewChild = {
                "basePath": "DigitalWaveDynamics/New Child",
                "enabledFor": "WorkUnit,ActorMixer,SwitchContainer,RandomSequenceContainer, BlendContainer, MusicSwitchContainer, MusicPlaylistContainer"
            }
    command_contextMenu_NewParent = {
                "basePath": "DigitalWaveDynamics/New Parent",
                "enabledFor": "ActorMixer,SwitchContainer,RandomSequenceContainer, BlendContainer, MusicSwitchContainer, MusicPlaylistContainer,Sound"
            }

    newcommand_child = {
        "id" : command_id_child,
        "displayName" : command_display_name,
        "program": command_program,
        "startMode" : command_startUpMode,
        "args" : command_arguments,
        "cwd" : "",
        "redirectOutputs" : command_redirectOutputs,
        "contextMenu" : command_contextMenu_NewChild
    }
    
    newcommand_parent = {
        "id" : command_id_parent,
        "displayName" : command_display_name,
        "program": command_program,
        "startMode" : command_startUpMode,
        "args" : command_arguments,
        "cwd" : "",
        "redirectOutputs" : command_redirectOutputs,
        "contextMenu" : command_contextMenu_NewParent
    }
    
    with open(commands_filepath, 'r') as command_file:
        json_data = json.load(command_file)
    
    found_child = next((command for command in json_data["commands"] if command.get("id") == command_id_child), None)
    if not found_child:
        json_data["commands"].append(newcommand_child)
        with open(commands_filepath, 'w') as command_file:
            json.dump(json_data, command_file, indent=4)
    
    found_parent = next((command for command in json_data["commands"] if command.get("id") == command_id_parent), None)
    if not found_parent:
        json_data["commands"].append(newcommand_parent)
        with open(commands_filepath, 'w') as command_file:
            json.dump(json_data, command_file, indent=4)
    
    args = { "command": "ReloadCommandAddons"}
    client.call("ak.wwise.ui.commands.execute", args)

    print ("Digital Wave Dynamics - Hierarchy Container Command/Script ran successfully!")
    if platform.system() != 'Windows':
        log_file.close()
    
if instruction == "insert":
    if container_name == None:
        print("Insert command provided without container name")
        exit()
        
    #recursively assemble the tree from the root object
    try:
        client = WaapiClient()
    except CannotConnectToWaapiException:
        print("Couldn't connect to WAAPI. Terminating program")
        exit()
        
    if container_owner:
        try:
            with open(f"containers\\user_{container_name}.json", "r") as container_file:
                container_json = json.load(container_file)
                waapi_args = {
                    "name" : container_json['name'], 
                    "type": container_json['type'], 
                    "notes" : container_json['notes'],
                    "parent" : head_object_id,
                    "children" : container_json['children']
                    }
                waapi_command = "ak.wwise.core.object.create"
                client.call(waapi_command, waapi_args)
        except FileNotFoundError:
            print("Error: The file does not exist.")
            exit()
        
if platform.system() != 'Windows':
    log_file.close()
        
client.disconnect()
