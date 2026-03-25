import { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';

export const useCamera = () => {
  const webcamRef = useRef(null);
  const [image, setImage] = useState(null);
  const [error, setError] = useState(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [facingMode, setFacingMode] = useState('environment'); // Default to back camera

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: facingMode
  };

  const capture = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setImage(imageSrc);
      return imageSrc;
    }
  }, [webcamRef]);

  const retake = useCallback(() => {
    setImage(null);
  }, []);

  const switchCamera = useCallback(() => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
  }, []);

  const handleUserMedia = useCallback(() => {
    setIsCameraActive(true);
    setError(null);
  }, []);

  const handleUserMediaError = useCallback((error) => {
    console.error('Camera error:', error);
    setError('Unable to access camera. Please ensure camera permissions are granted.');
    setIsCameraActive(false);
  }, []);

  return {
    webcamRef,
    image,
    error,
    isCameraActive,
    facingMode,
    videoConstraints,
    capture,
    retake,
    switchCamera,
    handleUserMedia,
    handleUserMediaError
  };
};