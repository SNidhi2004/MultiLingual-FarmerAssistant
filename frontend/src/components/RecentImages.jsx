import { useEffect, useState } from "react";
import api from "../api/api";

export default function RecentImages({ onSwitch }) {
  const [images, setImages] = useState([]);

  const fetchImages = async () => {
    try {
      const res = await api.get("/plant/recent-images");
      setImages(res.data);
    } catch (err) {
      console.error("Failed to load recent images");
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  const handleSwitch = async (imageId) => {
    const res = await api.post("/plant/switch-image", {
      image_id: imageId,
    });

    onSwitch(res.data);
  };

  return (
    <div className="recent-images">
      <h4>Recent Images</h4>
      {images.map((img) => (
        <div
          key={img.image_id}
          className="thumbnail"
          onClick={() => handleSwitch(img.image_id)}
        >
          <img src={img.thumbnail} alt="thumb" />
          <p>{img.disease}</p>
        </div>
      ))}
    </div>
  );
}
