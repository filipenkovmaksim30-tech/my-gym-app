const BASE_URL = 'http://localhost:8000';

export const api = {
  // Регистрация нового пользователя
  register: async (username, password) => {
    const response = await fetch(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Ошибка регистрации');
    return data;
  },

  // Получение тренировок по дате (для календаря)
  getWorkoutByDate: async (dateStr, token) => {
    const response = await fetch(`${BASE_URL}/workout/${dateStr}`, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json' 
      },
    });
    if (response.status === 404) return null; // Если тренировки нет — это норма
    if (!response.ok) throw new Error('Ошибка загрузки данных');
    return await response.json();
  }
};