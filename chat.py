import openai
import json
import getlogs
from datetime import datetime


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaiapikey_acp1.txt')

keywords = ["", "", ""]


def gpt35t_completion(prompt, model='gpt-3.5-turbo', temp=0.6, top_p=1.0, max_tokens=800, freq_pen=0.7, pres_pen=0.0, stop=['"role": "assistant", "content": " "', 'user:', 'User:', 'USER:']):
    response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=temp,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=freq_pen,
        presence_penalty=pres_pen,
        stop=stop)
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
    datecheck = True
    formatted_dates = []
    # Date formats that will be scanned for
    formats = ["%Y.%m.%d", "%d.%m.%Y", "%Y.%m.%d.", "%d.%m.%Y.", "%Y.%m.%d,", "%d.%m.%Y,", "%Y.%m.%d!", "%d.%m.%Y!", "%Y.%m.%d?", "%d.%m.%Y?"]
    words = input_to_scan.split()
    for i in words:
        for j in formats:
            try:
                datecheck = bool(datetime.strptime(i, j))
                formatted_date = reformat_date(i, j)
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
    # Take a date formated in an acceptable way and turn it into yyyy.dd.mm
    ready_formats = ["%Y.%m.%d", "%Y.%m.%d.", "%Y.%m.%d,", "%Y.%m.%d!", "%Y.%m.%d?"]
    modify_formats = ["%d.%m.%Y", "%d.%m.%Y.", "%d.%m.%Y,", "%d.%m.%Y!", "%d.%m.%Y?"]
    punctuations = [".", ",", "?", "!"]
    while date[-1] in punctuations:
        date = date[:-1]
    if curr_format in ready_formats:
        return date
    if curr_format in modify_formats:
        date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y.%m.%d')
        return date


if __name__ == '__main__':
    # ChatAI System Message
    conversation = [{"role": "system", "content" : "You are a cyber security assistant called Alice. You aim to assist the user with cyber security and you have the ability to analyze system logs. If user prompts you with a date in format yyyy.mm.dd or dd.mm.yyyy, you get the user's logs for given date(s) at the end of the prompt. Log data begins in format LOG EVENT:"}]
    while True:
        # Ask user for prompt
        user_input = input('USER: ')
        # SCAN THE USER INPUT FOR KEYWORDS
        dates = dates_check(user_input)
        if dates:
            # If found dates in acceptable format in user's input
            # Get meaningful system logs for given dates form ElasticSearch API
            meaningful_logs = ["\n\n"]
            for i in dates:
                logs = getlogs.get_logs(i)
                meaningful_logs = meaningful_logs + logs
            for index, logs in enumerate(meaningful_logs):
                for j in logs:
                    user_input += j
        #print(f"\nUser input before appending to convo: {user_input}")
        # Append the user prompt into conversation.
        conversation.append('{' + f'"role": "user", "content": "{user_input}"' + '}')
        conversation[-1] = json.loads(conversation[-1], strict=False)
        # Append a stop signal for AI to the end of convo.
        conversation.append('{' + '"role": "assistant", "content": " "' + '}')
        conversation[-1] = json.loads(conversation[-1], strict=False)
        # Get response from AI
        response, tokens = gpt35t_completion(conversation)
        print('Alice:', response)
        #print(f'Total tokens used: {tokens}')
        # Append the AI's response into convo.
        conversation[-1] = '{' + f'"role": "assistant", "content": "{response}"' + '}'
        conversation[-1] = json.loads(conversation[-1], strict=False)
        # If Conversation starts to near max tokens (4096), remove older half of convo from memory.
        if tokens > 3000:
            for i in range(int(len(conversation)/2)):
                conversation.pop(1)





'{"role": assistant, "content": As a cyber security assistant, I can help you with various tasks related to cyber security. For example, I can:\n\n1. Provide general information about cyber security and best practices.\n2. Help you identify potential vulnerabilities in your system.\n3. Assist you in configuring and securing your network.\n4. Analyze system logs to detect any suspicious activities or potential threats.\n5. Offer guidance on how to respond to a security incident or breach.\n\nLet me know if there is anything specific you need help with!'