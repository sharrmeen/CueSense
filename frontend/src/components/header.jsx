import { Video } from 'lucide-react';

export default function Header({ projectId }) {
  return (
    <header className="flex justify-between items-center py-6 border-b border-zinc-800 mb-10">
      <div className="flex items-center gap-3">
        <div className="bg-blue-600 p-2 rounded-lg">
          <Video className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-600">CueSense</h1>
      </div>
      
      {projectId && (
        <div className="flex items-center gap-2 px-4 py-1.5 bg-zinc-900 border border-zinc-800 rounded-full">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span className="text-sm font-mono text-zinc-400">proj_{projectId}</span>
        </div>
      )}
    </header>
  );
}