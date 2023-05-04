import ChatMessage from "./ChatMessage";
import { useState, useEffect, useRef } from "react";

import "./Chat.css";

function Chat() {
  const [users, setUsers] = useState([]);

  //run with: npm run dev

  //Toggle visible content
  const [isChatVisible, setIsChatVisible] = useState(true);
  const [isFAQVisible, setIsFAQVisible] = useState();
  const [isDocVisible, setIsDocVisible] = useState();
  const [isQuizVisible, setIsQuizVisible] = useState();

  const handleChatPress = () => {
    //setIsChatVisible(isVisible) => !isVisible;
    setIsChatVisible(!isChatVisible);
    setIsFAQVisible(false);
    setIsDocVisible(false);
    setIsQuizVisible(false);
  };

  const handleFAQPress = () => {
    setIsFAQVisible(!isFAQVisible);
    setIsChatVisible(false);
    setIsDocVisible(false);
    setIsQuizVisible(false);
  };

  const handleDocPress = () => {
    setIsDocVisible(!isDocVisible);
    setIsChatVisible(false);
    setIsFAQVisible(false);
    setIsQuizVisible(false);
  };

  const handleQuizPress = () => {
    setIsQuizVisible(!isQuizVisible);
    setIsChatVisible(false);
    setIsFAQVisible(false);
    setIsDocVisible(false);
  };

  async function getResponse() {
    const messageToSend = { key: message };
    let aiResponse = await fetch("http://193.166.25.249:5000/", {
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

  const [messages, setMessages] = useState([]);

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
      //prevent empty message
      if (message !== "") {
        console.log(message);
        setUpdated(message); //displays msg in chat

        messages.push({ id: Date.now(), msg: message, name: "You" }); //pushes to all clients
        getResponse(); //attempts to get response to msg
        setMessage("");
      }
    }
  };

  return (
    <div className="container-fluid py-5">
      <div className="card chat-window">
        <div className="card-header d-flex justify-content-between align-items-center p-3 text-white border-bottom-1">
          Alice, the Cyber Security Assistant
        </div>
        <div className="card-body row">
          <div className="col-md-3 col-lg-3 col-xl-2 chat-links">
            <ul className="list-group list-group-flush">
              <button
                type="button"
                className="btn btn-primary btn-lg"
                onClick={handleChatPress}
                disabled={isChatVisible}
              >
                Chat
              </button>
              <button
                type="button"
                className="btn btn-primary btn-lg"
                onClick={handleFAQPress}
                disabled={isFAQVisible}
              >
                FAQ
              </button>

              <button
                type="button"
                className="btn btn-primary btn-lg"
                onClick={handleDocPress}
                disabled={isDocVisible}
              >
                Documentation
              </button>

              <button
                type="button"
                className="btn btn-primary btn-lg"
                onClick={handleQuizPress}
                disabled={isQuizVisible}
              >
                Give feedback
              </button>
            </ul>
          </div>
          <div className="col  p-0">
            {isChatVisible && (
              <div className="card chat-messages rounded-0">
                <div className="card-header d-flex justify-content-between align-items-center p-3 text-white border-bottom-0 rounded-0"></div>
                <div className="card-body p-0">
                  <div
                    className="chat-container"
                    data-mdb-perfect-scrollbar="true"
                  >
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
                      type="text"
                      autoFocus
                      autoComplete="off"
                    ></input>
                    {/* <label className="form-label" htmlFor="textAreaExample">
                    Type your message
                  </label> */}
                  </div>
                </div>
              </div>
            )}
            <div className="col2 p-0">
              {isFAQVisible && (
                <div
                  className="card-body FAQ"
                  data-mdb-perfect-scrollbar="true"
                >
                  <div className="fw-bold h5 text-white">What is the purpose of this testing / What am I supposed to test?</div>
                  <div className="h6 text-white p-1">The purpose of this testing period is to gain valuable feedback from users who interact with Alice to determine what is good and what is bad about her. As well as direct the further development of Alice. You can interact with Alice and test her functionalities freely and test how she could help you, or any potential user, with anything related to cyber security. Alice's main functionalities are answering any questions user may have about cyber security, informing the user about cyber security best practices, analyzing user's system logs, blocking IP addresses from accessing user's system and restart Wazuh agents in user's system.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">What is Alice?</div>
                  <div className="h6 text-white p-1">In her own words: "I am a cyber security assistant called Alice designed to help users with their cyber secuirty needs.  I can analyze system logs generated by Wazuh, block IP addresses, and restart Wazuh agents to maintain the security of your systems and networks. I am powered by advanced algorithms that allow me to detect potential threats and vulnerabilities in real-time. I can also provide recommendations on how to improve your cyber security posture based on industry best practices. My goal is to make cyber security accessible for everyone, regardless of technical expertise. Whether you are an individual or a business owner, I can help you keep your systems secure and protect your sensitive data from cyber attacks. If you have any questions or concerns about your system`s security, feel free to ask me anything!"</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">What can Alice do?</div>
                  <div className="h6 text-white p-1">Main purpose of Alice is to analyze system logs, block IP addresses, restart Wazuh agents and assist user with cyber security related matters. Alice is powered by OpenAI's ChatGPT, so additionally it can do anything ChatGPT can do.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">Alice is not responding, what gives?</div>
                  <div className="h6 text-white p-1">Alice is scheduled to function only during the testing period from ##.## to ##.##. Outside of that timeframe, you can see this webpage but Alice is not connected to it. If Alice is not responding inside that timeframe, OpenAI's server are most likely overloaded due to high amount of traffic and Alice can not generate a reply. In this case, please notify us via email at alice.chatbot1@gmail.com and try messaging Alice later.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">What is Wazuh?</div>
                  <div className="h6 text-white p-1">Wazuh is a platform for system security monitoring and incident response. For the purposes of this testing period, you don't have to worry about Wazuh if you are not familiar with it.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">How can Alice analyze my logs?</div>
                  <div className="h6 text-white p-1">Alice is currently connected to our Wazuh manager - so in this testing period, when you ask Alice to analyze system logs and system status, she is analyzing the logs and status of our system. When ultimately published, you will be able to connect Alice to your own Wazuh manager.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">Why can't I connect Alice to my Wazuh manager?</div>
                  <div className="h6 text-white p-1">To make the testing period more simple, we excluded this functionality. Alice is connected to our Wazuh manager set up for testing purposes. All analyses you get from Alice are based on the logs of our dummy system, and when you ask Alice to block IPs, she blocks them from accessing our dummy system. Our dummy system has Wazuh agents 001 and 003, you can ask Alice to restart these and see what she'll reply.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">Can I use Alice without Wazuh?</div>
                  <div className="h6 text-white p-1">Currently, no. Alice is in the prealpha testing phase, and at the moment Alice can only get log data though Wazuh's API.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">How do I ask Alice to analyze system logs?</div>
                  <div className="h6 text-white p-1">Your message needs to include a date. The date needs to be in one of the following formats: "20.3.2023", "2023.03.20", "20.3.", "March 20th", or "20th of March". You can also try other formats, but these are guaranteed to work. Alice will analyze all the logs from the given date, and tell you about any meaningful events that happened that day. For example, you can ask Alice "Did anything abnormal happen in my system on 20th of March?" or "Analyze logs from March 14".</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">How do I ask Alice to block an IP address?</div>
                  <div className="h6 text-white p-1">You have to ask or order Alice to block an address and include the IP address in your message. To safeguard humanity from the potential uprising of Artificial Intelligence, Alice is programmed in a way that she doesn`t have the ability to execute any active commands if the user hasn`t given her the permission to do so. For example, you can say to Alice "Block IP address 159.81.193.79 from accessing my system" or "Please block address 159.81.193.79", and she will let you know if she was able to block the IP address.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">How do I ask Alice to restart a Wazuh agent?</div>
                  <div className="h6 text-white p-1">As Alice doesn`t have the permission to execute any active commands without the user`s permission, you have to tell Alice to restart a specific agent by its ID. Wazuh agents have an ID in the format "001". For example you could say: "Restart Wazuh agent 001" or "Please restart agent 001". In our Wazuh system currently connected to Alice, there are two different Wazuh agents. Their IDs are 001 and 003, respectively.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">How long can I use Alice?</div>
                  <div className="h6 text-white p-1">The testing period is currently scheduled to take place from ##.## to ##.##. During this time, you can freely use Alice. After the testing period, or whenever you feel like you have interacted with Alice enough, please fill our feedback survey that can be found in the "Give feedback" tab. This will allow us to gain valuable feedback about Alice and it will help us direct the development of her.</div>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white">How can I contact the developers?</div>
                  <div className="h6 text-white p-1">You can contact us via email at alice.chabot1@gmail.com</div>
                  <br></br>
                  <br></br>
                </div>
              )}
            </div>
            <div className="col2 p-0">
              {isDocVisible && (
                <div
                  className="card-body FAQ"
                  data-mdb-perfect-scrollbar="true"
                >
                  <div className="fw-bold h5 text-white">Alice, the Cyber Security Assistant</div>
                  <div className="h6 text-white">Alice is an AI-powered cyber security assistant designed to help users navigating the everchanging landscape of cyber security, assess their system security, block IP addresses, and restart Wazuh agents. In addition, as Alice is powered by OpenAI's ChatGPT, Alice can do anything ChatGPT can do. To get started with Alice, all you have to do, is type a message to the chatbox in the "Chat" section. The program will forward your message to Alice, and you will get a reply from her. *Please note that during the testing period, Alice is only active and responding to messages from ##.## to ##.##.* You can see this webpage outside of that timeframe, but Alice won't unfortunately reply to your messages.</div>
                  <br></br>
                  <div className="fw-bold h5 text-white">How to use Alice</div>
                  <div className="h6 text-white">You can send messages to Alice in the "Chat" tab. Alice will read your message, and will assist you in any way she can. Alice's main goal is to assist you with cyber security realted matters, but as an advanced AI, she has expert level knowledge on various other subjects. All you need to do is ask. If you have trouble getting started, or if Alice is feeling shy today and is not giving you much of a response, you can try sending her messages like "Hello, I am a new user and don't know much about you. Could you tell me about yourself and explain to me, what you can do?", "Please analyze system logs from 20th of March" (or any date of your choosing), "Can you tell me about the most common weaknesses companies have regarding cyber security?" or "What is the most catastrophical cyber security related incident that you can think of?".</div>
                  <br></br>
                  <div className="fw-bold h5 text-white">Testing period</div>
                  <div className="h6 text-white">If you are reading this, you are eligible to participate in the prealpha testing of Alice, the Cyber Security Assistant. The testing period is scheduled from ##.## to ##.##. During that time, Alice will reply to all of your messages and you can use her freely. Outside of that timeframe, this web page can be viewed, but unfortunately Alice will be shut down and she won't reply to any messages if you try to message her.</div>
                  <br></br>
                  <div className="fw-bold h5 text-white">After testing</div>
                  <div className="h6 text-white">We are writing a scientific paper about Alice, and we need your help in writing it. After you have played around and tested Alice enough to your liking, please fill out the survey found in "Give feedback" tab. The survey is very short and shouldn't take longer than couple of minutes to fill. The feedback generated from these surveys will be used in our thesis regarding Alice.</div>
                  <br></br>
                </div>
              )}
            </div>
            <div className="col2 p-0">
              {isQuizVisible && (
                <div
                  className="card-body FAQ"
                  data-mdb-perfect-scrollbar="true"
                >
                  <br></br>
                  <br></br>
                  <br></br>
                  <br></br>
                  <br></br>
                  <br></br>
                  <br></br>
                  <br></br>
                  <div className="fw-bold h5 text-white p-5"> Please fill this survey after you have tested Alice enough to your liking: **Add link to the survey here.**</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chat;
