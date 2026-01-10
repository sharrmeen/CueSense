import { FileText, ArrowLeft, ExternalLink } from 'lucide-react';

export default function LibraryPage({ projects, onBack, onSelectProject }) {
  return (
    <div className="min-h-screen bg-slate-50 py-12 animate-in fade-in duration-500">
      <div className="max-w-4xl mx-auto px-6">
        {/* Navigation Header */}
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-slate-400 hover:text-indigo-600 font-bold mb-8 transition-colors group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          Back to Editor
        </button>

        <h1 className="text-4xl font-black text-slate-800 italic uppercase tracking-tighter mb-12">
          Project Library
        </h1>

        <div className="grid gap-8">
          {projects.length === 0 ? (
            <div className="p-20 text-center bg-white rounded-[40px] border-2 border-dashed border-slate-200 text-slate-400 italic">
              No completed projects found.
            </div>
          ) : (
            projects.map((proj) => (
              <div key={proj.project_id} className="bg-white p-10 rounded-[40px] shadow-xl shadow-slate-200/50 border border-slate-100">
                <div className="flex justify-between items-center mb-8 pb-6 border-b border-slate-50">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-indigo-500 text-white rounded-2xl">
                      <FileText className="w-6 h-6" />
                    </div>
                    <h3 className="text-2xl font-black text-slate-800 tracking-tight uppercase italic">{proj.name}</h3>
                  </div>
                  <button 
                    onClick={() => onSelectProject(proj.project_id)}
                    className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-indigo-500 hover:bg-indigo-50 px-4 py-2 rounded-full ring-1 ring-indigo-100 transition-all"
                  >
                    Open in Editor <ExternalLink className="w-3 h-3" />
                  </button>
                </div>

                {/* The Edit Plan List */}
                <div className="space-y-3">
                  {proj.edit_plan?.map((step, i) => (
                    <div key={i} className="flex items-start gap-4 p-4 bg-slate-50 rounded-2xl border border-slate-100">
                      <span className="text-xs font-black text-indigo-600 bg-white px-3 py-1 rounded-lg shadow-sm border border-slate-100">
                        @{step.start_in_aroll}s
                      </span>
                      <p className="text-xs text-slate-600 font-medium italic leading-relaxed">
                        "{step.reason}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}