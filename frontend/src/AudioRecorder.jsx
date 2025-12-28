import { useState, useRef } from 'react';
import { Mic, Square, Loader2 } from 'lucide-react';
import axios from 'axios';

const AudioRecorder = ({ onTranscriptionComplete }) => {
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
        handleUpload(audioBlob);
        
        // Stop all tracks to turn off the red mic light
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (err) {
      console.error("Mic Error:", err);
      alert("Could not access microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const handleUpload = async (audioBlob) => {
    setProcessing(true);
    const formData = new FormData();
    formData.append("file", audioBlob, "voice_note.wav");

    try {
      const API_URL = import.meta.env.VITE_API_URL;
      const response = await axios.post(`${API_URL}/analyze-voice`, formData);
      
      if (response.data.status === 'success') {
        // Pass the translated text back to the parent component
        onTranscriptionComplete(response.data.detected_text);
      }
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
      {processing ? (
        <span className="flex items-center gap-2 text-sm text-gray-500 animate-pulse">
          <Loader2 size={16} className="animate-spin" /> Translating...
        </span>
      ) : !recording ? (
        <button
          onClick={startRecording}
          className="flex items-center gap-2 bg-blue-50 text-blue-600 px-4 py-2 rounded-full text-sm font-semibold hover:bg-blue-100 transition"
        >
          <Mic size={16} /> Speak Features
        </button>
      ) : (
        <button
          onClick={stopRecording}
          className="flex items-center gap-2 bg-red-50 text-red-600 px-4 py-2 rounded-full text-sm font-semibold hover:bg-red-100 transition animate-pulse"
        >
          <Square size={16} fill="currentColor" /> Stop & Send
        </button>
      )}
    </div>
  );
};

export default AudioRecorder;