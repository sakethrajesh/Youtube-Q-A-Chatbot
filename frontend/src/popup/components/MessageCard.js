import * as React from 'react';

export default function MessageCard({message, index}) {
    return (
        <>
            { index%2 == 0 ?
                <div class="card" style={{ margin: '4px', textAlign: 'right' }}> 
                    <div class="card-body">
                        {message}
                    </div>
                </div>
                : 
                <div style={{ margin: '4px', textAlign: 'left' }}>
                    <div >
                        {message}
                    </div>
                </div>
            }
                
        </>
    );
}
