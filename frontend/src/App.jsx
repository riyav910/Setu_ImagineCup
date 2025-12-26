import { useState } from 'react';
import axios from 'axios';
import { Camera, Upload, Share2, AlertCircle } from 'lucide-react'; 

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setImagePreview(URL.createObjectURL(file));
    setLoading(true);
    setResult(null); // Reset previous results

    const formData = new FormData();
    formData.append("file", file);

    try {
      const API_URL = import.meta.env.VITE_API_URL;
      const response = await axios.post(`${API_URL}/analyze`, formData);
      console.log("Backend Response:", response.data); // Debugging line
      setResult(response.data);
    } catch (error) {
      console.error("Error analyzing image:", error);
      setResult({ status: "error", message: "Failed to connect to backend." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4">
      <header className="w-full max-w-md bg-white rounded-2xl shadow-sm p-4 mb-6 text-center">
        <h1 className="text-2xl font-bold text-blue-600">Setu AI 🛍️</h1>
        <p className="text-gray-500 text-sm">Selling made simple.</p>
      </header>

      <main className="w-full max-w-md bg-white rounded-3xl shadow-xl overflow-hidden">
        
        {/* INPUT SECTION */}
        {!result && (
          <div className="p-8 flex flex-col items-center justify-center min-h-[400px]">
            {imagePreview ? (
                <div className="relative w-full h-64 rounded-xl overflow-hidden mb-6">
                  <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
                  {loading && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center text-white font-medium animate-pulse">
                      Analyzing Image...
                    </div>
                  )}
                </div>
            ) : (
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-10 mb-6 w-full flex flex-col items-center">
                  <Camera className="w-12 h-12 text-gray-400 mb-2" />
                  <p className="text-gray-400">Tap to take photo</p>
                </div>
            )}
            
            <label className="w-full">
              <input type="file" onChange={handleImageUpload} className="hidden" accept="image/*" />
              <div className="bg-blue-600 text-white font-bold py-4 rounded-xl text-center cursor-pointer hover:bg-blue-700 transition flex items-center justify-center gap-2">
                <Upload size={20} />
                {loading ? "Processing..." : "Upload Photo"}
              </div>
            </label>
          </div>
        )}

        {/* ERROR STATE (New!) */}
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
               onClick={() => {setResult(null); setImagePreview(null);}} 
               className="w-full border border-gray-300 py-3 rounded-xl text-gray-500"
             >
               Try Again
             </button>
           </div>
        )}

        {/* SUCCESS STATE */}
        {result && result.status === "success" && (
          <div className="p-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-800">{result.product_name}</h2>
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">High Demand</span>
              </div>
              <div className="text-right">
                <p className="text-gray-500 text-xs">Recommended</p>
                <p className="text-2xl font-bold text-blue-600">{result.suggested_price}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                <h3 className="text-sm font-semibold text-gray-500 mb-2 uppercase flex items-center gap-2">
                   <Share2 size={16} /> WhatsApp Message
                </h3>
                <p className="text-gray-700 italic">"{result.listings.whatsapp}"</p>
                <button className="mt-3 w-full bg-green-500 text-white py-2 rounded-lg font-medium text-sm">
                  Send to Buyers
                </button>
              </div>

              <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                <h3 className="text-sm font-semibold text-gray-500 mb-2 uppercase">
                   Amazon Listing
                </h3>
                <p className="text-gray-800 font-medium text-sm">{result.listings.amazon.title}</p>
                <ul className="list-disc list-inside text-xs text-gray-600 mt-2">
                   {result.listings.amazon.features.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </div>
            </div>

            <button 
              onClick={() => {setResult(null); setImagePreview(null);}} 
              className="mt-8 w-full border border-gray-300 py-3 rounded-xl text-gray-500 text-sm"
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