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
        return ["LOG DATA: User's given date is not in correct format. They need to give the date as 'yyyy.mm.dd'"]
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
                    command = f'curl -k -u {userdata.WAZUH_ACC}:{userdata.WAZUH_PASS} -X GET \
                    "{userdata.WAZUH_IP}{userdata.WAZUH_PORT}/wazuh-alerts-4.x-{date}/_search?pretty&size=10000&scroll&scroll_id={sid}"'
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
        events.append("LOG DATA: No log events recorded for the given date.")
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
                        #events.append(f"\nLOG EVENT: Device information: [IP: {i['_source']['agent']['ip']}, Agent name: {i['_source']['agent']['name']}], Description: {i['_source']['rule']['description']}, Level: {i['_source']['rule']['level']}, Timestamp: {i['_source']['timestamp']}\n")
                        events.append(scan_log(i))
            if not events:
                events.append("LOG DATA: No notable events recorded on given date. System is secure.")

        else:
            events.append("No log data available for given date")
    logs_total = f"Analyzed {total_value} logs."
    meaningful_total = f"Found {count} records of meaningful log events."
    events.append(logs_total)
    events.append(meaningful_total)
    return events

def scan_log(log):
    '''
    Extract certain information from a log given as input.

    :param log: (string) A log returned by ElasticSearch API.
    :return: (string) Compacted information from the given log.
    '''
    log_event = '{LOG EVENT: '
    device_info = 'Device information: {'
    try:
        # Get device IP, if possible
        device_ip = f"IP: {log['_source']['agent']['ip']}, "
        device_info += device_ip
    except KeyError:
        pass
    try:
        # Get agent name, if possible
        device_agent = f"Wazuh agent name: {log['_source']['agent']['name']}"
        device_info += device_agent
    except KeyError:
        pass
    device_info += "}, "
    log_event += device_info
    try:
        # Get event description, if possible
        log_description = "Description: {" + f"{log['_source']['rule']['description']}" + "}, "
        log_event += log_description
    except KeyError:
        pass
    try:
        # Get security level, if possible
        event_level = "Level: {" + f"{log['_source']['rule']['level']}" + "}, "
        log_event += event_level
    except KeyError:
        pass
    try:
        # Get event timestamp, if possible
        log_timestamp = "Timestamp: {" f"{log['_source']['timestamp']}" + "}"
        log_event += log_timestamp
    except KeyError:
        pass
    log_event += "}\n"
    return log_event



# Get logs for given date
if __name__ == '__main__':
    test = get_logs('2023.03.16')
    print(test)
