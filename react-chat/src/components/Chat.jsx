import ChatMessage from "./ChatMessage";
import { useState, useEffect } from "react";

import "./Chat.css";
//const { Configuration, OpenAIapi } = require("openai");

function Chat() {
  const [users, setUsers] = useState([]);

  /* const openai = new openai(configuration);
  const [prompt, setPrompt] = useState(""); */

  /* const configuration = {
    apiKey: process.env.REACT_APP_OPENAI_API_KEY,
  }; */

  /*   const openai = new OpenAIapi(configuration);
  const [prompt, setPrompt] = useState("");
  const [apiResponse, setApiResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const configuration = new Configuration({
    apiKey: process.env.REACT_APP_OPENAI_API_KEY,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await openai.createCompletion({
        model: "text-davinci-003",
        prompt: prompt,
        temperature: 0.5,
        max_tokens: 4000,
      });
      //console.log("response", result.data.choices[0].text);
      messages.push(setApiResponse(result.data.choices[0].text));
    } catch (e) {
      //console.log(e);
      setApiResponse("Something is going wrong, Please try again.");
    }
    setLoading(false);
  }; */

  //http api taski kutsuja frontista ja mistä osoitteesta löytyy

  //postman

  //position relative
  //flex column tyyppi, bootstrap uusi rivi loppuun

  //async so it waits until it can run

  //run with: npm run dev

  async function getResponse() {
    const messageToSend = { key: message };
    let aiResponse = await fetch("http://192.168.0.179:5000/", {
      //await so that AI can generate the response?
      method: "POST",
      mode: "cors", //permits loading resource from other origins (our API)

      body: JSON.stringify(messageToSend),
    })
      .then((response) => response.json()) //fetch response (object), this is unreadable so convert to json -> now refer as "data"
      .then((data) => {
        return data["message"]; //this is what the API has returned, look for the key called message in it, contains AI's completion
      });
    console.log(aiResponse);
    messages.push({
      id: Date.now(),
      msg: aiResponse,
      name: "Alice",
    });
    setUpdated(aiResponse); //displays pushed msg in UI
  }

  const fetchResponse = () => {
    fetch("https://jsonplaceholder.typicode.com/comments/1")
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        console.log(data);
        setUsers(data);
      });
  };

  useEffect(() => {
    fetchResponse();
  }, []);

  //Mock data
  /* let messages = [
    { id: "1", msg: "jou 1", name: "gpt" },
    { id: "2", msg: "jeejee", name: "user" },
  ]; */

  const [messages, setMessages] = useState([]);

  const links = [
    { title: "FAQ", url: "https://www.justwatch.com/" },
    {
      title: "Bootstrap",
      url: "https://getbootstrap.com/docs/5.0/getting-started/introduction/",
    },
    { title: "Gradients", url: "https://cssgradient.io/" },
    { title: "JSON Mock", url: "https://jsonplaceholder.typicode.com/guide/" },
  ];

  //Test state
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const handleSelectItem = (item) => {
    setSelectedIndex(item.id);
    console.log(item);
  };

  const [message, setMessage] = useState("");

  const [updated, setUpdated] = useState("");

  const handleChange = (event) => {
    setMessage(event.target.value);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      //  Get input value
      console.log(message);
      setUpdated(message); //displays msg in chat

      messages.push({ id: Date.now(), msg: message, name: "user" }); //pushes to all clients
      getResponse(); //attempts to get response to msg
      setMessage("");
    }
  };

  return (
    <div className="container-fluid py-5">
      <div className="card chat-window">
        <div className="card-header d-flex justify-content-between align-items-center p-3 text-white border-bottom-1">
          LogBot
        </div>
        <div className="card-body row">
          <div className="col-md-3 col-lg-3 col-xl-2 chat-links">
            <ul className="list-group list-group-flush">
              {links.map((link) => (
                <li key={link.url} className="list-group-item bg-transparent">
                  <a href={link.url} className="text-white" target="_blank">
                    {link.title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div className="col  p-0">
            <div className="card chat-messages rounded-0">
              <div className="card-header d-flex justify-content-between align-items-center p-3 text-white border-bottom-0 rounded-0"></div>
              <div className="card-body p-0">
                <div data-mdb-perfect-scrollbar="true">
                  {messages.map((msg) => (
                    <ChatMessage
                      className={selectedIndex === msg.id ? "active" : ""}
                      key={msg.id}
                      message={msg}
                      onSelectItem={handleSelectItem}
                    ></ChatMessage>
                  ))}
                </div>
                <div className="form-outline">
                  <input
                    className="form-control text-white chat-input rounded-0"
                    id="textAreaExample"
                    value={message}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message"
                  ></input>
                  {/* <label className="form-label" htmlFor="textAreaExample">
                    Type your message
                  </label> */}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chat;
