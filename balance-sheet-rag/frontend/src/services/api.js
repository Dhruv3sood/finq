import axios from 'axios';

const API_BASE_URL = 'http://localhost:5002/api';

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
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
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      session_id: sessionId,
      question: question,
      chat_history: chatHistory
    });
    
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message || 'Chat request failed');
  }
};