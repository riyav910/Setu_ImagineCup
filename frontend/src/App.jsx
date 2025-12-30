import { useState } from 'react';
import axios from 'axios';
import { Camera, Upload, Share2, AlertCircle, Sparkles, X } from 'lucide-react';
import AudioRecorder from './AudioRecorder';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  // State for multiple images
  const [imagePreviews, setImagePreviews] = useState([]); 
  const [selectedFiles, setSelectedFiles] = useState([]);
  
  const [features, setFeatures] = useState("");
  const [userPrice, setUserPrice] = useState("");

  // 1. HANDLE FILE SELECTION (Preview Only)
  const handleImageUpload = (event) => {
    const inputFiles = event.target.files;
    if (!inputFiles || inputFiles.length === 0) return;

    const files = Array.from(inputFiles);
    const newPreviews = files.map((file) => URL.createObjectURL(file));

    // Append new files to existing ones (or replace if you prefer)
    // Here we append to allow adding more photos
    setSelectedFiles(prev => [...prev, ...files]);
    setImagePreviews(prev => [...prev, ...newPreviews]);
    setResult(null); 
  };

  // 2. SUBMIT TO BACKEND
  const submitAnalysis = async () => {
    if (selectedFiles.length === 0) return;
    setLoading(true);

    const formData = new FormData();

    // Append ALL selected files
    selectedFiles.forEach(file => {
      formData.append("files", file);
    });

    formData.append("user_features", features);
    formData.append("user_price", userPrice);

    try {
      const API_URL = import.meta.env.VITE_API_URL;
      const response = await axios.post(`${API_URL}/analyze`, formData);
      console.log("Backend Response:", response.data);
      setResult(response.data);
    } catch (error) {
      console.error("Analysis Error:", error);
      setResult({ status: "error", message: "Failed to connect to backend." });
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = (text) => {
    setFeatures((prev) => prev ? `${prev} ${text}` : text);
  };

  const removeImage = (index) => {
     const newFiles = selectedFiles.filter((_, i) => i !== index);
     const newPreviews = imagePreviews.filter((_, i) => i !== index);
     setSelectedFiles(newFiles);
     setImagePreviews(newPreviews);
  };

  const calculatePosition = (min, max, current) => {
    if (!min || !max || !current) return 50;
    const range = max - min;
    const position = ((current - min) / range) * 100;
    return Math.min(Math.max(position, 0), 100); 
  };

  return (
    <div className="min-h-screen w-full max-w-5xl mx-auto bg-gray-50 flex flex-col items-center p-4 font-sans">
      <header className="w-full max-w-5xl mx-auto bg-white rounded-2xl shadow-sm p-4 mb-6 text-center">
        <h1 className="text-2xl font-bold text-blue-600 tracking-tight">Setu AI 🛍️</h1>
        <p className="text-gray-500 text-sm">Selling made simple.</p>
      </header>

      <main className="w-full max-w-5xl mx-auto bg-white rounded-3xl shadow-xl overflow-hidden transition-all duration-300">

        {/* INPUT SECTION */}
        {!result && (
          <div className="p-8 flex flex-col items-center justify-center min-h-[400px]">
            
            {/* GALLERY PREVIEW GRID */}
            {imagePreviews.length > 0 ? (
              <div className="w-full mb-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {imagePreviews.map((src, idx) => (
                    <div key={idx} className="relative aspect-square rounded-xl overflow-hidden shadow-sm group border border-gray-100">
                      <img src={src} alt={`Preview ${idx}`} className="w-full h-full object-cover" />
                      <button 
                          onClick={() => removeImage(idx)}
                          className="absolute top-1 right-1 bg-black/50 text-white p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition hover:bg-red-500"
                      >
                          <X size={14} />
                      </button>
                    </div>
                  ))}
                  
                  {/* "Add More" Button */}
                   <label className="aspect-square border-2 border-dashed border-gray-300 rounded-xl flex items-center justify-center cursor-pointer hover:bg-gray-50 text-gray-400 transition">
                        <input type="file" onChange={handleImageUpload} className="hidden" accept="image/*" multiple />
                        <span className="text-3xl font-light">+</span>
                   </label>
                </div>
                
                <p className="text-center text-xs text-gray-400 mt-3">{selectedFiles.length} photos selected</p>

                {/* ANALYZE BUTTON */}
                <button
                  onClick={submitAnalysis}
                  disabled={loading}
                  className="w-full mt-6 bg-blue-600 text-white font-bold py-4 rounded-xl hover:bg-blue-700 transition flex justify-center items-center gap-2 shadow-lg shadow-blue-200"
                >
                  {loading ? (
                       <> <Sparkles className="animate-spin" size={20}/> Analyzing Market... </>
                  ) : (
                       `Analyze ${selectedFiles.length} Photos`
                  )}
                </button>
              </div>
            ) : (
              // EMPTY STATE
              <label className="w-full cursor-pointer group">
                  <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 mb-6 w-full flex flex-col items-center group-hover:bg-blue-50 group-hover:border-blue-300 transition-all">
                    <Camera className="w-16 h-16 text-gray-300 group-hover:text-blue-400 mb-3 transition-colors" />
                    <p className="text-gray-500 font-medium">Tap to upload photos</p>
                    <p className="text-gray-400 text-xs mt-1">(Front, Back, Label)</p>
                  </div>
                  <input type="file" onChange={handleImageUpload} className="hidden" accept="image/*" multiple />
              </label>
            )}

            {/* INPUT FIELDS */}
            <div className="w-full mb-4 space-y-4 max-w-lg">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-gray-700 text-sm font-bold flex items-center gap-2">
                    <Sparkles size={16} className="text-yellow-500" />
                    Unique Features
                  </label>
                  <AudioRecorder onTranscriptionComplete={handleVoiceInput} />
                </div>
                <textarea
                  className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-sm bg-gray-50"
                  placeholder="Type or Speak (e.g. 'Pure cotton shirt...')"
                  rows="2"
                  value={features}
                  onChange={(e) => setFeatures(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-gray-700 text-sm font-bold mb-1">
                  Expected Price (₹) <span className="text-gray-400 font-normal text-xs">(Optional)</span>
                </label>
                <input
                  type="number"
                  className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-sm bg-gray-50"
                  placeholder="e.g. 1500"
                  value={userPrice}
                  onChange={(e) => setUserPrice(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {/* ERROR STATE */}
        {result && result.status === "error" && (
          <div className="p-8 text-center max-w-md mx-auto">
            <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-4 flex items-center gap-3 text-left border border-red-100">
              <AlertCircle size={24} className="shrink-0" />
              <div>
                <p className="font-bold">Analysis Failed</p>
                <p className="text-sm">{result.message}</p>
              </div>
            </div>
            <button
              onClick={() => setResult(null)}
              className="w-full border border-gray-300 py-3 rounded-xl text-gray-500 hover:bg-gray-50 transition"
            >
              Try Again
            </button>
          </div>
        )}

        {/* SUCCESS STATE */}
        {result && result.status === "success" && (
          <div className="p-6 md:p-8">
            
            {/* Header: Name, Brand, Badges, Price */}
            <div className="flex flex-col md:flex-row justify-between items-start mb-8 border-b border-gray-100 pb-6 gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                   {result.brand && result.brand !== "Unknown Brand" && (
                       <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">{result.brand}</span>
                   )}
                </div>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-900 leading-tight">
                  {result.product_name}
                </h2>

                <div className="flex flex-wrap gap-2 mt-3">
                  <span className="bg-purple-100 text-purple-800 text-xs font-bold px-3 py-1 rounded-full border border-purple-200 shadow-sm flex items-center gap-1">
                    💎 {result.material}
                  </span>
                  <span className="bg-green-100 text-green-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider flex items-center gap-1">
                    🔥 High Demand
                  </span>
                </div>

                {result.unique_tags && result.unique_tags.length > 0 && (
                  <div className="flex gap-2 mt-3 flex-wrap">
                    {result.unique_tags.map((tag, i) => (
                      <span key={i} className="bg-yellow-50 text-yellow-700 text-[10px] font-medium border border-yellow-200 px-2 py-1 rounded-md flex items-center gap-1">
                        ✨ {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="text-left md:text-right bg-blue-50 p-4 rounded-2xl border border-blue-100 min-w-[200px]">
                <p className="text-blue-500 text-xs font-bold uppercase tracking-wider mb-1">Recommended Price</p>
                <p className="text-4xl font-extrabold text-blue-600 tracking-tight">{result.suggested_price}</p>
                {result.pricing_reason && (
                    <div className="mt-2 text-xs text-blue-800 bg-white/60 p-2 rounded-lg leading-snug">
                      📈 {result.pricing_reason}
                    </div>
                )}
              </div>
            </div>

            {/* Price Graph & Sources */}
            {result.market_stats && (
                <div className="w-full mb-8">
                  <div className="bg-gray-50 p-6 rounded-2xl border border-gray-100">
                      <div className="flex justify-between text-xs text-gray-400 mb-2 font-medium uppercase tracking-wide">
                        <span>Economy (₹{result.market_stats.min})</span>
                        <span>Luxury (₹{result.market_stats.max})</span>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="relative h-4 bg-gray-200 rounded-full w-full mb-2">
                        {/* Avg Marker */}
                        <div className="absolute top-0 bottom-0 w-1 bg-gray-400 opacity-30 z-0" style={{ left: `${calculatePosition(result.market_stats.min, result.market_stats.max, result.market_stats.avg)}%` }}></div>
                        
                        {/* Your Price Dot */}
                        <div 
                            className="absolute top-1/2 -translate-y-1/2 w-6 h-6 bg-blue-600 border-4 border-white rounded-full shadow-lg z-10 transition-all duration-1000 ease-out" 
                            style={{ left: `${calculatePosition(result.market_stats.min, result.market_stats.max, result.raw_price)}%` }}
                        ></div>
                      </div>

                      <div className="flex justify-center mt-1">
                          <span className="text-xs text-gray-500 font-medium">Market Average: ₹{result.market_stats.avg}</span>
                      </div>
                  
                      {/* ✅ SOURCES DISPLAY (The part you asked for) */}
                      {result.market_stats.sources && result.market_stats.sources.length > 0 && (
                          <div className="mt-6 pt-4 border-t border-gray-200">
                            <p className="text-[10px] text-gray-400 uppercase font-bold tracking-wider mb-3">
                              Price Comparisons From
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {result.market_stats.sources.map((source, idx) => (
                                    <span key={idx} className="bg-white text-gray-600 text-xs font-semibold px-3 py-1.5 rounded-lg border border-gray-200 shadow-sm flex items-center gap-1.5">
                                        🌍 {source}
                                    </span>
                                ))}
                            </div>
                          </div>
                      )}
                  </div>
                </div>
            )}

            {/* Advice Section */}
            {result.photo_advice && result.photo_advice.length > 0 && (
                <div className="mb-8">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-3">Photo Coach 📸</h3>
                    <div className="grid md:grid-cols-2 gap-3">
                        {result.photo_advice.map((tip, i) => (
                            <div key={i} className="bg-orange-50 text-orange-800 text-sm p-3 rounded-xl border border-orange-100 flex items-center">
                                {tip}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Listings Grid */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* WhatsApp */}
              <div className="bg-green-50 p-5 rounded-2xl border border-green-100 flex flex-col h-full">
                <h3 className="text-xs font-bold text-green-700 mb-3 uppercase flex items-center gap-2">
                    <Share2 size={16} /> WhatsApp Message
                </h3>
                <div className="flex-grow">
                    <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap bg-white p-4 rounded-xl border border-green-100 shadow-sm font-medium">
                        {result.listings.whatsapp}
                    </p>
                </div>
                <button className="mt-4 w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-xl font-bold text-sm transition shadow-lg shadow-green-200">
                  Copy Message
                </button>
              </div>

              {/* Amazon */}
              <div className="bg-gray-50 p-5 rounded-2xl border border-gray-200 flex flex-col h-full">
                <h3 className="text-xs font-bold text-gray-500 mb-3 uppercase tracking-wide">
                  Marketplace Listing
                </h3>
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex-grow">
                    <p className="text-gray-900 font-bold text-sm mb-3 leading-snug">{result.listings.amazon.title}</p>
                    <ul className="space-y-2">
                      {result.listings.amazon.features.map((f, i) => (
                        <li key={i} className="text-xs text-gray-600 flex items-start gap-2">
                            <span className="text-blue-500 mt-0.5">•</span> {f}
                        </li>
                      ))}
                    </ul>
                </div>
                <button className="mt-4 w-full bg-gray-800 hover:bg-gray-900 text-white py-3 rounded-xl font-bold text-sm transition">
                  Copy Listing
                </button>
              </div>
            </div>

            <button
              onClick={() => { setResult(null); setImagePreviews([]); setSelectedFiles([]); setFeatures(""); }}
              className="mt-10 w-full border-2 border-dashed border-gray-300 py-4 rounded-2xl text-gray-500 text-sm font-bold hover:bg-gray-50 hover:border-gray-400 transition"
            >
              Scan Another Item
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;