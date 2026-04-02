import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import VoiceRecorder from './VoiceRecorder';
import { Send, Volume2, StopCircle } from 'lucide-react';
import { useLanguage } from '../../contexts/LanguageContext';
import api from '../../api/axios';
import toast from 'react-hot-toast';

const ChatInterface = ({ sessionId, disease, confidence, initialQA = [] }) => {
  const [messages, setMessages] = useState(initialQA);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Track which message index is currently playing (-1 = none)
  const [playingIndex, setPlayingIndex] = useState(-1);

  const messagesEndRef = useRef(null);
  const { language } = useLanguage();
  const initialQALoadedRef = useRef(false);

  // ONE global audio ref — only one audio can ever play at a time
  const audioRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (initialQA.length > 0 && !initialQALoadedRef.current) {
      setMessages(initialQA);
      initialQALoadedRef.current = true;
      scrollToBottom();
    }
  }, [initialQA]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Stop audio when component unmounts (e.g. user switches image)
  useEffect(() => {
    return () => stopAudio();
  }, []);

  // --------------------------------------------------
  // Core audio helpers
  // --------------------------------------------------

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    setPlayingIndex(-1);
  };

  const playAudio = (audioUrl, messageIndex) => {
    // If this message is already playing, stop it
    if (playingIndex === messageIndex) {
      stopAudio();
      return;
    }

    // Stop whatever is currently playing first
    stopAudio();

    if (!audioUrl) return;

    const audio = new Audio(audioUrl);
    audioRef.current = audio;

    audio.play().catch((e) => {
      console.log('Autoplay blocked:', e);
      toast('Tap the 🔊 button to hear the answer', { icon: '🔊', duration: 3000 });
      audioRef.current = null;
      setPlayingIndex(-1);
    });

    audio.onplay = () => setPlayingIndex(messageIndex);

    audio.onended = () => {
      audioRef.current = null;
      setPlayingIndex(-1);
    };

    audio.onerror = () => {
      audioRef.current = null;
      setPlayingIndex(-1);
    };
  };

  // --------------------------------------------------
  // Sending questions
  // --------------------------------------------------

  const handleSendText = async () => {
    if (!inputText.trim() || isLoading) return;
    const question = inputText.trim();
    setInputText('');
    await sendQuestion(question);
  };

  const handleVoiceRecorded = async (audioBlob) => {
    await sendQuestion(audioBlob, true);
  };

  const sendQuestion = async (input, isAudio = false) => {
    // Stop any playing audio before sending new question
    stopAudio();
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
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
        responseType: 'json'
      });

      const newMessage = {
        question: typeof input === 'string' ? input : '🎤 Voice message',
        answer: response.data.answer,
        audioUrl: response.data.audio_url,
        timestamp: new Date()
      };

      setMessages(prev => {
        const updated = [...prev, newMessage];

        // Autoplay the new answer — index is last item
        if (response.data.audio_url) {
          const newIndex = updated.length - 1;
          // Small delay so state settles before playing
          setTimeout(() => playAudio(response.data.audio_url, newIndex), 100);
        }

        return updated;
      });

    } catch (error) {
      console.error('Send question error:', error);
      toast.error('Failed to get response');
    } finally {
      setIsLoading(false);
    }
  };

  // --------------------------------------------------
  // Render
  // --------------------------------------------------

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

          {/* Global stop button — only visible while audio is playing */}
          {playingIndex !== -1 && (
            <button
              onClick={stopAudio}
              className="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-600 rounded-full text-xs font-medium hover:bg-red-200 transition"
            >
              <StopCircle className="w-3 h-3" />
              Stop Audio
            </button>
          )}
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
          messages.map((msg, idx) => {
            const isThisPlaying = playingIndex === idx;
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-2"
              >
                {/* Question bubble */}
                <div className="flex justify-end">
                  <div className="bg-primary-500 text-white rounded-2xl rounded-tr-none px-4 py-2 max-w-[80%]">
                    <p className="text-sm break-words">
                      {msg.question || msg.question_user || 'Question'}
                    </p>
                  </div>
                </div>

                {/* Answer bubble */}
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-tl-none px-4 py-2 max-w-[80%]">
                    <p className="text-sm break-words">
                      {msg.answer || msg.answer_user || msg.answer_en || 'Response'}
                    </p>

                    {msg.audioUrl && (
                      <button
                        onClick={() => playAudio(msg.audioUrl, idx)}
                        className={`mt-2 flex items-center space-x-1 transition-colors ${isThisPlaying
                            ? 'text-red-500 hover:text-red-600'
                            : 'text-primary-600 hover:text-primary-700'
                          }`}
                      >
                        {isThisPlaying
                          ? <><StopCircle className="w-4 h-4" /><span className="text-xs">Stop</span></>
                          : <><Volume2 className="w-4 h-4" /><span className="text-xs">Play Audio</span></>
                        }
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })
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

      {/* Input */}
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