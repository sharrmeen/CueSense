import { Sparkles, Clapperboard, Download, Loader2, AlertCircle, ListChecks, FileWarning, Video, CheckCircle } from 'lucide-react';

export default function StatusCard({ status, onAnalyzeBroll, onGenerate, onRender, projectId, editPlan, metadata }) {
  
  const bRollCount = metadata?.b_roll_count || 0;
  
  const renderActions = () => {
    switch (status) {
      case 'TRANSCRIPTION_COMPLETE':
      case 'BROLL_ANALYZED':
        return (
          <div className="space-y-4">
            {/* Warning if no B-Rolls are present */}
            {bRollCount === 0 && (
              <div className="flex items-center gap-3 p-4 bg-amber-50 text-amber-700 rounded-2xl border border-amber-100 text-sm font-medium animate-in fade-in slide-in-from-top-2">
                <FileWarning className="w-5 h-5 flex-shrink-0" />
                <span>Upload B-Roll clips to enable the analysis step.</span>
              </div>
            )}

            {/* STEP 1: Analyze B-Rolls */}
            <div className="relative">
              <button 
                onClick={onAnalyzeBroll}
                disabled={bRollCount === 0 || status === 'BROLL_ANALYZED'}
                className={`w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-bold transition-all border-2
                  ${status === 'BROLL_ANALYZED' 
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-700 cursor-default' 
                    : bRollCount > 0 
                      ? 'bg-amber-500 border-amber-400 text-white shadow-lg hover:bg-amber-600 active:scale-95' 
                      : 'bg-slate-50 border-slate-100 text-slate-300 cursor-not-allowed'
                  }`}
              >
                {status === 'BROLL_ANALYZED' ? <CheckCircle className="w-5 h-5" /> : <Video className="w-5 h-5" />}
                {status === 'BROLL_ANALYZED' ? '1. B-Roll Library Analyzed' : '1. Analyze B-Roll Library'}
              </button>
              {status === 'BROLL_ANALYZED' && (
                <span className="absolute -top-2 -right-2 bg-emerald-500 text-white text-[10px] font-black px-2 py-0.5 rounded-full shadow-sm">DONE</span>
              )}
            </div>

            {/* STEP 2: Generate Plan (Locked until Step 1 is done) */}
            <button 
              onClick={onGenerate}
              disabled={status !== 'BROLL_ANALYZED'}
              className={`w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-bold shadow-lg transition-all 
                ${status === 'BROLL_ANALYZED' 
                  ? 'bg-indigo-500 text-white shadow-indigo-100 hover:bg-indigo-600 hover:scale-[1.02] active:scale-95' 
                  : 'bg-slate-100 text-slate-300 cursor-not-allowed border-2 border-dashed border-slate-200 shadow-none'
                }`}
            >
              <Sparkles className={`w-5 h-5 ${status === 'BROLL_ANALYZED' ? 'animate-pulse' : ''}`} />
              2. Generate AI Edit Plan
            </button>
          </div>
        );
      
      // StatusCard.jsx - PLAN_READY section
    case 'PLAN_READY':
    return (
      <div className="space-y-4">
        <div className="bg-slate-50 border border-slate-100 rounded-[24px] p-6 shadow-inner">
          <div className="flex items-center gap-2 mb-4 text-slate-600 font-black text-xs uppercase tracking-widest">
            <ListChecks className="w-4 h-4 text-indigo-500" />
            AI Master Edit Plan
          </div>
          
          {/* Changed max-height and allowed vertical scrolling for long plans */}
          <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
            {editPlan?.map((item, idx) => (
              <div key={idx} className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:border-indigo-200 transition-colors group">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-black text-indigo-600 bg-indigo-50 px-3 py-1 rounded-lg text-xs">
                    @{item.start_in_aroll}s
                  </span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
                    Clip: {item.broll_id.replace('.mp4', '')}
                  </span>
                </div>
                
                {/* Removed 'truncate' to show the full text */}
                <p className="text-slate-600 text-xs leading-relaxed font-medium italic">
                  "{item.reason}"
                </p>
                
                <div className="mt-2 text-[10px] font-bold text-indigo-300">
                  Duration: {item.duration}s
                </div>
              </div>
            ))}
          </div>
        </div>
  
        <button 
          onClick={onRender}
          className="w-full flex items-center justify-center gap-2 py-5 bg-rose-500 text-white rounded-2xl font-black shadow-lg shadow-rose-100 hover:bg-rose-600 transition-all hover:scale-[1.02] active:scale-95"
        >
          <Clapperboard className="w-5 h-5" />
          Render Final Video
        </button>
      </div>
    );

      case 'COMPLETED':
        return (
          <div className="flex flex-col gap-4">
            <div className="p-6 bg-emerald-50 text-emerald-700 rounded-3xl border-2 border-emerald-100 text-center animate-in zoom-in">
              <div className="text-2xl mb-1">🎬</div>
              <span className="font-black uppercase tracking-tighter text-lg">Master Cut Ready!</span>
            </div>
            <a 
              href={`http://localhost:8000/${projectId}/download`}
              target="_blank"
              rel="noreferrer"
              className="w-full flex items-center justify-center gap-3 py-5 bg-slate-900 text-white rounded-2xl font-bold shadow-xl hover:bg-black transition-all hover:scale-[1.02] active:scale-95"
            >
              <Download className="w-6 h-6" />
              Download High-Res MP4
            </a>
          </div>
        );

      case 'FAILED':
        return (
          <div className="flex items-start gap-4 p-5 bg-red-50 text-red-600 rounded-3xl border-2 border-red-100">
            <AlertCircle className="w-6 h-6 flex-shrink-0 mt-1" />
            <div className="flex flex-col">
              <span className="font-black uppercase tracking-tight">Pipeline Error</span>
              <span className="text-xs font-medium opacity-80 leading-relaxed">The AI encountered a technical issue. Please check your backend terminal for error logs.</span>
            </div>
          </div>
        );

        default:
            // Loading states for busy background tasks
            if (['TRANSCRIBING', 'ANALYZING_BROLL', 'MATCHING_CLIPS', 'RENDERING'].includes(status)) {
              const readableStatus = status.toLowerCase()
                .replace(/_/g, ' ')
                .replace(/\b\w/g, l => l.toUpperCase());
    
              return (
                <div className="flex flex-col items-center gap-4 p-10 bg-slate-50 rounded-[32px] border-2 border-dashed border-slate-200">
                  <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
                  <div className="text-center">
                    <span className="block text-slate-800 font-black text-lg tracking-tight">
                      {readableStatus}...
                    </span>
                    
                    {/* ADDED: Granular Debug Message from Backend */}
                    {metadata?.status_message && (
                      <span className="text-xs text-indigo-500 font-mono mt-3 block bg-indigo-50 px-4 py-1.5 rounded-full border border-indigo-100 animate-pulse font-bold uppercase tracking-wider">
                        {metadata.status_message}
                      </span>
                    )}
                    
                    <span className="text-[10px] text-slate-400 uppercase font-black mt-2 block tracking-widest opacity-60">
                      AI is processing in background
                    </span>
                  </div>
                </div>
              );
            }
            return <p className="text-center text-slate-400 font-bold italic py-6">Waiting for asset uploads... ✨</p>;
    }
  };

  return (
    <div className="bg-white p-8 rounded-[40px] shadow-2xl shadow-slate-200/60 border border-slate-100 animate-in fade-in duration-700">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-xl font-black text-slate-800 tracking-tighter uppercase italic">Timeline Dashboard</h2>
        <div className="flex items-center gap-2">
           <span className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse" />
           <span className="px-4 py-1.5 bg-indigo-50 text-indigo-600 rounded-full text-[10px] font-black uppercase tracking-widest ring-1 ring-indigo-100">
            {status.replace(/_/g, ' ')}
          </span>
        </div>
      </div>
      <div className="space-y-6">{renderActions()}</div>
    </div>
  );
}