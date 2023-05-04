import "./ChatMessage.css";
import AliceIcon from "../assets/alice-icon-2.png";
import UserIcon from "../assets/user.png";

function ChatMessage({ message, onSelectItem }) {
  return (
    <div
      className="message d-flex flex-row justify-content-start p-1 align-items-center"
      onClick={() => {
        onSelectItem(message);
      }}
    >
      {message.name === "Alice" ? (
        <img src={AliceIcon} alt="avatar 2" />
      ) : (
        <img src={UserIcon} alt="avatar 1" />
      )}
      <div className="p-3 ms-3">
        <p className="fw-bold mb-0 text-white">{message.name}</p>
        <p className="small mb-0 text-white">{message.msg}</p>
      </div>
    </div>
  );
}

export default ChatMessage;
