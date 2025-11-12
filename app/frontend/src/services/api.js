import axios from 'axios';

// Unified API base (proxy handles routing to backend)
const API_BASE = '';

// ==================== RAG API ====================
export const uploadRAGFile = async (balanceSheet, companyProfile = null) => {
  const formData = new FormData();
  formData.append('balance_sheet', balanceSheet);
  if (companyProfile) {
    formData.append('company_profile', companyProfile);
  }
  
  try {
    const response = await axios.post(`${API_BASE}/api/rag/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Upload failed');
  }
};

export const sendChatMessage = async (sessionId, question, chatHistory) => {
  try {
    const response = await axios.post(`${API_BASE}/api/rag/chat`, {
      session_id: sessionId,
      question: question,
      chat_history: chatHistory
    });
    
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Chat request failed');
  }
};

// ==================== PPT API ====================
export const uploadPPTFiles = async (balanceSheet, companyProfile) => {
  const formData = new FormData();
  formData.append('balance_sheet', balanceSheet);
  formData.append('company_profile', companyProfile);
  
  try {
    const response = await axios.post(`${API_BASE}/api/ppt/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Upload failed');
  }
};

export const generatePresentation = async (sessionId, slides, template, theme) => {
  try {
    const response = await axios.post(`${API_BASE}/api/ppt/generate`, {
      session_id: sessionId,
      slides: slides,
      template: template,
      theme: theme
    });
    
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Generation failed');
  }
};

export const downloadPresentation = async (sessionId) => {
  try {
    const response = await axios.get(`${API_BASE}/api/ppt/download/${sessionId}`, {
      responseType: 'blob'
    });
    
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Download failed');
  }
};

export const previewSlides = async (sessionId) => {
  try {
    const response = await axios.get(`${API_BASE}/api/ppt/preview/${sessionId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Preview failed');
  }
};
