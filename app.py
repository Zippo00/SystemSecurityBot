from flask import Flask, request
from flask_cors import CORS
import json


# flask run --host=0.0.0.0
app = Flask(__name__)
CORS(app)
@app.route('/', methods=['POST'])
def return_response():
    print(f"req is {request}")
    prompt = json.loads(request.data)
    print(f"prompt is {prompt}")
    prompt_to_give = prompt['key']
    print(prompt_to_give)
    text, tokens = gpt35t_completion(prompt_to_give)
    returnval = {"message":text}
    print(returnval)
    return returnval