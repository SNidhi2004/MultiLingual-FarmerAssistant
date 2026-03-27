import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';
import toast from 'react-hot-toast';

export const useHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching history...'); // Debug log
      const token = localStorage.getItem('token');
      console.log('Token exists:', !!token); // Debug log
      
      const response = await api.get('/plant/history');
      console.log('History response:', response.data); // Debug log
      setHistory(response.data || []);
    } catch (err) {
      console.error('History fetch error details:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      
      if (err.response?.status === 401) {
        setError('Session expired. Please login again.');
        // Optionally redirect to login
        // window.location.href = '/login';
      } else {
        setError('Failed to load history');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const getImageDetails = useCallback(async (imageId) => {
    try {
      const response = await api.get(`/plant/image/${imageId}`);
      return response.data;
    } catch (err) {
      toast.error('Failed to load image details');
      throw err;
    }
  }, []);

  const resumeSession = useCallback(async (sessionId, imageId = null) => {
    try {
      const payload = imageId ? { image_id: imageId } : {};
      const response = await api.post(`/plant/resume/${sessionId}`, payload);
      return response.data.session;
    } catch (err) {
      toast.error('Failed to resume session');
      throw err;
    }
  }, []);

  

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    history,
    loading,
    error,
    fetchHistory,
    resumeSession,
    getImageDetails
  };
};