import { useState, useEffect, useRef } from 'react';
import { Sparkles, Volume2, StopCircle, RefreshCw } from 'lucide-react';
import api from '../../api/axios';
import { useLanguage } from '../../contexts/LanguageContext';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

const SummaryPanel = ({ sessionId, imageId }) => {
  const [summary, setSummary] = useState('');
  const [audioUrl, setAudioUrl] = useState(null);
  const [generatedAt, setGeneratedAt] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const { language } = useLanguage();

  const audioRef = useRef(null);

  // Stop audio and fetch saved summary whenever image changes
  useEffect(() => {
    stopAudio();
    if (!imageId) {
      setSummary('');
      setAudioUrl(null);
      setGeneratedAt(null);
      return;
    }
    fetchSavedSummary();
  }, [imageId]);

  // Clean up on unmount
  useEffect(() => {
    return () => stopAudio();
  }, []);

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    setIsPlaying(false);
  };

  const playAudio = (url) => {
    // Toggle off if already playing
    if (isPlaying) {
      stopAudio();
      return;
    }

    const target = url || audioUrl;
    if (!target) return;

    stopAudio();

    const audio = new Audio(target);
    audioRef.current = audio;

    audio.play().catch(() => {
      toast.error('Audio playback was blocked by browser');
      audioRef.current = null;
      setIsPlaying(false);
    });

    audio.onplay = () => setIsPlaying(true);
    audio.onended = () => { audioRef.current = null; setIsPlaying(false); };
    audio.onerror = () => { audioRef.current = null; setIsPlaying(false); };
  };

  const fetchSavedSummary = async () => {
    setIsFetching(true);
    try {
      const response = await api.get(`/plant/summary/${imageId}`);
      if (response.data.has_summary) {
        setSummary(response.data.summary);
        setAudioUrl(response.data.audio_url);
        setGeneratedAt(response.data.generated_at);
      } else {
        setSummary('');
        setAudioUrl(null);
        setGeneratedAt(null);
      }
    } catch (error) {
      console.error('Failed to fetch saved summary:', error);
    } finally {
      setIsFetching(false);
    }
  };

  const generateSummary = async () => {
    stopAudio();
    setIsLoading(true);
    try {
      const response = await api.post('/plant/summary', {
        image_id: imageId,
        language
      });

      if (response.data.status === 'empty') {
        toast('No questions asked yet. Ask a question first!', { icon: 'ℹ️' });
      } else {
        setSummary(response.data.summary);
        setAudioUrl(response.data.audio_url);
        setGeneratedAt(new Date().toISOString());
        toast.success('Summary generated!');

        // Autoplay the new summary audio
        if (response.data.audio_url) {
          setTimeout(() => playAudio(response.data.audio_url), 300);
        }
      }
    } catch (error) {
      console.error('Summary error:', error);
      toast.error('Failed to generate summary');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return null;
    return new Date(isoString).toLocaleString('en-IN', {
      day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <div className="flex flex-col h-full bg-cream-50 rounded-2xl shadow-lg border border-primary-100 overflow-hidden">

      {/* Header */}
      <div className="p-4 bg-primary-50 border-b border-primary-100 flex items-center justify-between">
        <h3 className="font-semibold text-primary-800 flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          Session Summary
        </h3>
        <button
          onClick={generateSummary}
          disabled={isLoading || isFetching || !imageId}
          className="p-2 bg-white rounded-full text-primary-600 hover:bg-primary-100 transition disabled:opacity-50"
          title={summary ? 'Regenerate Summary' : 'Generate Summary'}
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Body */}
      <div className="p-5 flex-1 overflow-y-auto">
        {isFetching ? (
          <div className="flex flex-col items-center justify-center h-full text-primary-400 space-y-3">
            <RefreshCw className="w-6 h-6 animate-spin" />
            <p className="text-sm">Loading saved summary...</p>
          </div>

        ) : isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-primary-400 space-y-3">
            <RefreshCw className="w-8 h-8 animate-spin" />
            <p className="text-sm font-medium">Generating summary...</p>
          </div>

        ) : summary ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {generatedAt && (
              <p className="text-xs text-gray-400">
                Last generated: {formatDate(generatedAt)}
              </p>
            )}

            <div className="prose prose-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
              {summary}
            </div>

            {audioUrl && (
              <button
                onClick={() => playAudio()}
                className={`w-full mt-4 flex items-center justify-center space-x-2 py-2 px-4 rounded-lg transition font-medium ${isPlaying
                    ? 'bg-red-100 text-red-700 hover:bg-red-200'
                    : 'bg-primary-100 text-primary-700 hover:bg-primary-200'
                  }`}
              >
                {isPlaying ? (
                  <><StopCircle className="w-5 h-5" /><span>Stop Audio</span></>
                ) : (
                  <><Volume2 className="w-5 h-5" /><span>Play Summary Audio</span></>
                )}
              </button>
            )}
          </motion.div>

        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <Sparkles className="w-10 h-10 mb-3 text-gray-300" />
            <p>No summary yet.</p>
            <p className="text-sm mt-1 text-gray-400">
              Ask questions about the disease, then click the refresh button to generate a summary.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SummaryPanel;