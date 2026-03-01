import api from "../api/api";

export default function ImageUploader({ language, onDetected }) {
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);
    formData.append("language", language);

    const res = await api.post("/plant/analyze", formData);

    onDetected(res.data);
  };

  return <input type="file" accept="image/*" onChange={handleUpload} />;
}
