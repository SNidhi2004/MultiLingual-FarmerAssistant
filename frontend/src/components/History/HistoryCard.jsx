import { motion } from 'framer-motion';
import { ChevronRight, AlertCircle, CheckCircle, HelpCircle } from 'lucide-react';
import toast from 'react-hot-toast'; // Add this import

const HistoryCard = ({ image, onClick }) => {
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceIcon = (confidence) => {
    if (confidence >= 0.8) return <CheckCircle className="w-4 h-4" />;
    if (confidence >= 0.6) return <HelpCircle className="w-4 h-4" />;
    return <AlertCircle className="w-4 h-4" />;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const handleClick = () => {
    // Debug log to see what we're getting
    console.log('🔍 HistoryCard clicked - image data:', {
      image_id: image.image_id,
      session_id: image.session_id,
      disease: image.disease,
      full_image: image
    });

    // Check if we have a valid session_id
    if (!image.session_id) {
      console.error('❌ No session_id for this image!');
      toast.error('Cannot resume session - missing session ID');
      return;
    }

    // Call the onClick with the image
    onClick(image);
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={handleClick}  // Use the new handler
      className="bg-white rounded-xl shadow-md overflow-hidden cursor-pointer border border-gray-100"
    >
      {/* Thumbnail */}
      <div className="relative aspect-square bg-gray-100">
        {image.thumbnail ? (
          <img
            src={`data:image/jpeg;base64,${image.thumbnail}`}
            alt={image.disease}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <img
              src={image.image_url}
              alt={image.disease}
              className="w-full h-full object-cover"
            />
          </div>
        )}
        
        {/* Confidence Badge */}
        <div className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getConfidenceColor(image.confidence)}`}>
          {getConfidenceIcon(image.confidence)}
          <span>{Math.round(image.confidence * 100)}%</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-3">
        <h3 className="font-semibold text-gray-800 line-clamp-1">
          {image.disease || 'Unknown Disease'}
        </h3>
        
        {/* Date */}
        <p className="text-xs text-gray-500 mt-1">
          {formatDate(image.created_at)}
        </p>

        {/* QA Preview */}
        {image.qa_preview && image.qa_preview.length > 0 && (
          <div className="mt-2 space-y-1">
            {image.qa_preview.map((qa, idx) => (
              <div key={idx} className="text-xs bg-gray-50 p-1.5 rounded">
                <p className="text-gray-700 line-clamp-1">
                  <span className="font-medium">Q:</span> {qa.question}
                </p>
                <p className="text-gray-600 line-clamp-1 mt-0.5">
                  <span className="font-medium">A:</span> {qa.answer}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* View Details - Add session_id display for debugging */}
        <div className="mt-2 flex items-center justify-between text-xs">
          <span className="text-primary-600">{image.total_qa || 0} questions</span>
          <div className="flex items-center space-x-1">
            {image.session_id ? (
              <span className="text-green-600 text-xs">✅</span>
            ) : (
              <span className="text-red-600 text-xs">❌ No session</span>
            )}
            <ChevronRight className="w-4 h-4 text-primary-600" />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default HistoryCard;