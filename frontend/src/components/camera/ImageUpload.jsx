import { useRef } from 'react';
import { Camera, Upload, X } from 'lucide-react';
import { motion } from 'framer-motion';

const ImageUpload = ({ onCameraSelect, onGallerySelect, onClose }) => {
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      onGallerySelect(file); // ✅ Call the gallery select handler with the file
    }
  };

  const handleCameraClick = () => {
    onCameraSelect(); // ✅ Just call the camera handler, no need to set mode
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="bg-white rounded-2xl p-6 shadow-xl"
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Select Image Source</h3>
        <button 
          onClick={onClose} 
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={handleCameraClick}
          className="flex flex-col items-center p-6 bg-green-50 rounded-xl hover:bg-green-100 transition-all duration-200 border-2 border-transparent hover:border-green-300"
        >
          <Camera className="w-10 h-10 text-green-600 mb-3" />
          <span className="font-medium text-gray-700">Take Photo</span>
          <span className="text-xs text-gray-500 mt-1">Use camera</span>
        </button>

        <button
          onClick={() => fileInputRef.current.click()}
          className="flex flex-col items-center p-6 bg-blue-50 rounded-xl hover:bg-blue-100 transition-all duration-200 border-2 border-transparent hover:border-blue-300"
        >
          <Upload className="w-10 h-10 text-blue-600 mb-3" />
          <span className="font-medium text-gray-700">Upload from Gallery</span>
          <span className="text-xs text-gray-500 mt-1">Choose existing photo</span>
        </button>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept="image/*"
        className="hidden"
      />

      <p className="text-xs text-center text-gray-400 mt-4">
        Supported formats: JPG, PNG, JPEG (Max 10MB)
      </p>
    </motion.div>
  );
};

export default ImageUpload;