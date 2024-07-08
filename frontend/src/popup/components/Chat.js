import React from 'react'
import MessageList from './MessageList'

function Chat({ url }) {
    const [messages, setMessages] = React.useState([])

    function handleFormSubmit(event) {
        event.preventDefault();
        const questionInput = document.querySelector('input.form-control');
        const question = questionInput.value;

        const message = {
            "role": "user",
            "content": question
        }

        setMessages((prevMessages) => ([...prevMessages, message]));
        
        console.log(JSON.stringify({ "messages": [...messages, message], "video_id": url }))


        fetch('http://localhost:5001/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "messages": [...messages, message], "video_id": url })
        })
            .then(response => response.json())
            .then(data => {
                console.log("ai resp: ", data['text'])
                setMessages((prevMessages) => ([...prevMessages, {
                    "role": "assistant",
                    "content": data['text']
                }]));

                console.log(messages)
            })
            .catch(error => {
                console.error('Error:', error);
            });

        questionInput.value = '';
    }


    return (
        <div>
            <MessageList messages={messages} />

            <form class="row" onSubmit={handleFormSubmit} style={{ margin: '2px'}}>
                    <label for="inputPassword2" class="visually-hidden">Question</label>
                    <input class="form-control" placeholder="Question" />
            </form>
        </div>
    )
}

export default Chat