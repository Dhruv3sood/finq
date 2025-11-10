import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

export const uploadFiles = async (balanceSheet, companyProfile) => {
  const formData = new FormData();
  formData.append('balance_sheet', balanceSheet);
  formData.append('company_profile', companyProfile);
  
  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  
  return response.data;
};

export const generatePresentation = async (sessionId, slides, template, theme) => {
  const response = await axios.post(`${API_BASE_URL}/generate`, {
    session_id: sessionId,
    slides: slides,
    template: template,
    theme: theme
  });
  
  return response.data;
};

export const downloadPresentation = async (sessionId) => {
  const response = await axios.get(`${API_BASE_URL}/download/${sessionId}`, {
    responseType: 'blob'
  });
  
  return response.data;
};

export const previewSlides = async (sessionId) => {
  const response = await axios.get(`${API_BASE_URL}/preview/${sessionId}`);
  return response.data;
};