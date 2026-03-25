import { useHistory } from '../../hooks/useHistory';
import HistoryCard from './HistoryCard';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import { History, Camera } from 'lucide-react';

const HistoryGrid = ({ onSelectImage }) => {
  const { history, loading, error, fetchHistory } = useHistory();

  if (loading) {
    return (
      <div className="py-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-4">
        <ErrorMessage message={error} onRetry={fetchHistory} />
      </div>
    );
  }

  if (!history || history.length === 0) {
    return (
      <div className="bg-white rounded-xl p-8 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
          <Camera className="w-8 h-8 text-primary-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">No History Yet</h3>
        <p className="text-gray-600">
          Take your first plant photo to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 text-gray-700">
        <History className="w-5 h-5 text-primary-500" />
        <h2 className="font-semibold">Recent Scans</h2>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {history.slice(0, 3).map((item,index) => (
          <HistoryCard
            key={item.image_id || `history-${index}-${Date.now()}` }
            image={item}
            onClick={() => onSelectImage(item)}
          />
        ))}
      </div>
    </div>
  );
};

export default HistoryGrid;