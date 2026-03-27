import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import VoiceRecorder from './VoiceRecorder';
import { Send, Volume2 } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const ChatInterface = ({ sessionId, disease, confidence, initialQA = [] }) => {
  const [messages, setMessages] = useState(initialQA);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { language } = useLanguage();
  
  // ✅ Add this ref to prevent infinite loop
  const initialQALoadedRef = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // ✅ FIXED: Only update messages once when initialQA is first received
  useEffect(() => {
    if (initialQA.length > 0 && !initialQALoadedRef.current) {
      console.log('ChatInterface received initialQA:', initialQA.length, 'items');
      setMessages(initialQA);
      initialQALoadedRef.current = true;
      scrollToBottom();
    }
  }, [initialQA]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ✅ Define handleSendText
  const handleSendText = async () => {
    if (!inputText.trim() || isLoading) return;

    const question = inputText.trim();
    setInputText('');
    await sendQuestion(question);
  };

  // ✅ Define handleVoiceRecorded
  const handleVoiceRecorded = async (audioBlob) => {
    await sendQuestion(audioBlob, true);
  };

  // ✅ Define playAudio
  const playAudio = (audioUrl) => {
    if (!audioUrl) return;
    
    const audio = new Audio(audioUrl);
    
    const playPromise = audio.play();
    
    if (playPromise !== undefined) {
      playPromise.catch(error => {
        console.log('Auto-play blocked:', error);
        toast('Tap the 🔊 button to hear the answer', {
          icon: '🔊',
          duration: 3000
        });
      });
    }
  };

  // ✅ Define sendQuestion
  const sendQuestion = async (input, isAudio = false) => {
    setIsLoading(true);

    const formData = new FormData();
    if (isAudio) {
      formData.append('audio', input, 'recording.wav');
    } else {
      formData.append('question', input);
    }
    formData.append('language', language);

    try {
      const response = await api.post('/plant/ask', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000,
        responseType: 'json'
      });

      const newMessage = {
        question: typeof input === 'string' ? input : '🎤 Voice message',
        answer: response.data.answer,
        audioUrl: response.data.audio_url,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, newMessage]);

      // Auto-play the audio response
      if (response.data.audio_url) {
        const audio = new Audio(response.data.audio_url);
        audio.oncanplaythrough = () => {
          audio.play().catch(e => console.log('Auto-play blocked:', e));
        };
        audio.onerror = () => console.error('Audio load failed');
      }
    } catch (error) {
      console.error('Send question error:', error);
      toast.error('Failed to get response');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">Chat with Assistant</h3>
            <p className="text-sm text-gray-600 mt-1">
              Disease: {disease} ({Math.round(confidence * 100)}% confidence)
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>Ask me anything about {disease}</p>
            <p className="text-sm mt-2">Try: "How to treat this?" or "Will it spread?"</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-2"
            >
              {/* Question */}
              <div className="flex justify-end">
                <div className="bg-primary-500 text-white rounded-2xl rounded-tr-none px-4 py-2 max-w-[80%]">
                  <p className="text-sm break-words">{msg.question || msg.question_user || 'Question'}</p>
                </div>
              </div>

              {/* Answer */}
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-tl-none px-4 py-2 max-w-[80%]">
                  <p className="text-sm break-words">{msg.answer || msg.answer_user || msg.answer_en || 'Response'}</p>
                  {msg.audioUrl && (
                    <button
                      onClick={() => playAudio(msg.audioUrl)}
                      className="mt-2 flex items-center space-x-1 text-primary-600 hover:text-primary-700 transition-colors"
                    >
                      <Volume2 className="w-4 h-4" />
                      <span className="text-xs">Play Audio</span>
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
            placeholder="Type your question..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition"
            disabled={isLoading}
          />
          
          <VoiceRecorder
            onRecordingComplete={handleVoiceRecorded}
            disabled={isLoading}
          />

          <button
            onClick={handleSendText}
            disabled={!inputText.trim() || isLoading}
            className="p-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;

// import { useState, useRef, useEffect } from 'react';
// import { motion, AnimatePresence } from 'framer-motion';
// import VoiceRecorder from './VoiceRecorder';
// import AudioMessage from './AudioMessage';
// import { Send, Mic, MicOff, Volume2 } from 'lucide-react';
// import { useLanguage } from '../../contexts/LanguageContext';
// import api from '../../api/axios';
// import toast from 'react-hot-toast';

// const ChatInterface = ({ sessionId, disease, confidence, initialQA = [] }) => {
//   const [messages, setMessages] = useState(initialQA);
//   const [inputText, setInputText] = useState('');
//   const [isRecording, setIsRecording] = useState(false);
//   const [isLoading, setIsLoading] = useState(false);
//   const [isSpeaking, setIsSpeaking] = useState(false);
//   const messagesEndRef = useRef(null);
//   const { language } = useLanguage();

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   // ✅ FIX: Update messages when initialQA changes (for history chat)
//   useEffect(() => {
//     console.log('ChatInterface received initialQA:', initialQA.length, 'items');
//     setMessages(initialQA);
//     scrollToBottom();
//   }, [initialQA]);  // ← This is the key! Re-run when initialQA changes

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const handleSendText = async () => {
//     if (!inputText.trim() || isLoading) return;

//     const question = inputText.trim();
//     setInputText('');
//     await sendQuestion(question);
//   };

//   const handleVoiceRecorded = async (audioBlob) => {
//     await sendQuestion(audioBlob, true);
//   };

//   const sendQuestion = async (input, isAudio = false) => {
//   setIsLoading(true);

//   const formData = new FormData();
//   if (isAudio) {
//     formData.append('audio', input, 'recording.wav');
//   } else {
//     formData.append('question', input);
//   }
//   formData.append('language', language);

//   try {
//     const response = await api.post('/plant/ask', formData, {
//       headers: {
//         'Content-Type': 'multipart/form-data',
//       },
//       responseType: 'json'
//     });

//     const newMessage = {
//       question: typeof input === 'string' ? input : 'Voice message',
//       answer: response.data.answer,
//       audioUrl: response.data.audio_url,
//       timestamp: new Date()
//     };
//     setMessages(prev => [...prev, newMessage]);

//     // ✅ FIX: Play audio with better error handling
//     if (response.data.audio_url) {
//       console.log('Attempting to play audio from URL:', response.data.audio_url);
      
//       // Create audio element
//       const audio = new Audio(response.data.audio_url);
      
//       // Add event listeners for debugging
//       audio.addEventListener('canplaythrough', () => {
//         console.log('Audio can play through');
//       });
      
//       audio.addEventListener('error', (e) => {
//         console.error('Audio error:', e);
//         toast.error('Audio playback failed');
//       });
      
//       audio.addEventListener('play', () => {
//         console.log('Audio playing');
//       });
      
//       // Try to play
//       const playPromise = audio.play();
      
//       if (playPromise !== undefined) {
//         playPromise.catch(error => {
//           console.error('Playback failed:', error);
//           // Most browsers require user interaction first
//           toast('Tap anywhere to enable audio', { icon: '🔊' });
//         });
//       }
//     }
//   } catch (error) {
//     console.error('Send question error:', error);
//     toast.error('Failed to get response');
//   } finally {
//     setIsLoading(false);
//   }
// };

//   return (
//     <div className="flex flex-col h-full bg-white rounded-2xl shadow-lg">
//       {/* Header */}
//       <div className="p-4 border-b border-gray-100">
//         <div className="flex items-center justify-between">
//           <div>
//             <h3 className="font-semibold text-gray-800">Chat with Assistant</h3>
//             <p className="text-sm text-gray-600 mt-1">
//               Disease: {disease} ({Math.round(confidence * 100)}% confidence)
//             </p>
//           </div>
//           <button
//             onClick={() => setIsSpeaking(!isSpeaking)}
//             className={`p-2 rounded-full transition ${
//               isSpeaking ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-600'
//             }`}
//           >
//             <Volume2 className="w-5 h-5" />
//           </button>
//         </div>
//       </div>

//       {/* Messages */}
//       <div className="flex-1 overflow-y-auto p-4 space-y-4">
//         {messages.length === 0 ? (
//           <div className="text-center text-gray-500 py-8">
//             <p>Ask me anything about {disease}</p>
//             <p className="text-sm mt-2">Try: "How to treat this?" or "Will it spread?"</p>
//           </div>
//         ) : (
//           messages.map((msg, idx) => (
//             <motion.div
//               key={idx}
//               initial={{ opacity: 0, y: 10 }}
//               animate={{ opacity: 1, y: 0 }}
//               className="space-y-2"
//             >
//               {/* Question */}
//               <div className="flex justify-end">
//                 <div className="bg-primary-500 text-white rounded-2xl rounded-tr-none px-4 py-2 max-w-[80%]">
//                   <p className="text-sm">{msg.question || msg.question_user || 'Question'}</p>
//                 </div>
//               </div>

//               {/* Answer */}
//               <div className="flex justify-start">
//                 <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-tl-none px-4 py-2 max-w-[80%]">
//                   <p className="text-sm">{msg.answer || msg.answer_user || msg.answer_en || 'Response'}</p>
//                   {msg.audioUrl && (
//                     <div className="mt-2">
//                       <button
//                         onClick={() => {
//                           const audio = new Audio(msg.audioUrl);
//                           audio.play().catch(e => console.log('Play error:', e));
//                         }}
//                         className="flex items-center space-x-1 text-primary-600 hover:text-primary-700"
//                       >
//                         <Volume2 className="w-4 h-4" />
//                         <span className="text-xs">Play Audio</span>
//                       </button>
//                     </div>
//                   )}
//                 </div>
//               </div>
//             </motion.div>
//           ))
//         )}
//         {isLoading && (
//           <div className="flex justify-start">
//             <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3">
//               <div className="flex space-x-1">
//                 <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
//                 <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
//                 <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
//               </div>
//             </div>
//           </div>
//         )}
//         <div ref={messagesEndRef} />
//       </div>

//       {/* Input Area */}
//       <div className="p-4 border-t border-gray-100">
//         <div className="flex items-center space-x-2">
//           <input
//             type="text"
//             value={inputText}
//             onChange={(e) => setInputText(e.target.value)}
//             onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
//             placeholder="Type your question..."
//             className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition"
//             disabled={isLoading}
//           />
          
//           <VoiceRecorder
//             onRecordingComplete={handleVoiceRecorded}
//             disabled={isLoading}
//           />

//           <button
//             onClick={handleSendText}
//             disabled={!inputText.trim() || isLoading}
//             className="p-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
//           >
//             <Send className="w-5 h-5" />
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ChatInterface;


// import { useState, useRef, useEffect } from 'react';
// import { motion } from 'framer-motion';
// import VoiceRecorder from './VoiceRecorder';
// import { Send, Volume2 } from 'lucide-react';
// import { useLanguage } from '../../contexts/LanguageContext';
// import api from '../../api/axios';
// import toast from 'react-hot-toast';

// const ChatInterface = ({ sessionId, disease, confidence, initialQA = [] }) => {
//   const [messages, setMessages] = useState(initialQA);
//   const [inputText, setInputText] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const messagesEndRef = useRef(null);
//   const { language } = useLanguage();
  
//   // ✅ Add this ref to prevent infinite loop
//   const initialQALoadedRef = useRef(false);

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   // ✅ FIXED: Only update messages once when initialQA is first received
//   useEffect(() => {
//     if (initialQA.length > 0 && !initialQALoadedRef.current) {
//       console.log('ChatInterface received initialQA:', initialQA.length, 'items');
//       setMessages(initialQA);
//       initialQALoadedRef.current = true;
//       scrollToBottom();
//     }
//   }, [initialQA]);

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   // ... rest of your code remains the same

//   const handleVoiceRecorded = async (audioBlob) => {
//     await sendQuestion(audioBlob, true);
//   };

//   // Function to play audio with user interaction fallback
//   const playAudio = (audioUrl) => {
//     if (!audioUrl) return;
    
//     const audio = new Audio(audioUrl);
    
//     const playPromise = audio.play();
    
//     if (playPromise !== undefined) {
//       playPromise.catch(error => {
//         console.log('Auto-play blocked:', error);
//         // Show a toast asking user to click the play button
//         toast('Tap the 🔊 button to hear the answer', {
//           icon: '🔊',
//           duration: 3000
//         });
//       });
//     }
//   };

//   const sendQuestion = async (input, isAudio = false) => {
//     setIsLoading(true);

//     const formData = new FormData();
//     if (isAudio) {
//       formData.append('audio', input, 'recording.wav');
//     } else {
//       formData.append('question', input);
//     }
//     formData.append('language', language);

//     try {
//       const response = await api.post('/plant/ask', formData, {
//         headers: {
//           'Content-Type': 'multipart/form-data',
//         },
//         timeout: 30000,
//         responseType: 'json'
//       });

//       const newMessage = {
//         question: typeof input === 'string' ? input : '🎤 Voice message',
//         answer: response.data.answer,
//         audioUrl: response.data.audio_url,
//         timestamp: new Date()
//       };
//       setMessages(prev => [...prev, newMessage]);

//       // Auto-play the audio response
//       if (response.data.audio_url) {
//       const audio = new Audio(response.data.audio_url);
//       audio.oncanplaythrough = () => {
//         audio.play().catch(e => console.log('Auto-play blocked:', e));
//       };
//       audio.onerror = () => console.error('Audio load failed');
//     }
//     } catch (error) {
//       console.error('Send question error:', error);
//       toast.error('Failed to get response');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="flex flex-col h-full bg-white rounded-2xl shadow-lg">
//       {/* Header */}
//       <div className="p-4 border-b border-gray-100">
//         <div className="flex items-center justify-between">
//           <div>
//             <h3 className="font-semibold text-gray-800">Chat with Assistant</h3>
//             <p className="text-sm text-gray-600 mt-1">
//               Disease: {disease} ({Math.round(confidence * 100)}% confidence)
//             </p>
//           </div>
//         </div>
//       </div>

//       {/* Messages */}
//       <div className="flex-1 overflow-y-auto p-4 space-y-4">
//         {messages.length === 0 ? (
//           <div className="text-center text-gray-500 py-8">
//             <p>Ask me anything about {disease}</p>
//             <p className="text-sm mt-2">Try: "How to treat this?" or "Will it spread?"</p>
//           </div>
//         ) : (
//           messages.map((msg, idx) => (
//             <motion.div
//               key={idx}
//               initial={{ opacity: 0, y: 10 }}
//               animate={{ opacity: 1, y: 0 }}
//               className="space-y-2"
//             >
//               {/* Question */}
//               <div className="flex justify-end">
//                 <div className="bg-primary-500 text-white rounded-2xl rounded-tr-none px-4 py-2 max-w-[80%]">
//                   <p className="text-sm break-words">{msg.question || msg.question_user || 'Question'}</p>
//                 </div>
//               </div>

//               {/* Answer */}
//               <div className="flex justify-start">
//                 <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-tl-none px-4 py-2 max-w-[80%]">
//                   <p className="text-sm break-words">{msg.answer || msg.answer_user || msg.answer_en || 'Response'}</p>
//                   {msg.audioUrl && (
//                     <button
//                       onClick={() => playAudio(msg.audioUrl)}
//                       className="mt-2 flex items-center space-x-1 text-primary-600 hover:text-primary-700 transition-colors"
//                     >
//                       <Volume2 className="w-4 h-4" />
//                       <span className="text-xs">Play Audio</span>
//                     </button>
//                   )}
//                 </div>
//               </div>
//             </motion.div>
//           ))
//         )}
//         {isLoading && (
//           <div className="flex justify-start">
//             <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3">
//               <div className="flex space-x-1">
//                 <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
//                 <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
//                 <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
//               </div>
//             </div>
//           </div>
//         )}
//         <div ref={messagesEndRef} />
//       </div>

//       {/* Input Area */}
//       <div className="p-4 border-t border-gray-100">
//         <div className="flex items-center space-x-2">
//           <input
//             type="text"
//             value={inputText}
//             onChange={(e) => setInputText(e.target.value)}
//             onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
//             placeholder="Type your question..."
//             className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition"
//             disabled={isLoading}
//           />
          
//           <VoiceRecorder
//             onRecordingComplete={handleVoiceRecorded}
//             disabled={isLoading}
//           />

//           <button
//             onClick={handleSendText}
//             disabled={!inputText.trim() || isLoading}
//             className="p-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
//           >
//             <Send className="w-5 h-5" />
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ChatInterface;