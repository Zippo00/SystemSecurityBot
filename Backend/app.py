import ast
import traceback
from datetime import datetime
import openai
import wazuhfunctions
import backendfuncx

from flask import Flask, request
from flask_cors import CORS
import json



# OpenAI API key
# Make sure to create a text file named "openaiapikey", which contains nothing but your OpenAI API key in UTF-8, into the folder containing this python file if not already there.
openai.api_key = backendfuncx.open_file('openaiapikey.txt')



conversation = [{"role": "system", "content" : "You are a cyber security assistant called Alice. You aim to assist the user with cyber security and you have the ability to analyze system logs generated by Wazuh, block IP addresses and restart Wazuh agents. If user message includes 'Block IP command was sent to all agents', you have succesfully blocked the IP address. If user message includes 'Restart command was sent to agent', you have succesfully restarted the agent. If user prompts you with a date, you get the logs through Wazuh API. Log data is in format ***LOG DATA: ****"}]
LOG_FLAG = False
RESTART_AGENT_FLAG = False
BLOCK_IP_FLAG = False
tokens = 0
latest_logs = ""

# flask run --host=0.0.0.0
app = Flask(__name__)
CORS(app)
@app.route('/', methods=['POST'])
def return_response():
    dates = []
    active_responses = []    
    global tokens
    global conversation
    global latest_logs
    # If Conversation starts to near max tokens (4096), remove older half of convo from memory.
    if tokens > 3000:
        for i in range(int(len(conversation)/2)):
            conversation.pop(1)
        global LOG_FLAG
        LOG_FLAG = True
    #print(f"Request is: \n{request}\n")
    # Ask user for prompt
    user_input = json.loads(request.data)
    user_input = user_input['key']
    dates = backendfuncx.dates_check(user_input)
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
    # If AI completion triggered the RESTART_AGENT_FLAG
    global RESTART_AGENT_FLAG
    if RESTART_AGENT_FLAG:
        RESTART_AGENT_FLAG = False
        for i in ("yes", "Yes", "sure", "Sure", "proceed", "Proceed", "certainly", "Certainly", "absolutely", "Absolutely"):
            if i in user_input:
                # If user's input contained a keyword suggesting they want to restart a wazuh agent, try to do so.
                if not active_responses:
                    active_responses = backendfuncx.active_response_scan(conversation[-1]["content"])
                    if not active_responses:
                        words = conversation[-1]["content"].split()
                        string_to_scan = conversation[-2]["content"]
                        for word in words:
                            string_to_scan += " " + word
                        active_responses = backendfuncx.active_response_scan(string_to_scan)
                        break
        if not active_responses:
            # Also check if the user's input only contained the ID of agent to be restarted, if yes try to do so.
            if any(char.isdigit() for char in user_input):
                active_responses = backendfuncx.active_response_scan(conversation[-1]["content"] + user_input)
                if not active_responses:
                    words = conversation[-1]["content"].split()
                    #print(f"Words: {words}")
                    string_to_scan = conversation[-2]["content"]
                    for word in words:
                        string_to_scan += " " + word
                    string_to_scan += " " + user_input
                    active_responses = backendfuncx.active_response_scan(string_to_scan)

    # If AI completion triggered the BLOCK_IP_FLAG
    global BLOCK_IP_FLAG
    if BLOCK_IP_FLAG:
        BLOCK_IP_FLAG = False
        for i in (
            "yes", "Yes", "sure", "Sure", "proceed", "Proceed", "certainly", "Certainly", "absolutely", "Absolutely", "confirm", "Confirm", "block on", "Block on",
            "yes.", "Yes.", "sure.", "Sure.", "proceed.", "Proceed.", "certainly.", "Certainly.", "absolutely.", "Absolutely.", "confirm.", "Confirm.", "block on,", "Block on,",
            "yes,", "Yes,", "sure,", "Sure,", "proceed,", "Proceed,", "certainly,", "Certainly,", "absolutely,", "Absolutely,", "confirm,", "Confirm,", "block on.", "Block on."
        ):
            if i in user_input:
                # If user's input contained a keyword suggesting they want the IP address to be blocked, try to do so.
                active_responses = backendfuncx.active_response_scan(conversation[-1]["content"])
                break
    # Scan the user input for keywords associated with active
    # response commands and execute them if found.
    if not active_responses:
        active_responses = backendfuncx.active_response_scan(user_input)
    # If any active responses were executed,
    # add the response message associated with the active response into user's input
    if active_responses:
        for response in active_responses:
            user_input += response

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
    #print(f"Conversation :\n\n {conversation}\n\n")
    # Get response from AI
    response, tokens = gpt35t_completion(conversation)
    # Remove any unwanted sentences from the AI's response
    response = backendfuncx.remove_sentence(response)
    if response == "Exception occured":
        response = "I apologize. There seems to be so much traffic in my servers that I couldn't think of a reply. Please refresh the page or try chatting with me later."
    # Check if the reponse contains any keywords associated with restarting a wazuh agent
    for i in ("proceed with the restart", "proceed with restart", "me to restart", "want to restart"):
        if i in response:
            # If yes, check the RESTART_AGENT_FLAG
            RESTART_AGENT_FLAG = True
    # Check if the response contains any keywords associated with blocking an IP address
    for i in ("with blocking", "me to block", "want to block"):
        if i in response:
            # If yes, check the BLOCK_IP_FLAG
            BLOCK_IP_FLAG = True
    returnval = {"message":response}
    conversation[-1] = '''{''' + f''''role': 'assistant', 'content': '{response.replace("'", '"')}' ''' + '}'
    conversation[-1] = ast.literal_eval(conversation[-1].replace('\r','\\r').replace('\n','\\n'))
    # Save the convo into a new text file in user_data folder
    backendfuncx.save_conversation(conversation)
    #print("Script is now returning the response\n")
    return returnval



def gpt35t_completion(prompt, model='gpt-3.5-turbo', temp=0.4, top_p=1.0, max_tokens=1000, freq_pen=0.7, pres_pen=0.0, stop=['"role": "assistant", "content": " "', 'user:', 'User:', 'USER:']):
    '''
    Get a completion from OpenAI's GPT LLM to a prompt.

    :param prompt: (list) List of dictionaries where each dictionary is in format: {'role': 'user', 'content': 'Hello!'}
    :(Optional) param model: (string) GPT model to use. Default: gpt-3.5-turbo
    :(Optional) param temp: (int) See OpenAI documentation. Default: 0.4
    :(Optional) param top_p: (int) See OpenAI documentation. Default: 1.0
    :(Optional) param max_tokens: (int) See OpenAI documentation. Default: 1000
    :(Optional) param freq_pen: (int) See OpenAI documentation. Default: 0.7
    :(Optional) param pres_pen: (int) See OpenAI documentation. Default: 0.0
    :(Optional) param stop: (list) Stop signals for the GPT model (MAX 4).

    :return text: (string) Completion generated by the GPT model.
    :return tokens_total: (int) Total amount of tokens used on the prompt + completion.
    '''
    text = ''
    tokens_total = 0
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
        if len(prompt) < 3:
            # TODO: Cut some logs off if they exceed 4000 tokens.
            return text, tokens_total
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


if __name__ == '__main__':
    app.run(debug=True)
