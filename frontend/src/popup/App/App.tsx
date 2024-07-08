import React, { useEffect, useState } from 'react';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";
import './App.css';
import Chat from '../components/Chat';

function App() {
  const [url, setUrl] = useState<string>("");
  const [loaded, setLoaded] = useState<boolean>(false);
  const [loading, setLoadeding] = useState<boolean>(false);

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
    setLoadeding(true);
    chrome.runtime.sendMessage({ type: 'GET_CURRENT_TAB_URL' }, (response) => {
      setUrl(extractVideoID(response.url));

      console.log(extractVideoID(response.url))

      fetch("http://localhost:5001/api/load_transcript/" + extractVideoID(response.url))
        .then(response => response.json())
        .then(data => {
          console.log(data);
          setLoaded(true);
          setLoadeding(false);
        })
        .catch(error => {

        });
    });


  }


  return (
    <>
      {
        loaded == true ?
          (
            <div>
              <Chat url={url} />
            </div>
          )
          :
          (
            <div className="d-flex justify-content-center align-items-center vh-100 bg-gray-200">
              {
                loading == false ?
                  (
                    <button type="button" onClick={() => onSubmited()} className="btn btn-primary">Get Started</button>
                  )
                  :
                  (
                    <button className="btn btn-primary" type="button" disabled>
                      <span className="spinner-border spinner-border-sm" aria-hidden="true"></span>
                      <span role="status"> Loading...</span>
                    </button>
                  )
              }
            </div>
          )
      }
    </>
  );
}

export default App;