import { useState } from 'react';
import { Files, Plus, Loader2, CheckCircle2, Video, X } from 'lucide-react';

export default function BRollSection({ onUpload, disabled }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [hasUploaded, setHasUploaded] = useState(false);

  const handleFileSelection = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      setSelectedFiles(prev => [...prev, ...files]);
      setHasUploaded(false); // reset success state if new files are added
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUploadClick = async () => {
    if (selectedFiles.length === 0) return;
    
    setIsUploading(true);
    try {
      await onUpload(selectedFiles);
      setHasUploaded(true);
      setSelectedFiles([]); // clear list after successful handoff
    } catch (err) {
      console.error("upload failed", err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className={`relative p-8 rounded-[32px] border-2 border-dashed transition-all duration-500 ${
      hasUploaded 
        ? 'border-purple-300 bg-purple-50/50' 
        : 'border-purple-200 bg-purple-50/30 hover:border-purple-400'
    }`}>
      
      {/* processing overlay */}
      {isUploading && (
        <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] rounded-[32px] flex items-center justify-center z-10">
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            <span className="text-xs font-bold text-purple-600 uppercase tracking-tighter">Syncing Clips...</span>
          </div>
        </div>
      )}

      <div className="flex flex-col items-center text-center">
        <div className={`p-5 rounded-[24px] mb-4 transition-all ${hasUploaded ? 'bg-purple-600 scale-110' : 'bg-white shadow-sm'}`}>
          <Files className={`w-8 h-8 ${hasUploaded ? 'text-white' : 'text-purple-600'}`} />
        </div>
        
        <h3 className="text-lg font-black text-slate-800 tracking-tight">B-Roll Gallery</h3>
        <p className="text-sm text-slate-500 mb-6">Add your supporting clips</p>

        <div className="w-full space-y-4">
          {/* file list preview */}
          {selectedFiles.length > 0 && !hasUploaded && (
            <div className="bg-white/50 rounded-2xl p-3 border border-purple-100 max-h-32 overflow-y-auto space-y-2 mb-4 animate-in slide-in-from-top-2">
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="flex items-center justify-between bg-white px-3 py-2 rounded-xl border border-purple-50">
                  <div className="flex items-center gap-2 overflow-hidden">
                    <Video className="w-3 h-3 text-purple-400 flex-shrink-0" />
                    <span className="text-[10px] font-medium text-slate-600 truncate">{file.name}</span>
                  </div>
                  <button onClick={() => removeFile(idx)} className="text-slate-300 hover:text-red-400">
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <label className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-white border border-purple-200 text-purple-600 rounded-2xl font-bold cursor-pointer hover:bg-purple-50 transition-all ${disabled ? 'opacity-40 pointer-events-none' : ''}`}>
              <Plus className="w-4 h-4" />
              <span className="text-sm">Add Clips</span>
              <input type="file" className="hidden" multiple accept="video/*" onChange={handleFileSelection} />
            </label>

            {selectedFiles.length > 0 && (
              <button 
                onClick={handleUploadClick}
                className="flex-[1.5] py-3 bg-purple-600 text-white rounded-2xl font-bold shadow-lg shadow-purple-100 hover:bg-purple-700 active:scale-95 transition-all animate-in zoom-in"
              >
                Upload {selectedFiles.length} {selectedFiles.length === 1 ? 'Clip' : 'Clips'}
              </button>
            )}
          </div>

          {hasUploaded && (
            <div className="flex items-center justify-center gap-2 py-2 text-purple-600 animate-in fade-in">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-widest">Library Updated</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}