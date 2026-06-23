import axios from 'axios';

const API_URL = '/api';

const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Автоматически пересылает куки авторизации на бэк
});

export const workoutPlanApi = {
  getAll: async () => {
    const response = await apiClient.get('/workoutplan');
    return response.data;
  },
  create: async (date, title) => {
    const response = await apiClient.post('/workoutplan', { date, title });
    return response.data;
  },
  update: async (id, data) => {
    const response = await apiClient.patch(`/workoutplan/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await apiClient.delete(`/workoutplan/${id}`);
    return response.data;
  }
};

// --- API ДЛЯ РАБОТЫ С УПРАЖНЕНИЯМИ ---
export const exerciseApi = {
  getByWorkout: async (workoutId) => {
    const response = await apiClient.get(`/planned_exercises/workout/${workoutId}`);
    return response.data;
  },
  create: async (workoutPlanId, name) => {
    const response = await apiClient.post('/planned_exercises', { 
      workout_plan_id: workoutPlanId, 
      exercise_name: name 
    });
    return response.data;
  },
  delete: async (id) => {
    const response = await apiClient.delete(`/planned_exercises/${id}`);
    return response.data;
  }
};

// --- API ДЛЯ ЗАПЛАНИРОВАННЫХ ПОДХОДОВ ---
export const plannedSetsApi = {
  create: async (exerciseId, setNumber, targetWeight = 0, targetReps = 1) => {
    const response = await apiClient.post('/planned_sets', {
      planned_exercise_id: exerciseId,
      set_number: setNumber,
      target_weight: targetWeight,
      target_reps: targetReps
    });
    return response.data;
  },
  update: async (id, data) => {
    const response = await apiClient.put(`/planned_sets/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await apiClient.delete(`/planned_sets/${id}`);
    return response.data;
  }
};

// --- API ДЛЯ ФАКТИЧЕСКИХ ПОДХОДОВ ---
export const actualSetsApi = {
  create: async (exerciseId, setNumber, weight = 0, reps = 1) => {
    const response = await apiClient.post('/actual_sets', {
      planned_exercise_id: exerciseId,
      set_number: setNumber,
      weight: weight,
      reps_done: reps
    });
    return response.data;
  },
  update: async (id, data) => {
    const response = await apiClient.put(`/actual_sets/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await apiClient.delete(`/actual_sets/${id}`);
    return response.data;
  }
};