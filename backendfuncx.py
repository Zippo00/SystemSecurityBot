'''
Contains functions for the backend of cyber security assistant powered by GPT3.5 turbo.
'''
from datetime import datetime
import ipaddress
import openai
import wazuhfunctions

def open_file(filepath):
    '''
    Open a file.

    :param filepath: (string) Path to the file.
    :return: Opened file.
    '''
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def remove_sentence(response_to_scan):
    '''
    If a specified sentence is found in parameter response, removes the sentence from it and returns the modified string. 
    If no sentences to remove are found in the given string, returns the original string.

    :param response: (string) Completion message from ChatGPT.
    :return: (string) The message given as parameter without the specified sentences.
    '''
    if not isinstance(response_to_scan, str):
        return "Parameter response must be a string."
    to_remove =  [
                    "Based on the logs you provided,", "Based on the logs you provided.", 
                    "Based on the logs you provided", "based on the logs you provided,", 
                    "based on the logs you provided.", "based on the logs you provided", 
                    "Based on logs you provided,", "Based on logs you provided.", 
                    "Based on logs you provided", "based on logs you provided,", 
                    "based on logs you provided.", "based on logs you provided"
                    ]
    for sentence in to_remove:
        if sentence in response_to_scan:
            response_to_scan = response_to_scan.replace(sentence, "")
    while response_to_scan[0] == " ":
        response_to_scan = response_to_scan[1:]
    if response_to_scan[0].isupper() == False:
        response_to_scan = response_to_scan[0].upper() + response_to_scan[1:]
    return response_to_scan


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
    formats = [
                "%Y.%m.%d", "%d.%m.%Y", "%Y.%m.%d.", "%d.%m.%Y.", "%Y.%m.%d,", "%d.%m.%Y,",
                "%Y.%m.%d!", "%d.%m.%Y!", "%Y.%m.%d?", "%d.%m.%Y?", "%d.%m", "%d.%m.", 
                "%d.%m,", "%d.%m!", "%d.%m?", "%d.%m.,", "%d.%m..", "%d.%m.!", "%d.%m.?"
                ]
    formats_day = ["%d"]
    formats_month = ["%b", "%B"]
    day = ''
    month = ''
    date = ''
    punctuations = [".", ",", "?", "!", "-", "_", "'", '"', "=", "<", ">"]
    ordinals = ["st", "nd", "rd", "th"]
    # Split the input into single words
    words = input_to_scan.split()
    for word in words:
        raw_day = ""
        if len(word) > 1:
            # Remove punctuations from beginning and end of the word, if there are any
            while word[-1] in punctuations:
                word = word[:-1]
            while word[0] in punctuations:
                word = word[1:]
        # Remove potential ordinals "1st" --> "1"
        for ordinal in ordinals:
            if ordinal in word:
                # If ordinal was found and removed, store the modified word into variable raw_day
                raw_day = word.replace(f"{ordinal}", "")
        # Check if the word is a date in a specified format
        for dateformat in formats:
            try:
                datecheck = bool(datetime.strptime(word, dateformat))
                # If the program gets here, the word was a date in specified format
                # Format the date into yyyy.mm.dd
                formatted_date = reformat_date(word, dateformat)
                formatted_dates.append(formatted_date)

            except ValueError:
                datecheck = False
        # Check if the word matches a format in formats_day
        for day_format in formats_day:
            try:
                if raw_day:
                    if bool(datetime.strptime(raw_day, day_format)):
                        # If matches and raw_day variable isn't empty, raw_day is a day
                        # (And not some random word with a ordinal in it e.g. 'STable') 
                        day = raw_day
                else:
                    # If raw_day variable is empty, but word matches a format in day_format
                    if bool(datetime.strptime(word, day_format)):
                        day = word
            except ValueError:
                continue
        # Check if the word matches a format in formats_month
        for month_format in formats_month:
            try:
                if bool(datetime.strptime(word, month_format)):
                    # If matches, store the month and format into variables
                    month = word
                    format_m = month_format
            except ValueError:
                continue
        # If both day and month were found in the given input
        if day and month:
            # Add current year into the mix, and format the date into yyyy.mm.dd
            current_year = str(datetime.now().year)
            date = datetime.strptime(day + month + current_year, f"%d{format_m}%Y").strftime('%Y.%m.%d')
            formatted_dates.append(date)
            day = ''
            month = ''
    # Return found dates in yyyy.mm.dd
    return formatted_dates


def reformat_date(date, curr_format):
    '''
    Takes a date and its current format as parameters, and converts the date into acceptable format
    by ElasticSearch API.

    :param date: (string) A date as a string.
    :param curr_format: (string) Format of the date e.g. "%d.%m.%Y"
    :return: (string) Given date in format yyyy.mm.dd

    '''
    if not isinstance(date, str):
        raise ValueError("date parameter needs to be a string.")
    if not isinstance(curr_format, str):
        raise ValueError("curr_format parameter needs to be a string")
    # Take a date formated in an acceptable way and turn it into yyyy.dd.mm
    ready_formats = ["%Y.%m.%d", "%Y.%m.%d.", "%Y.%m.%d,", "%Y.%m.%d!", "%Y.%m.%d?"]
    modify_formats = ["%d.%m.%Y", "%d.%m.%Y.", "%d.%m.%Y,", "%d.%m.%Y!", "%d.%m.%Y?"]
    short_formats = [
                    "%d.%m", "%d.%m.", "%d.%m,", "%d.%m!", "%d.%m?", 
                    "%d.%m.,", "%d.%m..", "%d.%m.!", "%d.%m.?"
                    ]
    punctuations = [".", ",", "?", "!", "-", "_", "'", '"', "=", "<", ">"]
    # If any punctuations at the end or beginning of the given date, remove them.
    while date[-1] in punctuations:
        date = date[:-1]
    # If date already in format yyyy.mm.dd, return it
    if curr_format in ready_formats:
        return date
    # If format of the date is in modify_formats, change the format into yyyy.mm.dd
    if curr_format in modify_formats:
        date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y.%m.%d')
    # If format of the date is in short_formats, throw current year into the mix and change
    # the format into yyyy.mm.dd
    if curr_format in short_formats:
        current_year = str(datetime.now().year)
        date = date + "." + current_year
        date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y.%m.%d')
    # Return the given date in format yyyy.mm.dd
    return date

def active_response_scan(input_to_scan):
    '''
    Scans the given input for keywords related to executing an active response.
    
    :param input_to_scan: (string) String to be scanned for keywords
    :return: (list) List of active responses to execute.
    '''
    executed_responses = []
    message_for_AI = []
    punctuations = [".", ",", "?", "!", "-", "_", "'", '"', "=", "<", ">"]
    if not isinstance(input_to_scan, str):
        raise ValueError("input_to_scan parameter needs to be a string")
    ip_keywords = [
                    "block", "block ip", "block the ip", "block address", "block the address",
                    "blck ip", "blck the ip", "blck address", "blck the address", "block addrss", 
                    "block adress", "block addres", "blck addres", "blck adress", "blck addrs", "block pi", "block the pi"
                    ]
    restart_keywords = [
                        "restart wazuh agent", "restrat wazuh agent", "restart wazh agent",
                        "restart agent", "restrat agent", "restart agnt", "restrat agnt", 
                        "restart aent", "restrat aent", "restart agen", "restrat agen",
                        "restar agent", "restar agen", "restar agnt", "restart", "restar", "restrat"
                        ]
    input_to_scan = input_to_scan.lower()
    # Scan the input for Block IP keywords
    for keyword in ip_keywords:
        if keyword in input_to_scan:
            # If found, scan the input for IP address
            words = input_to_scan.split()
            for word in words:
                if len(word) > 1:
                    while word[-1] in punctuations:
                        word = word[:-1]
                    while word[0] in punctuations:
                        word = word[1:]
                try:
                    ipaddress.ip_address(word)
                    # If found, run block IP API command and append the response into list
                    executed_responses.append(wazuhfunctions.ar_block_ip(word))
                except Exception:
                    continue
            break
    for response in executed_responses:
        if "was sent" in response:
            #message_for_AI.append("***YOU, ALICE, SUCCESFULLY BLOCKED THE IP ADDRESS ON ALL DEVICES CONNECTED TO USER'S WAZUH MANAGER***")
            message_for_AI.append(response)
        else:
            message_for_AI.append(response)
    # Scan the input for Agent Restart keywords
    for keyword in restart_keywords:
        if keyword in input_to_scan:
            # If found split the input into words and find the word "agent" or misspelled
            # equivalent.
            words = input_to_scan.split()

            for index, word in enumerate(words):
                if len(word) > 1:
                    while word[-1] in punctuations:
                        word = word[:-1]
                    while word[0] in punctuations:
                        word = word[1:]
                if word in ("agent", "agnt", "aent", "agen", "id", "agentid", "agntid", "restart", "restar", "restrat"):
                    # When "id", "agent", "restart" or misspelled equivalent is found, make the educated
                    # guess that either one of the following words is the ID number.
                    try:
                        if words[index + 1].isnumeric():
                            executed_responses.append(wazuhfunctions.ar_restart_agent(words[index + 1]))
                    except IndexError:
                        pass
                    try:
                        if words[index + 2].isnumeric():
                            executed_responses.append(wazuhfunctions.ar_restart_agent(words[index + 2]))
                    except IndexError:
                        pass
                    try:
                        if words[index + 3].isnumeric():
                            executed_responses.append(wazuhfunctions.ar_restart_agent(words[index + 3]))
                    except IndexError:
                        pass
                    try:
                        if words[index + 4].isnumeric():
                            executed_responses.append(wazuhfunctions.ar_restart_agent(words[index + 4]))
                    except IndexError:
                        pass
            break
    for response in executed_responses:
        if "Restart command was sent" in executed_responses:
            message_for_AI.append("***YOU, ALICE, SUCCESFULLY RESTARTED THE AGENT THROUGH WAZUH API***")
        else:
            message_for_AI.append(response)
    return message_for_AI