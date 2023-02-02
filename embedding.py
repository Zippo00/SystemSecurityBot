import os
import openai
import numpy as np  # standard math module for python
from pprint import pprint


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def gpt3_embedding(content, engine='text-embedding-ada-002'):
    content = content.encode(encoding='ASCII',errors='ignore').decode()
    response = openai.Embedding.create(input=content,engine=engine)
    vector = response['data'][0]['embedding']  # this is a normal list
    return vector


def similarity(v1, v2):  # return dot product of two vectors
    return np.dot(v1, v2)


openai.api_key = open_file('openaiapikey_acp1.txt')


def match_class(vector, classes):
    results = []
    for c in classes:
        score = similarity(vector, c['vector'])
        information = {'category': c['category'], 'score': score}
        results.append(information)
    return results

def get_relevant_memories(memory):
    pass

def clear_memory():
    '''
    Clears the memory folder of the chatbot so it doesn't get filled with irrelevant memories
    '''
    files = os.listdir('/memories')
    if files:
        # Sort files in the folder to ascending order based on modification date
        # (Most recently modified last)
        sorted_files = sorted(files, key=lambda t: os.stat(t).st_mtime)
        # Remove least recently modified files until <200 files remain
        while len(sorted_files) > 200:
            os.remove(sorted_files[0])

def get_timestamp(filename):
    '''
    Get timestamp from a file
    :param filename: (string) Name of a file
    :return: (float) Timestamp of the file
    '''
    return float(filename.split('_')[0])

def pull_relevant_memories(memory):
    '''
    Gets relevant memories from memories

    :param memory: (string) Name of a memory file as "{vector}_{timestamp}.txt"
    :return: (list) Relevant memory files
    '''
    timestamp = get_timestamp(memory)
    memories = os.listdir('/memories')
    relevant_memories = []
    for item in memories:
        # Relevant memories = memories created +- 2hrs of the memory in question.
        # Adjust 7200s to increase/decrease relevance range
        if (get_timestamp(item) - timestamp) > 7200 and (get_timestamp(item) - timestamp) < -7200:
            relevant_memories.append(item)








if __name__ == '__main__':
    categories = ['plant', 'reptile', 'mammal', 'fish', 'bird', 'pet', 'wild animal']
    classes = []
    for c in categories:
        vector = gpt3_embedding(c)
        info = {'category': c, 'vector': vector}
        classes.append(info)
    #print(classes)
    #exit(0)
    while True:
        a = input('Enter a lifeform here: ')
        vector = gpt3_embedding(a)
        #print(a, vector)
        result = match_class(vector, classes)
        pprint(result)
