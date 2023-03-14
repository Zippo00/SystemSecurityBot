import os
import json
import traceback
from user_data import userdata


def get_logs(date):
    '''
    Get wazuh logs for given date from elasticsearch API

    :param date: (String) Date for which you want the logs for. Format: yyyy.mm.dd, for example "2023.03.14"
    :return events: (list) List of recorded events with security level higher than threshold. Includes event description & timestamp
    :return logs_total: (String) String that indicates how many logs were analyzed in total
    :return meaningful_total: (String) String that indicates how many logs were analyzed with security level higher than theshold.
    '''
    scroll_count = 0
    read_big_data = {}
    events = []
    count = 0
    total_value = 0
    # Get log entries for given date through API &
    # save them into a dictionary
    command = f'curl -k -u {userdata.WAZUH_ACC}:{userdata.WAZUH_PASS} -X GET \
    "{userdata.WAZUH_IP}{userdata.WAZUH_PORT}/wazuh-alerts-4.x-{date}/_search?pretty&size=10000&scroll=1m"'
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
        events.append("No log events recorded for the given date.")

    else:
        if read_data:
            # Go through the log entries
            for key in read_big_data:
                for i in read_big_data[key]["hits"]["hits"]:
                    # If security level >= threshold, 
                    # append event description & timestamp into events list.
                    if int(i['_source']['rule']['level']) >= userdata.LEVEL_THRESHOLD:
                        count += 1
                        events.append(f"LOG EVENT: Description: {i['_source']['rule']['description']},\
                        Level: {i['_source']['rule']['level']}, \
                        Timestamp: {i['_source']['timestamp']}\n")
            if not events:
                events.append("No notable events recorded on given date. System is secure.")

        else:
            events.append("No log data available for given date")
    logs_total = f"Analyzed {total_value} logs."
    meaningful_total = f"Found {count} records of meaningful log events."

    return events, logs_total, meaningful_total



# Get logs for given date
teste, testl, testm = get_logs('2023.03.14')
print(teste, testl, testm)
