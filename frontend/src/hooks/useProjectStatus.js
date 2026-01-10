import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = "http://localhost:8000";

export const useProjectStatus = (projectId) => {
  const [status, setStatus] = useState('IDLE');
  const [metadata, setMetadata] = useState(null);

  useEffect(() => {
    // flag to prevent state updates if the project changes while a request is pending
    let isCurrentProject = true; 

    // reset state immediately when switching projects or if projectId is null
    if (!projectId) {
      setStatus('IDLE');
      setMetadata(null);
      return;
    }

    const fetchStatus = async () => {
      try {
        const res = await axios.get(`${API_BASE}/${projectId}/status`);
        
        // only update if the component hasn't been unmounted or project hasn't changed
        if (isCurrentProject) {
          setStatus(res.data.status);
          setMetadata(res.data);
          
          // stop polling if we reach a final state
          if (res.data.status === 'COMPLETED' || res.data.status === 'FAILED') {
            clearInterval(pollInterval);
          }
        }
      } catch (err) {
        if (isCurrentProject) {
          console.error("polling error:", err);
        }
      }
    };

    // set up the polling timer
    const pollInterval = setInterval(fetchStatus, 3000);
    
    // trigger initial fetch
    fetchStatus();

    // cleanup function: stops the timer and invalidates the pending request
    return () => {
      isCurrentProject = false;
      clearInterval(pollInterval);
    };
  }, [projectId]); // effect re-runs whenever projectId changes

  return { status, metadata };
};