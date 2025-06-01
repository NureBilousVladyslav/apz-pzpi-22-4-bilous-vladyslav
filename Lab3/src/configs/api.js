import axios from 'axios';

const api = axios.create({
  baseURL: 'https://tire-presure-backend-dpg3ejcpgpbnfmeh.northeurope-01.azurewebsites.net',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;