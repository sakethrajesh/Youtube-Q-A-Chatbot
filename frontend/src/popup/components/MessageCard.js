import * as React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MessageCard({message, index}) {
    return (
        <>
            { index%2 == 0 ?
                <div class="card text-bg-primary" style={{ margin: '4px', textAlign: 'left' }}> 
                        <div class="card-header">Question</div>
                        <div class="card-body">
                            <p class="card-text"><ReactMarkdown>{message}</ReactMarkdown></p>
                        </div>
                </div>
                : 
                <div class="card border-dark mb-3" style={{ margin: '4px', textAlign: 'left' }}>
                    <div class="card-header">Answer</div>
                    <div class="card-body">
                        <p class="card-text"><ReactMarkdown>{message}</ReactMarkdown></p>
                    </div>
                </div>

            }
                
        </>
    );
}
