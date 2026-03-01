export default function LanguageSelect({ language, setLanguage }) {
  return (
    <select value={language} onChange={(e) => setLanguage(e.target.value)}>
      <option value="en-IN">English</option>
      <option value="hi-IN">Hindi</option>
      <option value="te-IN">Telugu</option>
    </select>
  );
}
