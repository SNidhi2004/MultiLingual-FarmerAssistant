import { useRef, useState } from 'react';
import Webcam from 'react-webcam';
import { useCamera } from '../../hooks/useCamera';
import { Camera, SwitchCamera, X, Check, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CameraCapture = ({ onCapture, onClose }) => {
  const {
    webcamRef,
    image,
    error,
    isCameraActive,
    videoConstraints,
    capture,
    retake,
    switchCamera,
    handleUserMedia,
    handleUserMediaError
  } = useCamera();

  const [isCapturing, setIsCapturing] = useState(false);

  const handleCapture = () => {
    setIsCapturing(true);
    const imageSrc = capture();
    if (imageSrc) {
      // Convert base64 to blob
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          onCapture(blob);
        });
    }
    setIsCapturing(false);
  };

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-2xl p-6 text-center"
      >
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Camera Error</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={onClose}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg"
        >
          Close
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      className="relative"
    >
      {/* Camera View */}
      <div className="relative rounded-2xl overflow-hidden bg-black aspect-[4/3]">
        {!image ? (
          <>
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              onUserMedia={handleUserMedia}
              onUserMediaError={handleUserMediaError}
              className="w-full h-full object-cover"
            />
            
            {/* Camera Guide Overlay */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-4/5 h-4/5 border-2 border-white/50 rounded-2xl">
                  <div className="absolute top-2 left-2 text-white/70 text-xs bg-black/30 px-2 py-1 rounded">
                    Center the leaf here
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <img src={image} alt="Captured" className="w-full h-full object-cover" />
        )}

        {/* Camera Controls */}
        <div className="absolute bottom-4 left-0 right-0 flex justify-center space-x-4">
          {!image ? (
            <>
              <button
                onClick={switchCamera}
                className="w-12 h-12 bg-black/50 backdrop-blur rounded-full flex items-center justify-center text-white hover:bg-black/70 transition"
              >
                <SwitchCamera className="w-6 h-6" />
              </button>
              <button
                onClick={handleCapture}
                disabled={!isCameraActive || isCapturing}
                className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg hover:scale-105 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Camera className="w-8 h-8 text-gray-800" />
              </button>
              <button
                onClick={onClose}
                className="w-12 h-12 bg-black/50 backdrop-blur rounded-full flex items-center justify-center text-white hover:bg-black/70 transition"
              >
                <X className="w-6 h-6" />
              </button>
            </>
          ) : (
            <>
              <button
                onClick={retake}
                className="w-12 h-12 bg-black/50 backdrop-blur rounded-full flex items-center justify-center text-white hover:bg-black/70 transition"
              >
                <X className="w-6 h-6" />
              </button>
              <button
                onClick={() => {
                  // Image is already captured, just confirm
                  fetch(image)
                    .then(res => res.blob())
                    .then(blob => {
                      onCapture(blob);
                    });
                }}
                className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center shadow-lg hover:scale-105 transition"
              >
                <Check className="w-8 h-8 text-white" />
              </button>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default CameraCapture;