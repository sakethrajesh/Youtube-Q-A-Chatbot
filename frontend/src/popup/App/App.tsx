import React, { useEffect, useState } from 'react';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";
import './App.css';
import Chat from '../components/Chat';

function App() {
  const [url, setUrl] = useState<string>("");
  const [loaded, setLoaded] = useState<boolean>(false);

  const getCurrentTabUrl = () => {
    chrome.runtime.sendMessage({ type: 'GET_CURRENT_TAB_URL' }, (response) => {
      setUrl(extractVideoID(response.url));
    });
  };

  function extractVideoID(url: string) {
    const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\s*[^\/\n\s]+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regex);
    return match ? match[1] : "";
  }

  const onSubmited = () => {
    chrome.runtime.sendMessage({ type: 'GET_CURRENT_TAB_URL' }, (response) => {
      setUrl(extractVideoID(response.url));

      console.log(extractVideoID(response.url))

      fetch("http://localhost:5001/api/load_transcript/" + extractVideoID(response.url))
        .then(response => response.json())
        .then(data => {
          console.log(data);
          setLoaded(true);
        })
        .catch(error => {
          // Handle any errors here
        });
    });


  }


  return (
    <>
      {
        loaded == true ?
          (<div className="App">
            <Chat url={url} />
          </div>)
          :
          (
            <div className="bg-info p-5">
              <p className="">
                load the video
              </p>
              <a
                className="btn btn-primary"
                data-bs-toggle="collapse"
                role="button"
                onClick={() => onSubmited()}
              >
                Start
              </a>
            </div>
          )

      }
    </>

  );
}

export default App;