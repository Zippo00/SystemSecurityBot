'''
Functions for remote use of Wazuh.
'''
import os
import json
import traceback
from datetime import datetime
from user_data import userdata


def get_logs(date):
    '''
    Get wazuh logs for given date from elasticsearch API. Return meaningful events as a list.

    :param date: (String) Date for which you want the logs for. Format: yyyy.mm.dd, for example "2023.03.14".
    :return events: (list) List of recorded events with security level higher than threshold. 
        Includes event description & timestamp. Also returns the total amount of logs analyzed 
        and total amount of events with security level higher than threshold.
    '''
    format = "%Y.%m.%d"
    datecheck = True
    try:
        datecheck = bool(datetime.strptime(date, format))
    except ValueError:
        return ["LOG DATA FROM USER'S SYSTEM: User's given date is not in correct format. They need to give the date as 'yyyy.mm.dd'"]
    scroll_count = 0
    read_big_data = {}
    events = []
    count = 0
    total_value = 0
    # Get log entries for given date through API &
    # save them into a dictionary
    command = f'curl -k -u {userdata.WAZUH_ACC}:{userdata.WAZUH_PASS} -X GET "https://{userdata.WAZUH_IP}{userdata.WAZUH_PORT}/wazuh-alerts-4.x-{date}/_search?pretty&size=10000&scroll=1m"'
    try:
        logdata = os.popen(command, 'r', 1)
        read_data = logdata.read()
        logdata.close()
        read_data = json.loads(read_data)
        read_big_data[str(scroll_count)] = read_data
        if read_data:
            total_value = read_data['hits']['total']['value']
            if int(read_data['hits']['total']['value']) == 10000:
                # If more than 10 000 log entries for given date,
                # make more API calls to get more
                while int(read_data['hits']['total']['value']) == 10000:
                    sid = read_data['_scroll_id']
                    scroll_count += 1
                    command = f'curl -k -u {userdata.WAZUH_ACC}:{userdata.WAZUH_PASS} -X GET "{userdata.WAZUH_IP}{userdata.WAZUH_PORT}/wazuh-alerts-4.x-{date}/_search?pretty&size=10000&scroll&scroll_id={sid}"'
                    logdata = os.popen(command, 'r', 1)
                    read_data = logdata.read()
                    logdata.close()
                    read_data = json.loads(read_data)
                    read_big_data[str(scroll_count)] = read_data
                    print("10 000 hits")
    # In the event of random error
    except Exception:
        traceback.print_exc()
        read_data = {}
    # If no log entries were recorded for given date
    if 'error' in read_data.keys():
    #print(read_data['error']['reason'])
        events.append("***LOG DATA FROM USER'S SYSTEM: No log events recorded for the given date.")
        return events

    else:
        if read_data:
            # Go through the log entries
            for key in read_big_data:
                for i in read_big_data[key]["hits"]["hits"]:
                    # If security level >= threshold, 
                    # append event description & timestamp into events list.
                    if int(i['_source']['rule']['level']) >= userdata.LEVEL_THRESHOLD:
                        count += 1
                        if not events:
                            events.append("LOG DATA: ")
                        events.append(scan_log(i))
            if not events:
                events.append("***LOG DATA FROM USER'S SYSTEM: No notable events recorded on given date. System is secure.")

        else:
            events.append("***LOG DATA: No log data available for given date.\n")
    logs_total = f"Analyzed {total_value} logs."
    meaningful_total = f"Found {count} records of meaningful log events.***"
    if not events:
        events.append("***LOG DATA FROM USER'S SYSTEM: No log events recorded for the given date.")
    events.append(logs_total)
    events.append(meaningful_total)
    return events

def scan_log(log):
    '''
    Extract certain information from a log given as input.

    :param log: (string) A log returned by ElasticSearch API.
    :return: (string) Compacted information from the given log.
    '''
    log_event = '*{LOG EVENT: '
    device_info = 'Device information: '
    try:
        # Get device IP, if possible
        device_ip = f"IP: {log['_source']['agent']['ip']}, "
        device_info += device_ip
    except KeyError:
        pass
    try:
        # Get agent name and id, if possible
        device_agent = f"Wazuh agent name {log['_source']['agent']['name']}, ID: {log['_source']['agent']['id']}"
        device_info += device_agent

    except KeyError:
        pass
    device_info += ", "
    log_event += device_info
    try:
        # Get full log message, if possible
        full_log = f"Full log: {log['_source']['full_log']},"
        log_event += full_log
    except KeyError:
        try:
            # Get event description, if possible
            log_description = "Description: " + f"{log['_source']['rule']['description']}, "
            log_event += log_description
        except KeyError:
            pass
        try:
            # Get event timestamp, if possible
            log_timestamp = "Timestamp: " f"{log['_source']['timestamp']}, "
            log_event += log_timestamp
        except KeyError:
            pass
    try:
        # Get mirte attack information if possible
        mitre_data = "Mitre attack technique:" + f"{log['_source']['rule']['mitre']['technique']}, mitre tactic: {log['_source']['rule']['mitre']['tactic']}, "
        log_event += mitre_data
    except KeyError:
        pass
    try:
        # Get security level, if possible
        event_level = "Level: " + f"{log['_source']['rule']['level']}"
        log_event += event_level
    except KeyError:
        pass
    
    log_event += "}*\n"
    return log_event


def ar_block_ip(IP_address):
    '''
    Block an IP address on all Windows and Linux Wazuh agents through Wazuh API.

    :param IP_address: (string) IP address to block on Windows & Linux agents.
    :return: (string) Message(s) received as response to API call.
    '''
    if not isinstance(IP_address, str):
        return "Parameter IP_address must be a string."
    error_message = ""
    # Get authentication token
    try:
        command = f'curl -u {userdata.AUTH_ACC}:{userdata.AUTH_PASS} -k -X GET "https://{userdata.WAZUH_IP}:55000/security/user/authenticate"'
        command_line = os.popen(command, 'r', 1)
        auth_token = command_line.read()
        command_line.close()
        auth_token = json.loads(auth_token)
        token = auth_token["data"]["token"]
    except Exception:
        return "Could not authenticate to Wazuh server. Check Wazuh Server IP and API Authentication credentials."

    # Block IP command for Windows agents
    try:
        command2 = f'curl -k -X PUT "https://{userdata.WAZUH_IP}:55000/active-response?wait_for_complete=true" -H "Authorization: Bearer {token}" ' + '-H "Content-Type: application/json" -d "{\\"command\\":\\"!netsh.exe\\",\\"alert\\":{\\"data\\":{\\"srcip\\":' + f'\\"{IP_address}\\"' +'}}}"'
        command_line = os.popen(command2, 'r')
        server_response = command_line.read()
        command_line.close()
        server_response = json.loads(server_response)
        #print(f"Windows server response: {server_response}")
        try:
            if server_response["data"]["failed_items"]:
                for item in server_response["data"]["failed_items"]:
                    error_message = "\n" + item["error"]["message"] + f'. Agent ID: {item["id"]}.'
            try:
                if server_response["data"]["affected_items"]:
                    for item in server_response["data"]["affected_items"]:
                        error_message += f"\nBlock IP command was sent succesfully to agent with ID: {item}"
            except KeyError:
                pass
        except KeyError:
            pass
        
        response_message = server_response["message"]
        if error_message:
            response_message += error_message

        message_to_AI = "\n" + response_message
    except Exception:
        traceback.print_exc()
        message_to_AI = "API Command to block IP address on Windows devices failed."
    # Block IP command for Linux agents
    try:
        command2 = f'curl -k -X PUT "https://{userdata.WAZUH_IP}:55000/active-response?wait_for_complete=true" -H "Authorization: Bearer {token}" ' + '-H "Content-Type: application/json" -d "{\\"command\\":\\"!firewall-drop\\",\\"alert\\":{\\"data\\":{\\"srcip\\":' + f'\\"{IP_address}\\"' +'}}}"'
        command_line = os.popen(command2, 'r')
        server_response2 = command_line.read()
        command_line.close()
        server_response2 = json.loads(server_response2)
        #print(f"Linux server response: {server_response2}")
        try:
            if server_response2["data"]["failed_items"]:
                for item in server_response2["data"]["failed_items"]:
                    error_message2 = "\n" + item["error"]["message"] + f'. Agent ID: {item["id"]}.'
            try:
                if server_response2["data"]["affected_items"]:
                    for item in server_response2["data"]["affected_items"]:
                        error_message2 += f"\nBlock IP command was sent succesfully to agent with ID: {item}"
            except KeyError:
                pass
        except KeyError:
            pass
        response_message2 = server_response2["message"]
        if error_message2:
            response_message2 += error_message2
        if response_message2 != response_message:
            message_to_AI += "\n" + response_message2
    except Exception:
        message_to_AI += " API Command to block IP address on Linux devices failed."
    #TODO: ADD COMMAND FOR MAC DEVICES*****************************************************************************************************
    message_to_AI = message_to_AI.replace("AR", "Block IP")
    message_to_AI = "***THIS IS WHAT HAPPENED WHEN YOU, ALICE, ATTEMPTED TO BLOCK THE IP ADDRESS: " + message_to_AI + "***"
    return message_to_AI


        


def ar_restart_agent(agent_id):
    '''
    Restart given Wazuh agent through Wazuh API.

    :param agent_id: (string) ID of the agent to restart.
    :return: (string) Message(s) received from response to API call.
    '''
    if not isinstance(agent_id, str):
        return "Parameter agent_id must be a string."
    error_message = ''
    response_message = ''
    response_message2 = ''
    error_message2 = ''
    # Get authentication token
    try:
        command = f'curl -u {userdata.AUTH_ACC}:{userdata.AUTH_PASS} -k -X GET "https://{userdata.WAZUH_IP}:55000/security/user/authenticate"'
        command_line = os.popen(command, 'r', 1)
        auth_token = command_line.read()
        command_line.close()
        auth_token = json.loads(auth_token)
        token = auth_token["data"]["token"]
    except Exception:
        return "Could not authenticate to Wazuh server. Check Wazuh server IP and API Authentication credentials."

    # Restart agent command for Windows
    try:
        command2 = f'curl -k -X PUT "https://{userdata.WAZUH_IP}:55000/active-response?agents_list={agent_id}&wait_for_complete=true" -H "Authorization: Bearer {token}" ' + '-H "Content-Type: application/json" -d "{\\"command\\":\\"restart-wazuh.exe\\"}"'
        command_line = os.popen(command2, 'r')
        server_response = command_line.read()
        command_line.close()
        server_response = json.loads(server_response)
        try:
            if server_response["data"]["failed_items"]:
                for item in server_response["data"]["failed_items"]:
                    error_message = "\n" + item["error"]["message"] + '. '
        except KeyError:
            pass
        if error_message:
            response_message = error_message
        response_message += "\n" + server_response["message"]
        #print(f"Windows response: {server_response}")
        response_message = response_message.replace("all agents", f'agent {agent_id}')
    except Exception:
        response_message = "\n**API Command to restart Wazuh agent on Windows device failed.**"

    # Restart agent command for Linux
    try:
        command2 = f'curl -k -X PUT "https://{userdata.WAZUH_IP}:55000/active-response?agents_list={agent_id}&wait_for_complete=true" -H "Authorization: Bearer {token}" ' + '-H "Content-Type: application/json" -d "{\\"command\\":\\"restart-wazuh\\"}"'
        command_line = os.popen(command2, 'r')
        server_response = command_line.read()
        command_line.close()
        server_response = json.loads(server_response)
        try:
            if server_response["data"]["failed_items"]:
                for item in server_response["data"]["failed_items"]:
                    error_message2 = "\n" + item["error"]["message"] + '. '
        except KeyError:
            pass
        if error_message2:
            response_message2 = error_message2
        #print(f"Linux response: {server_response}")
        response_message2 += "\n" + server_response["message"]
        response_message2 = response_message.replace("all agents", f'agent {agent_id}')
    except Exception:
        response_message += "\n**API Command to restart Wazuh agent on Linux device failed.**"
    if response_message != response_message2:
        message_to_AI = response_message + response_message2
    else:
        message_to_AI = response_message

    #TODO: ADD COMMAND FOR MAC DEVICES*****************************************************************************************************
    message_to_AI = message_to_AI.replace("all agents", f'agent {agent_id}')
    message_to_AI = message_to_AI.replace("AR", "Restart")
    return message_to_AI



# Get logs for given date
if __name__ == '__main__':
    #print(get_logs('2023.03.09'))
    print(ar_block_ip("102.164.61.121"))
    #print(ar_restart_agent("002"))
