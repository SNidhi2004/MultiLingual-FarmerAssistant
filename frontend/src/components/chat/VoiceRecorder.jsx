// import { useState, useRef, useEffect } from 'react';
// import { Mic, Square, Loader2 } from 'lucide-react';

// const VoiceRecorder = ({ onRecordingComplete, disabled }) => {
//   const [isRecording, setIsRecording] = useState(false);
//   const [recordingTime, setRecordingTime] = useState(0);
//   const [isProcessing, setIsProcessing] = useState(false);
//   const mediaRecorderRef = useRef(null);
//   const chunksRef = useRef([]);
//   const timerRef = useRef(null);
//   const streamRef = useRef(null);

//   // Cleanup on unmount
//   useEffect(() => {
//     return () => {
//       if (timerRef.current) clearInterval(timerRef.current);
//       if (streamRef.current) {
//         streamRef.current.getTracks().forEach(track => track.stop());
//       }
//     };
//   }, []);

//   const formatTime = (seconds) => {
//     const mins = Math.floor(seconds / 60);
//     const secs = seconds % 60;
//     return `${mins}:${secs.toString().padStart(2, '0')}`;
//   };

//   const startRecording = async () => {
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       streamRef.current = stream;
      
//       const mediaRecorder = new MediaRecorder(stream);
//       mediaRecorderRef.current = mediaRecorder;
//       chunksRef.current = [];

//       mediaRecorder.ondataavailable = (e) => {
//         if (e.data.size > 0) {
//           chunksRef.current.push(e.data);
//         }
//       };

//       mediaRecorder.onstop = () => {
//         const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
//         if (blob.size > 0) {
//           setIsProcessing(true);
//           onRecordingComplete(blob);
//           setTimeout(() => setIsProcessing(false), 1000);
//         }
//       };

//       mediaRecorder.start();
//       setIsRecording(true);
      
//       // Start timer
//       setRecordingTime(0);
//       timerRef.current = setInterval(() => {
//         setRecordingTime(prev => prev + 1);
//       }, 1000);

//     } catch (error) {
//       console.error('Microphone error:', error);
//       alert('Unable to access microphone. Please check permissions.');
//     }
//   };

//   const stopRecording = () => {
//     if (mediaRecorderRef.current && isRecording) {
//       mediaRecorderRef.current.stop();
//       setIsRecording(false);
      
//       if (timerRef.current) {
//         clearInterval(timerRef.current);
//         timerRef.current = null;
//       }
      
//       if (streamRef.current) {
//         streamRef.current.getTracks().forEach(track => track.stop());
//         streamRef.current = null;
//       }
//     }
//   };

//   if (disabled) {
//     return (
//       <button disabled className="p-3 bg-gray-200 text-gray-400 rounded-xl">
//         <Mic className="w-5 h-5" />
//       </button>
//     );
//   }

//   return (
//     <div className="relative">
//       {/* Recording Indicator */}
//       {isRecording && (
//         <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg p-3 border border-gray-200 whitespace-nowrap z-50">
//           <div className="flex items-center space-x-3">
//             <div className="relative">
//               <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
//               <div className="absolute inset-0 w-3 h-3 bg-red-500 rounded-full animate-ping opacity-75" />
//             </div>
//             <span className="text-red-500 font-mono font-bold text-lg">
//               {formatTime(recordingTime)}
//             </span>
//             <div className="flex space-x-1">
//               {[...Array(8)].map((_, i) => (
//                 <div
//                   key={i}
//                   className="w-1.5 bg-secondary-500 rounded-full"
//                   style={{
//                     animation: 'wave 0.6s ease-in-out infinite',
//                     animationDelay: `${i * 0.08}s`,
//                     height: '24px'
//                   }}
//                 />
//               ))}
//             </div>
//             <span className="text-xs text-gray-500 ml-2">Recording...</span>
//           </div>
//         </div>
//       )}

//       {/* Processing Indicator */}
//       {isProcessing && (
//         <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg p-3 border border-gray-200">
//           <div className="flex items-center space-x-2">
//             <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />
//             <span className="text-sm text-gray-600">Processing...</span>
//           </div>
//         </div>
//       )}

//       {/* Record Button */}
//       <button
//         onClick={isRecording ? stopRecording : startRecording}
//         className={`p-3 rounded-xl transition-all duration-200 ${
//           isRecording
//             ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
//             : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
//         }`}
//         title={isRecording ? 'Stop recording' : 'Start voice recording'}
//       >
//         {isRecording ? <Square className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
//       </button>
//     </div>
//   );
// };

// export default VoiceRecorder;

// import { useState, useRef, useEffect } from 'react';
// import { Mic, Square, Loader2 } from 'lucide-react';

// const VoiceRecorder = ({ onRecordingComplete, disabled }) => {
//   const [isRecording, setIsRecording] = useState(false);
//   const [recordingTime, setRecordingTime] = useState(0);
//   const [isProcessing, setIsProcessing] = useState(false);
//   const mediaRecorderRef = useRef(null);
//   const chunksRef = useRef([]);
//   const timerRef = useRef(null);
//   const streamRef = useRef(null);

//   useEffect(() => {
//     return () => {
//       if (timerRef.current) clearInterval(timerRef.current);
//       if (streamRef.current) {
//         streamRef.current.getTracks().forEach(track => track.stop());
//       }
//     };
//   }, []);

//   const formatTime = (seconds) => {
//     const mins = Math.floor(seconds / 60);
//     const secs = seconds % 60;
//     return `${mins}:${secs.toString().padStart(2, '0')}`;
//   };

//   // Convert blob to proper WAV format for Azure
//   const convertToWav = async (blob) => {
//     try {
//       const audioContext = new (window.AudioContext || window.webkitAudioContext)();
//       const arrayBuffer = await blob.arrayBuffer();
//       const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      
//       // Convert to WAV
//       const wavBlob = await audioBufferToWav(audioBuffer);
//       return wavBlob;
//     } catch (error) {
//       console.error('Audio conversion error:', error);
//       return blob;
//     }
//   };

//   const audioBufferToWav = (buffer) => {
//     const numChannels = buffer.numberOfChannels;
//     const sampleRate = buffer.sampleRate;
//     const format = 1;
//     const bitDepth = 16;
//     const bytesPerSample = bitDepth / 8;
//     const blockAlign = numChannels * bytesPerSample;
    
//     const samples = [];
//     for (let channel = 0; channel < numChannels; channel++) {
//       samples.push(buffer.getChannelData(channel));
//     }
    
//     const dataLength = samples[0].length * numChannels * bytesPerSample;
//     const bufferLength = 44 + dataLength;
//     const arrayBuffer = new ArrayBuffer(bufferLength);
//     const view = new DataView(arrayBuffer);
    
//     // Write WAV header
//     writeString(view, 0, 'RIFF');
//     view.setUint32(4, 36 + dataLength, true);
//     writeString(view, 8, 'WAVE');
//     writeString(view, 12, 'fmt ');
//     view.setUint32(16, 16, true);
//     view.setUint16(20, format, true);
//     view.setUint16(22, numChannels, true);
//     view.setUint32(24, sampleRate, true);
//     view.setUint32(28, sampleRate * blockAlign, true);
//     view.setUint16(32, blockAlign, true);
//     view.setUint16(34, bitDepth, true);
//     writeString(view, 36, 'data');
//     view.setUint32(40, dataLength, true);
    
//     // Write samples
//     let offset = 44;
//     for (let i = 0; i < samples[0].length; i++) {
//       for (let channel = 0; channel < numChannels; channel++) {
//         const sample = Math.max(-1, Math.min(1, samples[channel][i]));
//         const value = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
//         view.setInt16(offset, value, true);
//         offset += 2;
//       }
//     }
    
//     return new Blob([arrayBuffer], { type: 'audio/wav' });
//   };
  
//   const writeString = (view, offset, string) => {
//     for (let i = 0; i < string.length; i++) {
//       view.setUint8(offset + i, string.charCodeAt(i));
//     }
//   };

//   const startRecording = async () => {
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ 
//         audio: {
//           echoCancellation: true,
//           noiseSuppression: true,
//           autoGainControl: true,
//           sampleRate: 16000
//         } 
//       });
//       streamRef.current = stream;
      
//       const mediaRecorder = new MediaRecorder(stream);
//       mediaRecorderRef.current = mediaRecorder;
//       chunksRef.current = [];

//       mediaRecorder.ondataavailable = (e) => {
//         if (e.data.size > 0) {
//           chunksRef.current.push(e.data);
//         }
//       };

//       mediaRecorder.onstop = async () => {
//         const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
//         if (blob.size > 0) {
//           setIsProcessing(true);
//           try {
//             // Convert to WAV format
//             const wavBlob = await convertToWav(blob);
//             console.log('Audio converted to WAV, size:', wavBlob.size);
//             onRecordingComplete(wavBlob);
//           } catch (error) {
//             console.error('Conversion error:', error);
//             // Fallback to original blob
//             onRecordingComplete(blob);
//           }
//           setTimeout(() => setIsProcessing(false), 1000);
//         }
//       };

//       mediaRecorder.start(1000);
//       setIsRecording(true);
      
//       setRecordingTime(0);
//       timerRef.current = setInterval(() => {
//         setRecordingTime(prev => prev + 1);
//       }, 1000);

//     } catch (error) {
//       console.error('Microphone error:', error);
//       alert('Unable to access microphone. Please check permissions.');
//     }
//   };

//   const stopRecording = () => {
//     if (mediaRecorderRef.current && isRecording) {
//       mediaRecorderRef.current.stop();
//       setIsRecording(false);
      
//       if (timerRef.current) {
//         clearInterval(timerRef.current);
//         timerRef.current = null;
//       }
      
//       if (streamRef.current) {
//         streamRef.current.getTracks().forEach(track => track.stop());
//         streamRef.current = null;
//       }
//     }
//   };

//   if (disabled) {
//     return (
//       <button disabled className="p-3 bg-gray-200 text-gray-400 rounded-xl">
//         <Mic className="w-5 h-5" />
//       </button>
//     );
//   }

//   return (
//     <div className="relative">
//       {isRecording && (
//         <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg p-3 border border-gray-200 whitespace-nowrap z-50">
//           <div className="flex items-center space-x-3">
//             <div className="relative">
//               <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
//               <div className="absolute inset-0 w-3 h-3 bg-red-500 rounded-full animate-ping opacity-75" />
//             </div>
//             <span className="text-red-500 font-mono font-bold text-lg">
//               {formatTime(recordingTime)}
//             </span>
//             <div className="flex space-x-1">
//               {[...Array(8)].map((_, i) => (
//                 <div
//                   key={i}
//                   className="w-1.5 bg-secondary-500 rounded-full"
//                   style={{
//                     animation: 'wave 0.6s ease-in-out infinite',
//                     animationDelay: `${i * 0.08}s`,
//                     height: '24px'
//                   }}
//                 />
//               ))}
//             </div>
//             <span className="text-xs text-gray-500 ml-2">Recording...</span>
//           </div>
//         </div>
//       )}

//       {isProcessing && (
//         <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg p-3 border border-gray-200">
//           <div className="flex items-center space-x-2">
//             <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />
//             <span className="text-sm text-gray-600">Processing...</span>
//           </div>
//         </div>
//       )}

//       <button
//         onClick={isRecording ? stopRecording : startRecording}
//         className={`p-3 rounded-xl transition-all duration-200 ${
//           isRecording
//             ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
//             : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
//         }`}
//         title={isRecording ? 'Stop recording' : 'Start voice recording'}
//       >
//         {isRecording ? <Square className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
//       </button>
//     </div>
//   );
// };

// export default VoiceRecorder;

import { useState, useRef, useEffect } from 'react';
import { Mic, Square, Send, Loader2, Trash2 } from 'lucide-react';

const VoiceRecorder = ({ onRecordingComplete, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Convert AudioBuffer to proper 16kHz 16-bit PCM WAV
  const audioBufferToWav = (buffer, targetSampleRate = 16000) => {
    let audioBuffer = buffer;
    if (buffer.sampleRate !== targetSampleRate) {
      const ratio = targetSampleRate / buffer.sampleRate;
      const newLength = Math.floor(buffer.length * ratio);
      const newData = new Float32Array(newLength);
      for (let i = 0; i < newLength; i++) {
        const index = Math.floor(i / ratio);
        newData[i] = buffer.getChannelData(0)[index];
      }
      
      audioBuffer = {
        sampleRate: targetSampleRate,
        length: newLength,
        numberOfChannels: 1,
        getChannelData: () => newData
      };
    }
    
    const numChannels = 1;
    const sampleRate = targetSampleRate;
    const format = 1;
    const bitDepth = 16;
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numChannels * bytesPerSample;
    
    const samples = audioBuffer.getChannelData(0);
    const dataLength = samples.length * bytesPerSample;
    const bufferLength = 44 + dataLength;
    const arrayBuffer = new ArrayBuffer(bufferLength);
    const view = new DataView(arrayBuffer);
    
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataLength, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);
    writeString(view, 36, 'data');
    view.setUint32(40, dataLength, true);
    
    let offset = 44;
    for (let i = 0; i < samples.length; i++) {
      let sample = Math.max(-1, Math.min(1, samples[i]));
      const value = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
      view.setInt16(offset, value, true);
      offset += 2;
    }
    
    return new Blob([arrayBuffer], { type: 'audio/wav' });
  };
  
  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000,
          channelCount: 1
        } 
      });
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        if (blob.size > 0) {
          setIsProcessing(true);
          try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const arrayBuffer = await blob.arrayBuffer();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
            const wavBlob = audioBufferToWav(audioBuffer, 16000);
            setAudioBlob(wavBlob);
            const url = URL.createObjectURL(wavBlob);
            setAudioUrl(url);
            console.log('✅ Recording ready, size:', wavBlob.size);
          } catch (error) {
            console.error('Conversion error:', error);
            setAudioBlob(blob);
            const url = URL.createObjectURL(blob);
            setAudioUrl(url);
          }
          setIsProcessing(false);
        }
      };

      mediaRecorder.start(1000);
      setIsRecording(true);
      setAudioBlob(null);
      setAudioUrl(null);
      
      setRecordingTime(0);
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Microphone error:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    }
  };

  const discardRecording = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
  };

  const sendRecording = () => {
    if (audioBlob) {
      onRecordingComplete(audioBlob);
      discardRecording();
    }
  };

  if (disabled) {
    return (
      <button disabled className="p-3 bg-gray-200 text-gray-400 rounded-xl">
        <Mic className="w-5 h-5" />
      </button>
    );
  }

  return (
    <div className="relative">
      {/* Recording Indicator */}
      {isRecording && (
        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg p-3 border border-gray-200 whitespace-nowrap z-50">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <div className="absolute inset-0 w-3 h-3 bg-red-500 rounded-full animate-ping opacity-75" />
            </div>
            <span className="text-red-500 font-mono font-bold text-lg">
              {formatTime(recordingTime)}
            </span>
            <div className="flex space-x-1">
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className="w-1.5 bg-secondary-500 rounded-full"
                  style={{
                    animation: 'wave 0.6s ease-in-out infinite',
                    animationDelay: `${i * 0.08}s`,
                    height: '24px'
                  }}
                />
              ))}
            </div>
            <span className="text-xs text-gray-500 ml-2">Recording...</span>
          </div>
        </div>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg p-3 border border-gray-200">
          <div className="flex items-center space-x-2">
            <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />
            <span className="text-sm text-gray-600">Processing...</span>
          </div>
        </div>
      )}

      {/* Preview & Controls when recording is ready */}
      {audioUrl && !isRecording && !isProcessing && (
        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-white rounded-xl shadow-lg p-3 border border-gray-200 z-50 min-w-[200px]">
          <div className="flex items-center space-x-3">
            <audio controls src={audioUrl} className="h-8 w-32" />
            <div className="flex space-x-1">
              <button
                onClick={discardRecording}
                className="p-1.5 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition"
                title="Discard"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={sendRecording}
                className="p-1.5 bg-green-100 text-green-600 rounded-lg hover:bg-green-200 transition"
                title="Send"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Record Button */}
      <button
        onClick={isRecording ? stopRecording : startRecording}
        className={`p-3 rounded-xl transition-all duration-200 ${
          isRecording
            ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
            : audioUrl
            ? 'bg-green-500 text-white hover:bg-green-600'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }`}
        title={isRecording ? 'Stop recording' : audioUrl ? 'Recording ready' : 'Start voice recording'}
      >
        {isRecording ? <Square className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
      </button>
    </div>
  );
};

export default VoiceRecorder;