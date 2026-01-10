import { useState } from 'react';
import { UploadCloud, CheckCircle2, Loader2, Video } from 'lucide-react';

export default function ARollSection({ onUpload, disabled, isUploaded }) {
  const [localFile, setLocalFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFile = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setLocalFile(file);
      setIsProcessing(true);
      // triggers the upload function from App.jsx
      await onUpload(file);
      setIsProcessing(false);
    }
  };

  return (
    <div className={`relative p-8 rounded-[32px] border-2 border-dashed transition-all duration-500 ${
      isUploaded 
        ? 'border-emerald-200 bg-emerald-50/50 shadow-inner' 
        : 'border-indigo-200 bg-indigo-50/30 hover:border-indigo-400'
    }`}>
      
      {/* active processing overlay */}
      {isProcessing && (
        <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] rounded-[32px] flex items-center justify-center z-10 animate-in fade-in">
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
            <span className="text-xs font-bold text-indigo-600 uppercase tracking-tighter">Uploading to Server...</span>
          </div>
        </div>
      )}

      <div className="flex flex-col items-center text-center">
        {/* icon container */}
        <div className={`p-5 rounded-[24px] mb-4 transition-transform duration-500 ${
          isUploaded ? 'bg-emerald-100 scale-110' : 'bg-white shadow-sm ring-1 ring-indigo-50'
        }`}>
          {isUploaded ? (
            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
          ) : (
            <UploadCloud className={`w-8 h-8 ${disabled ? 'text-slate-300' : 'text-indigo-500'}`} />
          )}
        </div>
        
        <h3 className="text-lg font-black text-slate-800 tracking-tight">Talking Head Video</h3>
        
        {/* dynamic status text */}
        <p className="text-sm text-slate-500 mb-6 max-w-[200px]">
          {isUploaded 
            ? "The AI has received your A-Roll and is ready." 
            : "Drop your main video here to start the magic."}
        </p>

        {!isUploaded ? (
          <div className="space-y-4 w-full">
            <label className={`group flex items-center justify-center gap-2 px-6 py-3 bg-white border border-indigo-100 text-indigo-600 rounded-2xl font-bold cursor-pointer shadow-sm hover:shadow-md hover:bg-indigo-500 hover:text-white transition-all ${disabled ? 'opacity-40 pointer-events-none' : ''}`}>
              <Video className="w-4 h-4 transition-transform group-hover:scale-110" />
              Select Video
              <input type="file" className="hidden" accept="video/*" onChange={handleFile} />
            </label>
            
            {localFile && !isUploaded && (
              <div className="text-[10px] font-mono text-slate-400 truncate px-4">
                Selected: {localFile.name}
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center animate-in zoom-in duration-300">
            <span className="px-4 py-1 bg-emerald-100 text-emerald-700 rounded-full font-bold text-[10px] uppercase tracking-widest">
              Success
            </span>
          </div>
        )}
      </div>
    </div>
  );
}