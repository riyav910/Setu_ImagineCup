import { useState } from 'react';
import axios from 'axios';
import { Camera, Upload, Share2, AlertCircle, Sparkles, X } from 'lucide-react';
import AudioRecorder from './AudioRecorder';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  // ✅ STATE: Only keep the plural versions
  const [imagePreviews, setImagePreviews] = useState([]); 
  const [selectedFiles, setSelectedFiles] = useState([]);
  
  const [features, setFeatures] = useState("");
  const [userPrice, setUserPrice] = useState("");

  // 1. HANDLE FILE SELECTION (Just Preview, Don't Upload Yet)
  const handleImageUpload = (event) => {
    const inputFiles = event.target.files;
    if (!inputFiles || inputFiles.length === 0) return;

    const files = Array.from(inputFiles);
    const newPreviews = files.map((file) => URL.createObjectURL(file));

    // Update State Only
    setSelectedFiles(files);
    setImagePreviews(newPreviews);
    setResult(null); // Clear previous results
    
    // ❌ REMOVED: setImagePreview(...) -> This caused the crash
    // ❌ REMOVED: axios.post call -> We wait for the button click now
  };

  // 2. SUBMIT TO BACKEND (Triggered by Button)
  const submitAnalysis = async () => {
    if (selectedFiles.length === 0) return;
    setLoading(true);

    const formData = new FormData();

    // Append stored files
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
      setResult({ status: "error", message: "Failed to connect." });
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceInput = (text) => {
    setFeatures((prev) => prev ? `${prev} ${text}` : text);
  };

  const calculatePosition = (min, max, current) => {
    if (!min || !max || !current) return 50;
    const range = max - min;
    const position = ((current - min) / range) * 100;
    return Math.min(Math.max(position, 0), 100); 
  };

  // 3. HELPER TO REMOVE IMAGE (Optional but good UX)
  const removeImage = (index) => {
     const newFiles = selectedFiles.filter((_, i) => i !== index);
     const newPreviews = imagePreviews.filter((_, i) => i !== index);
     setSelectedFiles(newFiles);
     setImagePreviews(newPreviews);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4 font-sans">
      <header className="w-full max-w-md bg-white rounded-2xl shadow-sm p-4 mb-6 text-center">
        <h1 className="text-2xl font-bold text-blue-600 tracking-tight">Setu AI 🛍️</h1>
        <p className="text-gray-500 text-sm">Selling made simple.</p>
      </header>

      <main className="w-full max-w-md bg-white rounded-3xl shadow-xl overflow-hidden transition-all duration-300">

        {/* INPUT SECTION */}
        {!result && (
          <div className="p-8 flex flex-col items-center justify-center min-h-[400px]">
            
            {/* GALLERY PREVIEW GRID */}
            {imagePreviews.length > 0 ? (
              <div className="w-full mb-6">
                <div className="grid grid-cols-2 gap-2">
                  {imagePreviews.map((src, idx) => (
                    <div key={idx} className="relative aspect-square rounded-xl overflow-hidden shadow-sm group">
                      <img src={src} alt={`Preview ${idx}`} className="w-full h-full object-cover" />
                      {/* Delete Button overlay */}
                      <button 
                         onClick={() => removeImage(idx)}
                         className="absolute top-1 right-1 bg-black/50 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition"
                      >
                         <X size={12} />
                      </button>
                    </div>
                  ))}
                  {/* "Add More" Button (Optional) */}
                   <label className="aspect-square border-2 border-dashed border-gray-300 rounded-xl flex items-center justify-center cursor-pointer hover:bg-gray-50 text-gray-400">
                        <input type="file" onChange={(e) => {
                             if(e.target.files.length > 0) {
                                 const newF = Array.from(e.target.files);
                                 const newP = newF.map(f => URL.createObjectURL(f));
                                 setSelectedFiles([...selectedFiles, ...newF]);
                                 setImagePreviews([...imagePreviews, ...newP]);
                             }
                        }} className="hidden" accept="image/*" multiple />
                        <span className="text-2xl">+</span>
                   </label>
                </div>
                
                <p className="text-center text-xs text-gray-400 mt-2">{selectedFiles.length} photos selected</p>

                {/* ANALYZE BUTTON (Only appears when images are selected) */}
                <button
                  onClick={submitAnalysis}
                  disabled={loading}
                  className="w-full mt-4 bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition flex justify-center items-center gap-2"
                >
                  {loading ? (
                       <> <Sparkles className="animate-spin" size={16}/> Analyzing... </>
                  ) : (
                       `Analyze ${selectedFiles.length} Photos`
                  )}
                </button>
              </div>
            ) : (
              // EMPTY STATE (Camera Icon)
              <label className="w-full cursor-pointer">
                  <div className="border-2 border-dashed border-gray-300 rounded-xl p-10 mb-6 w-full flex flex-col items-center hover:bg-gray-50 transition-colors">
                    <Camera className="w-12 h-12 text-gray-400 mb-2" />
                    <p className="text-gray-400 text-sm">Tap to take photos</p>
                  </div>
                  <input type="file" onChange={handleImageUpload} className="hidden" accept="image/*" multiple />
              </label>
            )}

            {/* INPUT FIELDS CONTAINER (Keep showing this even if images are selected) */}
            <div className="w-full mb-4 space-y-3">
              {/* Uniqueness Input */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-gray-700 text-sm font-bold flex items-center gap-2">
                    <Sparkles size={16} className="text-yellow-500" />
                    Unique Features (Optional)
                  </label>
                  <AudioRecorder onTranscriptionComplete={handleVoiceInput} />
                </div>
                <textarea
                  className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 text-sm bg-gray-50"
                  placeholder="Type or Speak (e.g. 'Yeh banarasi saree hai...')"
                  rows="2"
                  value={features}
                  onChange={(e) => setFeatures(e.target.value)}
                />
              </div>

              {/* Price Input */}
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-1">
                  Expected Price (₹) <span className="text-gray-400 font-normal text-xs">(If you have one)</span>
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

            {/* Initial Big Upload Button (Only show if no images selected yet) */}
            {imagePreviews.length === 0 && (
                 <label className="w-full">
                    <input type="file" onChange={handleImageUpload} className="hidden" accept="image/*" multiple />
                    <div className="bg-blue-600 text-white font-bold py-4 rounded-xl text-center cursor-pointer hover:bg-blue-700 transition shadow-lg shadow-blue-200">
                        Select Photos
                    </div>
                </label>
            )}
          </div>
        )}

        {/* ERROR STATE */}
        {result && result.status === "error" && (
          <div className="p-6 text-center">
            <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-4 flex items-center gap-3 text-left">
              <AlertCircle size={24} className="shrink-0" />
              <div>
                <p className="font-bold">Analysis Failed</p>
                <p className="text-sm">{result.message}</p>
                {result.details && <p className="text-xs mt-1 opacity-75 break-all">{result.details}</p>}
              </div>
            </div>
            <button
              onClick={() => { setResult(null); }}
              className="w-full border border-gray-300 py-3 rounded-xl text-gray-500 hover:bg-gray-50 transition"
            >
              Try Again
            </button>
          </div>
        )}

        {/* SUCCESS STATE */}
        {result && result.status === "success" && (
          <div className="p-6">
            <div className="flex justify-between items-start mb-6 border-b border-gray-100 pb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-800 leading-tight">
                  {result.product_name}
                </h2>

                {/* MATERIAL BADGE */}
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="bg-purple-100 text-purple-800 text-xs font-bold px-3 py-1 rounded-full border border-purple-200 shadow-sm flex items-center gap-1">
                    💎 {result.material}
                  </span>
                  <span className="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wider flex items-center">
                    🔥 High Demand
                  </span>
                </div>

                {/* Unique Tags */}
                {result.unique_tags && result.unique_tags.length > 0 && (
                  <div className="flex gap-1 mt-2 flex-wrap">
                    {result.unique_tags.map((tag, i) => (
                      <span key={i} className="bg-yellow-50 text-yellow-700 text-[10px] border border-yellow-200 px-2 py-0.5 rounded-md flex items-center gap-1">
                        ✨ {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Price Display */}
              <div className="text-right flex flex-col items-end">
                <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider">Recommended Price</p>
                <p className="text-3xl font-extrabold text-blue-600">{result.suggested_price}</p>
                {result.pricing_reason && (
                    <span className="text-[10px] bg-white text-blue-700 px-2 py-1 rounded border border-blue-200 shadow-sm max-w-[120px] text-right leading-tight mt-1">
                      📈 {result.pricing_reason}
                    </span>
                )}
              </div>
            </div>

            {/* Price Graph */}
            {result.market_stats && (
                <div className="w-full mt-6 bg-blue-50 p-4 rounded-xl border border-blue-100 mb-6">
                  <div className="relative h-2 bg-gray-200 rounded-full w-full mt-2">
                    <div className="absolute top-0 bottom-0 w-1 bg-gray-400 opacity-50" style={{ left: `${calculatePosition(result.market_stats.min, result.market_stats.max, result.market_stats.avg)}%` }}></div>
                    <div className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-blue-600 border-2 border-white rounded-full shadow-md" style={{ left: `${calculatePosition(result.market_stats.min, result.market_stats.max, result.raw_price)}%` }}></div>
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-500 mt-2 font-medium">
                    <span>Cheap (₹{result.market_stats.min})</span>
                    <span className="text-gray-400">Avg Market</span>
                    <span>Luxury (₹{result.market_stats.max})</span>
                  </div>
                  
                  {/* Sources */}
                  {result.market_stats.sources && (
                      <div className="mt-4 pt-4 border-t border-blue-200">
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-2">Verified Prices From</p>
                        <div className="flex flex-wrap gap-2">
                            {result.market_stats.sources.map((source, idx) => (
                                <span key={idx} className="bg-white text-blue-600 text-xs font-medium px-2 py-1 rounded border border-blue-100 shadow-sm">🌍 {source}</span>
                            ))}
                        </div>
                      </div>
                  )}
                </div>
            )}

            {/* Listings (WhatsApp / Amazon) */}
            <div className="space-y-4">
              <div className="bg-green-50 p-4 rounded-xl border border-green-100">
                <h3 className="text-xs font-bold text-green-700 mb-2 uppercase flex items-center gap-2"><Share2 size={14} /> WhatsApp Message</h3>
                <p className="text-gray-700 text-sm italic bg-white p-3 rounded-lg border border-green-100 shadow-sm">"{result.listings.whatsapp}"</p>
              </div>

              <div className="bg-gray-50 p-4 rounded-xl border border-gray-200">
                <h3 className="text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">E-commerce Listing</h3>
                <p className="text-gray-900 font-bold text-sm mb-2">{result.listings.amazon.title}</p>
                <ul className="space-y-1">
                  {result.listings.amazon.features.map((f, i) => (
                    <li key={i} className="text-xs text-gray-600 flex items-start gap-2"><span className="text-blue-500 mt-0.5">•</span> {f}</li>
                  ))}
                </ul>
              </div>
            </div>

            <button
              onClick={() => { setResult(null); setImagePreviews([]); setSelectedFiles([]); setFeatures(""); }}
              className="mt-8 w-full border border-gray-300 py-3 rounded-xl text-gray-500 text-sm font-medium hover:bg-gray-50 transition"
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