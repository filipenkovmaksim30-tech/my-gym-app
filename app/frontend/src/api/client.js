import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Автоматически пересылает куки авторизации на бэк
});

export const workoutPlanApi = {
  // Получить все тренировки пользователя
  getAll: async () => {
    const response = await apiClient.get('/workoutplan');
    return response.data;
  },

  // Создать тренировку
  create: async (date, title) => {
    const response = await apiClient.post('/workoutplan', { date, title });
    return response.data;
  },

  // Обновить тренировку
  update: async (id, data) => {
    const response = await apiClient.patch(`/workoutplan/${id}`, data);
    return response.data;
  },

  // Удалить тренировку
  delete: async (id) => {
    const response = await apiClient.delete(`/workoutplan/${id}`);
    return response.data;
  }
};