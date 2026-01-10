import { useState } from 'react';
import axios from 'axios';
import Header from './components/header';
import ARollSection from './components/aRollSection';
import BRollSection from './components/bRollSection';
import StatusCard from './components/StatusCard';
import LibraryPage from './components/ProjectHistory';
import { useProjectStatus } from './hooks/useProjectStatus';

const API_BASE = "http://localhost:8000";

export default function App() {
  const [projectId, setProjectId] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [showLibrary, setShowLibrary] = useState(false);
  const [projects, setProjects] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  
  // Polling hook to track backend status and metadata
  const { status, metadata } = useProjectStatus(projectId);
  const openLibrary = async () => {
    const res = await axios.get(`${API_BASE}/list-projects`);
    setProjects(res.data);
    setShowLibrary(true);
  };

  // Creates project using the name provided by the user
  const initProject = async () => {
    if (!projectName.trim()) {
      alert("Please enter a name for your project!");
      return;
    }
    try {
      setProjectId(null); 
      setIsUploading(false);
      const res = await axios.post(`${API_BASE}/create-project?name=${projectName}`);
      setProjectId(res.data.project_id);
      setProjectName('');
    } catch (err) {
      console.error(err.message);
      alert("Backend connection failed. Please ensure the server is running.");
    }
  };

  // Handles the main video file upload
  const onARollUpload = async (file) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      await axios.post(`${API_BASE}/a-roll?project_id=${projectId}`, formData);
    } catch (err) {
      console.error("a-roll upload failed", err);
    } finally {
      setIsUploading(false);
    }
  };

  // Handles uploading multiple supplementary clips
  const onBRollUpload = async (files) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));
      await axios.post(`${API_BASE}/b-roll?project_id=${projectId}`, formData);
      // Note: metadata.b_roll_count will update on the next poll
    } catch (err) {
      console.error("b-roll upload failed", err);
    } finally {
      setIsUploading(false);
    }
  };

  // Step 1: Trigger AI analysis of all B-roll clips
  const onAnalyzeBroll = () => axios.post(`${API_BASE}/${projectId}/analyze-broll`);

  // Step 2: Trigger timeline matching logic
  const onGenerate = () => axios.post(`${API_BASE}/${projectId}/generate-edit-plan`);
  
  // Final Step: Trigger the FFmpeg rendering stage
  const onRender = () => axios.post(`${API_BASE}/${projectId}/render`);

    if (showLibrary) {
      return (
        <LibraryPage 
          projects={projects} 
          onBack={() => setShowLibrary(false)} 
          onSelectProject={(id) => {
            setProjectId(id);
            setShowLibrary(false); 
          }}
        />
      );
    }

  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-indigo-100">
      <div className="max-w-4xl mx-auto px-6 pb-20">

      <div className="flex justify-end pt-8">
           <button 
             onClick={openLibrary}
             className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 hover:text-indigo-500 transition-colors flex items-center gap-2"
           >
             <span className="w-2 h-2 bg-slate-200 rounded-full" />
             View Project Library
           </button>
        </div>

        <Header projectId={projectName} />

        {!projectId ? (
          <div className="flex flex-col items-center justify-center py-24 bg-white rounded-[40px] border-2 border-dashed border-slate-200 shadow-sm">
            <h2 className="text-3xl font-black text-slate-800 mb-2">Welcome to B-Roll AI</h2>
            <p className="text-slate-500 mb-8 font-medium text-center max-w-sm">
              Create professional edits automatically using Gemini and FFmpeg.
            </p>
            
            <div className="flex flex-col gap-4 w-full max-w-sm px-4">
              <input 
                type="text"
                placeholder="Enter Project Name..."
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="px-6 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-400 transition-all font-medium text-slate-700"
              />
              <button 
                onClick={initProject} 
                className="px-10 py-4 bg-indigo-500 text-white rounded-2xl font-bold shadow-xl shadow-indigo-100 hover:bg-indigo-600 transition-all active:scale-95 disabled:bg-slate-300 disabled:shadow-none"
                disabled={!projectName.trim()}
              >
                + Create New Project
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            
            {/* result video preview once completed */}
            {status === 'COMPLETED' && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-slate-800 ml-2">Final Master Cut</h3>
                <div className="overflow-hidden rounded-[40px] bg-black shadow-2xl ring-1 ring-slate-200">
                  <video 
                    controls 
                    className="w-full h-auto aspect-video"
                    src={`${API_BASE}/${projectId}/download`}
                  />
                </div>
              </div>
            )}

            {/* upload section for video assets */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ARollSection 
                onUpload={onARollUpload} 
                // Strict check: Only show success if metadata confirms duration > 0
                isUploaded={metadata?.a_roll_duration > 0} 
                disabled={isUploading}
              />
              <BRollSection 
                onUpload={onBRollUpload} 
                disabled={isUploading}
              />
            </div>
            
            {/* dashboard controls for pipeline execution */}
            <StatusCard 
              status={status} 
              projectId={projectId}
              metadata={metadata} // Passing full metadata for b_roll_count
              editPlan={metadata?.edit_plan}
              onAnalyzeBroll={onAnalyzeBroll}
              onGenerate={onGenerate}
              onRender={onRender}
            />

            {/* project status footer summary */}
            <div className="flex justify-between items-center px-4 py-2 bg-slate-100 rounded-xl text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              <span>B-Roll Clips: {metadata?.b_roll_count || 0}</span>
              <span>A-Roll Length: {metadata?.a_roll_duration?.toFixed(1) || 0}s</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}