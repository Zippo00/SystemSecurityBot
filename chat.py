import openai


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaiapikey_acp1.txt')


def gpt3_completion(prompt, engine='text-davinci-003', temp=0.7, top_p=1.0, tokens=300, freq_pen=0.0, pres_pen=0.0, stop=['NANCYTHEBOT:', 'USER:']):
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temp,
        max_tokens=tokens,
        top_p=top_p,
        frequency_penalty=freq_pen,
        presence_penalty=pres_pen,
        stop=stop)
    text = response['choices'][0]['text'].strip()
    return text


if __name__ == '__main__':
    conversation = []
    while True:
        user_input = input('USER: ')
        conversation.append(f'USER: {user_input}')
        text_block = '\n'.join(conversation)
        prompt = open_file('chatlog.txt').replace('<<BLOCK>>', text_block)
        prompt = prompt + '\nNANCYTHEBOT:'
        response = gpt3_completion(prompt)
        print('NANCY:', response)
        conversation.append(f'NANCYTHEBOT: {response}')
