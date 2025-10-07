import { useState, useEffect, useRef } from 'react';

// Check for browser support at the module level
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const isSpeechRecognitionSupported = !!SpeechRecognition;

export const useSpeechRecognition = () => {
    const [text, setText] = useState('');
    const [isListening, setIsListening] = useState(false);
    
    // useRef is used to hold the recognition instance, which doesn't need to trigger re-renders
    const recognitionRef = useRef(null);

    useEffect(() => {
        if (!isSpeechRecognitionSupported) {
            console.error("Speech recognition is not supported in this browser.");
            return;
        }

        // Initialize the recognition instance
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        // Event handlers for the recognition instance
        recognition.onstart = () => {
            setIsListening(true);
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setText(transcript);
        };
        
        // Store the instance in the ref
        recognitionRef.current = recognition;

        // Cleanup function to stop recognition if the component unmounts
        return () => {
            recognition.stop();
        };
    }, []); // Empty dependency array ensures this runs only once on mount

    const startListening = () => {
        if (recognitionRef.current && !isListening) {
            setText(''); // Clear previous text
            recognitionRef.current.start();
        }
    };

    return {
        text,
        isListening,
        startListening,
        isSpeechRecognitionSupported,
    };
};