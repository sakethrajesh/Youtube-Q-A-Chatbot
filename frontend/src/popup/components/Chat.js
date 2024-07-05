import React from 'react'
import MessageList from './MessageList'

function Chat({ url }) {
    const [messages, setMessages] = React.useState([])

    function handleFormSubmit(event) {
        event.preventDefault();
        // Get the question input value
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
                // Update the messages state with the response data
                setMessages((prevMessages) => ([...prevMessages, {
                    "role": "assistant",
                    "content": data['text']
                }]));

                console.log(messages)
            })
            .catch(error => {
                console.error('Error:', error);
            });

        // Clear the question input value
        questionInput.value = '';
    }


    return (
        <>

            <div>url: {url}</div>

            <MessageList messages={messages} />

            <form class="row" onSubmit={handleFormSubmit} style={{ margin: '2px' }}>
                <div class="col">
                    <label for="inputPassword2" class="visually-hidden">Question</label>
                    <input class="form-control" placeholder="Question" />
                </div>
                {/* <div class="col">
                    <button type="submit" class="btn btn-primary">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-right-square" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M15 2a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1zM0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm4.5 5.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5z" />
                        </svg>
                    </button>
                </div> */}
            </form>
        </>
    )
}

export default Chat