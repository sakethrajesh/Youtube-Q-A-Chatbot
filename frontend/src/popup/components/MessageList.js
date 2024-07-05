import React from 'react'
import MessageCard from './MessageCard'

function MessageList({ messages }) {
    return (
        <div class="overflow-auto" style={{height: '525px'}}>
            {messages.map((message, index) => (
                <div key={index}>
                    <MessageCard message={message['content']} index={index}/>
                </div>
            ))}
        </div>
    )
}

export default MessageList