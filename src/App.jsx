import { useState } from 'react';
import Button from './components/button';
import Inputs from './components/Inputs';
import './App.css';

function App() {
  const [fileName, setFileName] = useState('');
  const [selectedValue, setSelectedValue] = useState('good');
  const [isRecording, setIsRecording] = useState(false);
  const [message, setMessage] = useState('');

  const handleStartRecording = async () => {
    if (!fileName) {
      setMessage('Please enter a filename.');
      return;
    }
    setMessage('Starting...');
    try {
      const response = await fetch('http://127.0.0.1:5000/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename: fileName, label: selectedValue }),
      });
      const data = await response.json();
      if (response.ok) {
        setIsRecording(true);
        setMessage(data.message);
      } else {
        setMessage(`Error: ${data.message}`);
      }
    } catch (error) {
      setMessage(`Error: Could not connect to server. Is it running?`);
    }
  };

  const handleStopRecording = async () => {
    setMessage('Stopping...');
    try {
      const response = await fetch('http://127.0.0.1:5000/stop', {
        method: 'POST',
      });
      const data = await response.json();
      if (response.ok) {
        setIsRecording(false);
        setMessage(data.message);
      } else {
        setMessage(`Error: ${data.message}`);
      }
    } catch (error) {
      setMessage(`Error: Could not connect to server.`);
    }
  };

  return (
    <div className='app-container'>
      <p className='app-title'>ESP-32 WEB INTERFACE</p>
      <Inputs 
        fileName={fileName}
        onFileNameChange={(e) => setFileName(e.target.value)}
        selectedValue={selectedValue}
        onSelectedValueChange={(e) => setSelectedValue(e.target.value)}
      />
      <Button 
        Value="start recording" 
        name='start-butt' 
        onClick={handleStartRecording} 
        disabled={isRecording} 
      />
      <Button 
        Value="stop recording" 
        name='stop-butt' 
        onClick={handleStopRecording} 
        disabled={!isRecording} 
      />
      {message && <p className="status-message">{message}</p>}
    </div>
  );
}

export default App;
