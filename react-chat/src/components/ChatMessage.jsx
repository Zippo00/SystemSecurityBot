import './ChatMessage.css'
function ChatMessage({ message, onSelectItem }) {
    return (
        <div
            className='message d-flex flex-row justify-content-start p-3'
            onClick={() => {
                onSelectItem(message)
            }}
        >
            {message.name === 'user' ? (
                <img
                    src='https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp'
                    alt='avatar 1'
                />
            ) : (
                <img
                    src='https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava2-bg.webp'
                    alt='avatar 2'
                />
            )}
            <div className='p-3 ms-3'>
                <p className='small mb-0 text-white'>{message.msg}</p>
            </div>
        </div>
    )
}

export default ChatMessage
