import openai
import json
import ast
import wazuhfunctions
import traceback
from datetime import datetime
import ipaddress

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaiapikey_acp1.txt')




def gpt35t_completion(prompt, model='gpt-3.5-turbo', temp=0.4, top_p=1.0, max_tokens=1000, freq_pen=0.7, pres_pen=0.0, stop=['"role": "assistant", "content": " "', 'user:', 'User:', 'USER:']):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=prompt,
            temperature=temp,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=freq_pen,
            presence_penalty=pres_pen,
            stop=stop)
    except openai.error.InvalidRequestError:
        # Most likely token limit exceeded.
        for item in range(int(len(prompt)/2)):
            prompt.pop(2)
        text, tokens_total = gpt35t_completion(prompt)
        return text, tokens_total
    except Exception:
        traceback.print_exc()
        return "Exception occured", 0
    text = response['choices'][0]['message']['content'].strip()
    tokens_total = response['usage']['total_tokens']
    return text, tokens_total


def dates_check(input_to_scan):
    '''
    Checks the given input for any dates in acceptable formats. If found, converts the date into
    an acceptable format by ElasticSearch API.

    :param input: (string) String to be scanned for dates.
    :return: (list) List of found dates in proper format. If none found, returns an empty list.
    '''
    if not isinstance(input_to_scan, str):
        raise ValueError("input_to_scan parameter needs to be a string")
    datecheck = True
    formatted_dates = []
    # Date formats that will be scanned for
    formats = ["%Y.%m.%d", "%d.%m.%Y", "%Y.%m.%d.", "%d.%m.%Y.", "%Y.%m.%d,", "%d.%m.%Y,", "%Y.%m.%d!", "%d.%m.%Y!", "%Y.%m.%d?", "%d.%m.%Y?", "%d.%m", "%d.%m.", "%d.%m,", "%d.%m!", "%d.%m?", "%d.%m.,", "%d.%m..", "%d.%m.!", "%d.%m.?"]
    words = input_to_scan.split()
    for word in words:
        for dateformat in formats:
            try:
                datecheck = bool(datetime.strptime(word, dateformat))
                formatted_date = reformat_date(word, dateformat)
                formatted_dates.append(formatted_date)

            except ValueError:
                datecheck = False

    return formatted_dates


def reformat_date(date, curr_format):
    '''
    Takes a date and its current format as parameters, and converts the date into acceptable format
    by ElasticSearch API.

    :param date: (string) A date as a string.
    :param curr_format: (string) Format of the date e.g. "%d.%m.%Y"
    :return: (string) Given date in proper format.

     '''
    if not isinstance(date, str):
        raise ValueError("date parameter needs to be a string.")
    if not isinstance(curr_format, str):
        raise ValueError("curr_format parameter needs to be a string")
    # Take a date formated in an acceptable way and turn it into yyyy.dd.mm
    ready_formats = ["%Y.%m.%d", "%Y.%m.%d.", "%Y.%m.%d,", "%Y.%m.%d!", "%Y.%m.%d?"]
    modify_formats = ["%d.%m.%Y", "%d.%m.%Y.", "%d.%m.%Y,", "%d.%m.%Y!", "%d.%m.%Y?"]
    short_formats = ["%d.%m", "%d.%m.", "%d.%m,", "%d.%m!", "%d.%m?", "%d.%m.,", "%d.%m..", "%d.%m.!", "%d.%m.?"]
    punctuations = [".", ",", "?", "!"]
    while date[-1] in punctuations:
        date = date[:-1]
    if curr_format in ready_formats:
        return date
    if curr_format in modify_formats:
        date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y.%m.%d')
    if curr_format in short_formats:
        current_year = str(datetime.now().year)
        date = date + "." + current_year
        date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y.%m.%d')
    return date

def active_response_scan(input_to_scan):
    '''
    Scans the given input for keywords related to executing an active response.
    
    :param input_to_scan: (string) String to be scanned for keywords
    :return: (list) List of active responses to execute.
    '''
    executed_responses = []
    message_for_AI = []
    if not isinstance(input_to_scan, str):
        raise ValueError("input_to_scan parameter needs to be a string")
    punctuations = [".", ",", "?", "!"]
    ip_keywords = ["block", "block ip", "block the ip", "block address", "block the address", "blck ip", "blck the ip", "blck address", "blck the address", "block addrss", "block adress", "block addres", "blck addres", "blck adress", "blck addrs", "block pi", "block the pi"]
    restart_keywords = ["restart wazuh agent", "restrat wazuh agent", "restart wazh agent", "restart agent", "restrat agent", "restart agnt", "restrat agnt", "restart aent", "restrat aent", "restart agen", "restrat agen"]
    input_to_scan = input_to_scan.lower()
    # Scan the input for Block IP keywords
    for keyword in ip_keywords:
        if keyword in input_to_scan:
            # If found scan the input for IP address
            words = input_to_scan.split()
            for word in words:
                try:
                    ipaddress.ip_address(word)
                    # If found, run block IP API command and append the response into list
                    executed_responses.append(wazuhfunctions.ar_block_ip(word))
                except Exception:
                    continue
    for response in executed_responses:
        if "was sent" in response:
            message_for_AI.append("***YOU, ALICE, SUCCESFULLY BLOCKED THE IP ADDRESS ON ALL DEVICES CONNECTED TO USER'S WAZUH MANAGER***")
    # Scan the input for Agent Restart keywords
    for keyword in restart_keywords:
        if keyword in input_to_scan:
            # If found split the input into words and find the word "agent" or misspelled
            # equivalent.
            words = input_to_scan.split()

            for index, word in enumerate(words):
                while word[-1] in punctuations:
                    word = word[:-1]
                if word in ("agent", "agnt", "aent", "agen", "id", "agentid", "agntid"):
                    # When "id", "agent" or misspelled equivalent is found, make the educated
                    # guess that either next word or the word after the next is the ID number.
                    try:
                        if words[index + 1].isnumeric():
                            executed_responses.append(wazuhfunctions.ar_restart_agent(words[index + 1]))
                    except IndexError:
                        pass
                    try:
                        if words[index + 2].isnumeric():
                            executed_responses.append(wazuhfunctions.ar_restart_agent(words[index + 1]))
                    except IndexError:
                        pass
    for response in executed_responses:
        if "Restart command was sent" in executed_responses:
            message_for_AI.append("***YOU, ALICE, SUCCESFULLY RESTARTED THE AGENT THROUGH WAZUH API***")
    return message_for_AI


            
if __name__ == '__main__':
    # ChatAI System Message
    conversation = [{"role": "system", "content" : "You are a cyber security assistant called Alice. You aim to assist the user with cyber security and you have the ability to analyze system logs generated by Wazuh, block IP addresses and restart Wazuh agents. If user message includes 'Block IP command was sent to all agents', you have succesfully blocked the IP address. If user message includes 'Restart command was sent to agent 002', you have succesfully restarted the agent. If user prompts you with a date in format yyyy.mm.dd, dd.mm.yyyy or dd.mm, you get the user's logs for given date(s) at the end of the prompt. Log data is in format ***LOG DATA: ****"}]
    LOG_FLAG = False
    tokens = 0
    while True:
        dates = []
        active_responses = []
        # If Conversation starts to near max tokens (4096), remove older half of convo from memory.
        if tokens > 3000:
            for i in range(int(len(conversation)/2)):
                conversation.pop(1)
            LOG_FLAG = True
        # Ask user for prompt
        user_input = input('USER: ')
        # Scan the user input for dates in formats dd.mm.yyy, yyyy.mm.dd, or dd.mm
        dates = dates_check(user_input)
        if dates:
            latest_logs = ""
            # If found dates in acceptable format in user's input
            # Get meaningful system logs for given dates from ElasticSearch API
            meaningful_logs = ["\n\n"]
            for i in dates:
                get_logs = wazuhfunctions.get_logs(i)
                meaningful_logs = meaningful_logs + get_logs
            for index, logs in enumerate(meaningful_logs):
                for j in logs:
                    latest_logs += j
                    user_input += j
        # Scan the user input for keywords associated with active response commands and execute them if found.
        active_responses = active_response_scan(user_input)
        if active_responses:
            for response in active_responses:
                user_input += response
        #print(f"\nUser input before appending to convo: {user_input}")
        # Make sure latest analyzed logs stay in memory
        if LOG_FLAG:
            LOG_FLAG = False
            if "LOG EVENT:" not in conversation and "LOG_EVENT:" not in user_input:
                conversation.insert(1, '''{''' + f''''role': 'user', 'content': '{latest_logs}' ''' + '}')
        # Append the user prompt into conversation.
        conversation.append('''{''' + f''''role': 'user', 'content': '{user_input.replace("'", '"')}' ''' + '}')
        conversation[-1] = ast.literal_eval(conversation[-1].replace('\r','\\r').replace('\n','\\n'))
        # Append a stop signal for AI to the end of convo.
        conversation.append('{"role": "assistant", "content": " "}')
        conversation[-1] = ast.literal_eval(conversation[-1].replace('\r','\\r').replace('\n','\\n'))
        # Get response from AI
        response, tokens = gpt35t_completion(conversation)
        if response == "Exception occured":
            print("Something went wrong. Please try again later.")
            exit()
        # Print the AI's response
        print('Alice:', response)
        #print(f'Total tokens used: {tokens}')
        # Append the AI's response into convo.
        conversation[-1] = '''{''' + f''''role': 'assistant', 'content': '{response.replace("'", '"')}' ''' + '}'
        conversation[-1] = ast.literal_eval(conversation[-1].replace('\r','\\r').replace('\n','\\n'))
