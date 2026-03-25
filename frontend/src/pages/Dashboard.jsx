import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useHistory } from '../hooks/useHistory';
import CameraCapture from '../components/camera/CameraCapture';
import ImagePreview from '../components/camera/ImagePreview';
import HistoryGrid from '../components/History/HistoryGrid';
import ChatInterface from '../components/chat/ChatInterface';
import LanguageSelector from '../components/common/LanguageSelector';
import { LogOut, Sprout, ChevronLeft } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ImageUpload from '../components/camera/ImageUpload';
import api from '../api/axios';
import toast from 'react-hot-toast';
const Dashboard = () => {
  const { logout } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const { resumeSession } = useHistory();

  const [showCamera, setShowCamera] = useState(false);
  const [showUpload, setShowUpload] = useState(false); 

  const [capturedImage, setCapturedImage] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [view, setView] = useState('main'); // main, chat, history-chat

  const handleCapture = async (imageBlob) => {
    setCapturedImage(imageBlob);
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', imageBlob, 'plant.jpg');
    formData.append('language', language);

    try {
      const response = await api.post('/plant/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAnalysis(response.data);
      setActiveSession({
        sessionId: response.data.session_id,
        imageId: response.data.image_id,
        disease: response.data.disease,
        confidence: response.data.confidence,
        imageUrl: response.data.image_url
      });
      setView('chat');
      setShowCamera(false);
      setShowUpload(false); 
      
      toast.success('Image analyzed successfully!');
    } catch (error) {
      setError('Failed to analyze image. Please try again.');
      console.error('Analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = async (historyItem) => {
    setLoading(true);
    try {
      const session = await resumeSession(historyItem.session_id);
      const qaHistory = session?.current_image?.qa_history || [];
      console.log('QA History length:', qaHistory.length);
      setActiveSession({
        sessionId: historyItem.session_id,
        imageId: historyItem.image_id,
        disease: historyItem.disease,
        confidence: historyItem.confidence,
        imageUrl: historyItem.image_url,
        qaHistory: qaHistory 
      });
      setView('history-chat');
    } catch (error) {
      toast.error('Failed to load session');
    } finally {
      setLoading(false);
    }
  };

  const handleNewScan = () => {
    setShowUpload(true);
    setShowCamera(true);
    setCapturedImage(null);
    setAnalysis(null);
    setError(null);
  };

  const handleBack = () => {
    setView('main');
    setActiveSession(null);
    setShowCamera(false);
    setCapturedImage(null);
  };

  const handleCameraOption = () => {
    setShowUpload(false);
    setShowCamera(true);
  };

  const handleGalleryOption = (file) => {
    setShowUpload(false);
    handleCapture(file); // ✅ Directly use the file from gallery
  };

  return (
    <div className="min-h-screen bg-cream">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {view !== 'main' && (
              <button
                onClick={handleBack}
                className="p-2 hover:bg-gray-100 rounded-full transition"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            )}
            <div className="flex items-center space-x-2">
              <Sprout className="w-6 h-6 text-primary-500" />
              <h1 className="text-xl font-bold text-gray-800">Farmer Assistant</h1>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <LanguageSelector />
            <button
              onClick={logout}
              className="p-2 hover:bg-gray-100 rounded-full transition"
              title="Logout"
            >
              <LogOut className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-md mx-auto px-4 py-6">
        <AnimatePresence mode="wait">
          {view === 'main' && (
            <motion.div
              key="main"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              {/* New Scan Button */}
              <button
                onClick={handleNewScan}
                className="w-full btn-primary flex items-center justify-center space-x-2"
              >
                <span>+</span>
                <span>Scan New Plant</span>
              </button>

              {/* History Grid */}
              <HistoryGrid onSelectImage={handleHistorySelect} />
            </motion.div>
          )}

          {/* Upload Options Modal */}
          {showUpload && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <ImageUpload
                onCameraSelect={handleCameraOption}
                onGallerySelect={handleGalleryOption}
                onClose={() => setShowUpload(false)}
              />
            </motion.div>
          )}

          {/* Camera Capture */}
          {showCamera && (
            <motion.div
              key="camera"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <CameraCapture
                onCapture={handleCapture}
                onClose={() => {
                  setShowCamera(false);
                  setShowUpload(true); // Go back to upload options
                }}
              />
            </motion.div>
          )}

          {view === 'chat' && activeSession && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="space-y-4"
            >
              {capturedImage && (
                <ImagePreview
                  image={capturedImage}
                  disease={activeSession.disease}
                  confidence={activeSession.confidence}
                  loading={loading}
                  error={error}
                  onRetry={() => {
                    setView('main');
                    setShowUpload(true);
                  }}
                />
              )}

              <ChatInterface
                sessionId={activeSession.sessionId}
                disease={activeSession.disease}
                confidence={activeSession.confidence}
                initialQA={activeSession.qaHistory}
              />
            </motion.div>
          )}

          {view === 'history-chat' && activeSession && (
            <motion.div
              key="history-chat"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
            >
              <ChatInterface
                sessionId={activeSession.sessionId}
                disease={activeSession.disease}
                confidence={activeSession.confidence}
                initialQA={activeSession.qaHistory}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default Dashboard;

//   return (
//     <div className="min-h-screen bg-cream">
//       {/* Header */}
//       <header className="bg-white shadow-sm sticky top-0 z-10">
//         <div className="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
//           <div className="flex items-center space-x-2">
//             {view !== 'main' && (
//               <button
//                 onClick={handleBack}
//                 className="p-2 hover:bg-gray-100 rounded-full transition"
//               >
//                 <ChevronLeft className="w-5 h-5" />
//               </button>
//             )}
//             <div className="flex items-center space-x-2">
//               <Sprout className="w-6 h-6 text-primary-500" />
//               <h1 className="text-xl font-bold text-gray-800">Farmer Assistant</h1>
//             </div>
//           </div>
//           <div className="flex items-center space-x-3">
//             <LanguageSelector />
//             <button
//               onClick={logout}
//               className="p-2 hover:bg-gray-100 rounded-full transition"
//               title="Logout"
//             >
//               <LogOut className="w-5 h-5 text-gray-600" />
//             </button>
//           </div>
//         </div>
//       </header>

//       {/* Main Content */}
//       <main className="max-w-md mx-auto px-4 py-6">
//         <AnimatePresence mode="wait">
//           {view === 'main' && (
//             <motion.div
//               key="main"
//               initial={{ opacity: 0, x: -20 }}
//               animate={{ opacity: 1, x: 0 }}
//               exit={{ opacity: 0, x: 20 }}
//               className="space-y-6"
//             >
//               {/* New Scan Button */}
//               <button
//                 onClick={handleNewScan}
//                 className="w-full btn-primary flex items-center justify-center space-x-2"
//               >
//                 <span>+</span>
//                 <span>Scan New Plant</span>
//               </button>

//               {/* History Grid */}
//               <HistoryGrid onSelectImage={handleHistorySelect} />
//             </motion.div>
//           )}

//           {showCamera && (
//             <motion.div
//               key="camera"
//               initial={{ opacity: 0, scale: 0.9 }}
//               animate={{ opacity: 1, scale: 1 }}
//               exit={{ opacity: 0, scale: 0.9 }}
//             >
//               <CameraCapture
//                 onCapture={handleCapture}
//                 onClose={() => setShowCamera(false)}
//               />
//             </motion.div>
//           )}

//           {view === 'chat' && activeSession && (
//             <motion.div
//               key="chat"
//               initial={{ opacity: 0, y: 20 }}
//               animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: 20 }}
//               className="space-y-4"
//             >
//               {capturedImage && (
//                 <ImagePreview
//                   image={capturedImage}
//                   disease={activeSession.disease}
//                   confidence={activeSession.confidence}
//                   loading={loading}
//                   error={error}
//                   onRetry={() => setShowCamera(true)}
//                 />
//               )}

//               <ChatInterface
//                 sessionId={activeSession.sessionId}
//                 disease={activeSession.disease}
//                 confidence={activeSession.confidence}
//                 initialQA={[]}
//               />
//             </motion.div>
//           )}

//           {view === 'history-chat' && activeSession && (
//             <motion.div
//               key="history-chat"
//               initial={{ opacity: 0, y: 20 }}
//               animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: 20 }}
//             >
//               <ChatInterface
//                 sessionId={activeSession.sessionId}
//                 disease={activeSession.disease}
//                 confidence={activeSession.confidence}
//                 initialQA={activeSession.qaHistory}
//               />
//             </motion.div>
//           )}
//         </AnimatePresence>
//       </main>
//     </div>
//   );
// };

// export default Dashboard;