import { motion } from 'framer-motion';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';

const ImagePreview = ({ image, disease, confidence, loading, error, onRetry }) => {
  const getConfidenceColor = () => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceText = () => {
    if (confidence >= 0.8) return 'High Confidence';
    if (confidence >= 0.6) return 'Medium Confidence';
    return 'Low Confidence - Please retake photo';
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-white rounded-2xl p-8 text-center"
      >
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Analyzing Image...</h3>
        <p className="text-gray-600">Our AI is detecting the disease</p>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-white rounded-2xl p-8 text-center"
      >
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Analysis Failed</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={onRetry}
          className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition flex items-center space-x-2 mx-auto"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Try Again</span>
        </button>
      </motion.div>
    );
  }

  if (!disease) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl overflow-hidden shadow-lg"
    >
      {/* Image */}
      <div className="aspect-video bg-gray-100">
        <img
          src={URL.createObjectURL(image)}
          alt="Captured plant"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Results */}
      <div className="p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">{disease}</h2>
        
        {/* Confidence Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Confidence</span>
            <span className={`font-semibold ${getConfidenceColor()}`}>
              {Math.round(confidence * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className={`h-2.5 rounded-full ${
                confidence >= 0.8 ? 'bg-green-500' :
                confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
          <p className={`text-sm ${getConfidenceColor()}`}>
            {getConfidenceText()}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default ImagePreview;