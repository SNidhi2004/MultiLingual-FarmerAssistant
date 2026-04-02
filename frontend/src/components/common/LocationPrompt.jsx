import { useState, useEffect } from 'react';
import { MapPin, X } from 'lucide-react';
import api from '../../api/axios';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

const LocationPrompt = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [location, setLocation] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Fetch user's current location from backend
    const fetchLocation = async () => {
      try {
        const response = await api.get('/auth/location');
        if (response.data.location) {
          setLocation(response.data.location);
        }
      } catch (error) {
        console.error('Failed to fetch location:', error);
      }
    };
    fetchLocation();
  }, []);

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await api.post('/auth/location', { location });
      toast.success('Location updated successfully!');
      setIsOpen(false);
    } catch (error) {
      toast.error('Failed to update location');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="p-2 hover:bg-gray-100 rounded-full transition relative block"
        title="Set Location"
      >
        <MapPin className="w-5 h-5 text-green-600" />
        {!location && (
          <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full animate-pulse border border-white"></span>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-xl w-full max-w-sm overflow-hidden"
            >
              <div className="p-4 bg-gray-50 flex justify-between items-center border-b border-gray-100">
                <h3 className="font-semibold text-gray-800 flex items-center space-x-2">
                  <MapPin className="w-5 h-5 text-primary-500" />
                  <span>Your Location</span>
                </h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-gray-200 rounded-full transition text-gray-500"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <p className="text-sm text-gray-600">
                  Set your location so the assistant can give you accurate nearby suggestions for tools and remedies.
                </p>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    City, State
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. Hyderabad, Telangana"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                
                <button
                  onClick={handleSave}
                  disabled={isLoading}
                  className="w-full btn-primary disabled:opacity-50"
                >
                  {isLoading ? 'Saving...' : 'Save Location'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};

export default LocationPrompt;
