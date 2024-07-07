import * as React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageCard({message, index}) {
    return (
        <>
            { index%2 == 0 ?
                <div class="card" style={{ margin: '4px', textAlign: 'right' }}> 
                    <div class="card-body">
                        <ReactMarkdown>{message}</ReactMarkdown>
                    </div>
                </div>
                : 
                <div style={{ margin: '4px', textAlign: 'left' }}>
                    <div >
                        <ReactMarkdown>{message}</ReactMarkdown>
                    </div>
                </div>
            }
                
        </>
    );
}
