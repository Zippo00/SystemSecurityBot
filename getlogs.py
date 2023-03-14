import os
import json
from user_data import userdata

date = '2023.02.25'
command = f'curl -k -u {userdata.WAZUH_ACC}:{userdata.WAZUH_PASS} -X GET "{userdata.WAZUH_IP}{userdata.WAZUH_PORT}/wazuh-alerts-4.x-{date}/_search?pretty&size=10000&scroll=1m'
scroll_count = 0
read_big_data = []
try:
    logdata = os.popen(command, 'r', 1)
    read_data = logdata.read()
    logdata.close()
    read_big_data[scroll_count] = json.loads(read_data)
    if read_data:
        if int(read_data['hits']['total']['value']) == 10000:
            while int(read_data['hits']['total']['value']) == 10000:
                sid = read_data['_scroll_id']
                scroll_count += 1
                command = f'curl -k -u {userdata.WAZUH_ACC}:{userdata.WAZUH_PASS} -X GET "{userdata.WAZUH_IP}{userdata.WAZUH_PORT}/wazuh-alerts-4.x-{date}/_search?pretty&size=10000&scroll&'
                logdata = os.popen(command, 'r', 1)
                read_data = logdata.read()
                logdata.close()
                read_data = json.loads(read_data)
                read_big_data[scroll_count] = read_data
                print("10 000 hits")
except Exception:
    read_data = {}
#print(f'{read_data}')

if 'error' in read_data.keys():
    #print(read_data['error']['reason'])
    print("No log data available for given date")
else:
    count = 0
    if read_data:
        for data in read_big_data:
            for i in data["hits"]["hits"]:
    #if int(i['_source']['data']['win']['system']['level']) >= userdata.LEVEL_THRESHOLD:
    #    print(f"log event description: {i['_source']['rule']['description']}")
    #    print(f"log event timestamp: {i['_source']['timestamp']}\n")
                if int(i['_source']['rule']['level']) >= userdata.LEVEL_THRESHOLD:
                    count += 1
                    print(f"log event description: {i['_source']['rule']['description']}")
                    print(f"log event timestamp: {i['_source']['timestamp']}\n")
            print(f'Count: {count}')
        else:
            print("No log data available for given date")






# Esimerkki i in read_data["hits"]["hits"] formaatista:
esimerkki_i = {
'_index': 'wazuh-alerts-4.x-2023.02.25', 
'_type': '_doc', '_id': 'Q0GdiIYBpwzpl5TUH_1d', 
'_score': 1.0, 
'_source': {
    'agent': {'ip': '192.168.1.123', 'name': 'DESKTOP-GV0CDGM', 'id': '001'}, 
    'manager': {'name': '172-104-138-12.ip.linodeusercontent.com'}, 
    'data': {
        'win': {
            'eventdata': {
                'subjectLogonId': '0x3e7', 
                'targetUserName': 'arttu', 
                'subjectUserSid': 'S-1-5-18', 
                'subjectDomainName': 'WORKGROUP', 
                'displayName': 'Arttu Juntunen', 
                'targetDomainName': 'DESKTOP-GV0CDGM', 
                'targetSid': 'S-1-5-21-526947645-2063055373-3576901729-1001', 
                'subjectUserName': 'DESKTOP-GV0CDGM$'
                }, 

            'system': {
                    'eventID': '4738', 
                    'keywords': '0x8020000000000000', 
                    'providerGuid': '{54849625-5478-4994-a5ba-3e3b0328c30d}', 
                    'level': '0', 
                    'channel': 'Security', 
                    'opcode': '0', 
                    'message': '"KÃ¤yttÃ¤jÃ¤tiliÃ¤ muutettiin.\r\n\r\nAihe:\r\n\tSuojaustunnus:\t\tS-1-5-18\r\n\tTilin nimi:\t\tDESKTOP-GV0CDGM$\r\n\tTilin toimialue:\t\tWORKGROUP\r\n\tKirjautumistunnus:\t\t0x3E7\r\n\r\nKohdetili:\r\n\tSuojaustunnus:\t\tS-1-5-21-526947645-2063055373-3576901729-1001\r\n\tTilin nimi:\t\tarttu\r\n\tTilin toimialue:\t\tDESKTOP-GV0CDGM\r\n\r\nMuutetut mÃ¤Ã¤ritteet:\r\n\tSAM-tilin nimi:\t-\r\n\tNÃ¤yttÃ¶nimi:\t\tArttu Juntunen\r\n\tKÃ¤yttÃ¤jÃ¤n tÃ¤ydellinen nimi:\t-\r\n\tKotikansio:\t\t-\r\n\tKotiasema:\t\t-\r\n\tKomentosarjan polku:\t\t-\r\n\tProfiilin polku:\t\t-\r\n\tKÃ¤yttÃ¤jÃ¤n tyÃ¶asemat:\t-\r\n\tSalasanan edellinen asetus:\t-\r\n\tTilin vanhentuminen:\t\t-\r\n\tEnsisijaisen ryhmÃ¤n tunnus:\t-\r\n\tSallittu delegoinnin kohde:\t-\r\n\tVanha kÃ¤yttÃ¤jÃ¤tilin valvonnan arvo:\t\t-\r\n\tUusi kÃ¤yttÃ¤jÃ¤tilin valvonnan arvo:\t\t-\r\n\tKÃ¤yttÃ¤jÃ¤tilien valvonta:\t-\r\n\tKÃ¤yttÃ¤jÃ¤n parametrit:\t-\r\n\tSID-historia:\t\t-\r\n\tKirjautumisajat:\t\t-\r\n\r\nLisÃ¤tiedot:\r\n\tOikeudet:\t\t-"',
                     'version': '0', 
                     'systemTime': '2023-02-25T12:47:03.5307898Z', 
                     'eventRecordID': '910413', 
                     'threadID': '22972', 
                     'computer': 'DESKTOP-GV0CDGM', 
                     'task': '13824', 
                     'processID': '1300', 
                     'severityValue': 'AUDIT_SUCCESS', 
                     'providerName': 'Microsoft-Windows-Security-Auditing'
                     }}}, 
                     'rule': {
                        'mail': False, 
                        'level': 8, 
                        'hipaa': ['164.312.a.2.I', '164.312.a.2.II', '164.312.b'],
                        'pci_dss': ['10.2.5', '8.1.2'],
                        'tsc': ['CC6.8', 'CC7.2', 'CC7.3'],
                        'description': 'User account changed.',
                        'groups': ['windows', 'windows_security', 'account_changed'], 
                        'nist_800_53': ['AC.2', 'AC.7', 'AU.14', 'IA.4'], 
                        'gdpr': ['IV_32.2', 'IV_35.7.d'], 
                        'firedtimes': 2, 
                        'mitre': {'technique': ['Account Manipulation'], 'id': ['T1098'], 'tactic': ['Persistence']}, 
                        'id': '60110', 
                        'gpg13': ['7.10']
                        }, 
                        'decoder': {'name': 'windows_eventchannel'}, 
                        'input': {'type': 'log'}, 
                        '@timestamp': '2023-02-25T12:47:18.879Z', 
                        'location': 'EventChannel', 
                        'id': '1677329238.3885', 
                        'timestamp': '2023-02-25T12:47:18.879+0000'
                        }}