import React, { useState, useEffect, useCallback } from 'react';
import { Dumbbell, Plus, Calendar as CalendarIcon, ChevronLeft, ChevronRight, Trash2, X } from 'lucide-react';
import { workoutPlanApi, exerciseApi, plannedSetsApi, actualSetsApi } from '../api/client';

// Функция дебаунса для предотвращения спама PUT-запросов
const debounce = (func, delay) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => func(...args), delay);
  };
};

export default function Calendar({ onNavigate }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [workouts, setWorkouts] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // Управление боковой панелью (Drawer)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState('');
  const [workoutTitle, setWorkoutTitle] = useState('');
  const [editingWorkout, setEditingWorkout] = useState(null);

  // Стейты для конструктора упражнений
  const [exercises, setExercises] = useState([]);
  const [newExerciseName, setNewExerciseName] = useState('');

  const fetchWorkouts = async () => {
    try {
      setLoading(true);
      const data = await workoutPlanApi.getAll();
      setWorkouts(data);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.status === 401) {
        setError('Сессия истекла. Войдите заново.');
        setTimeout(() => onNavigate('login'), 2000);
      } else {
        setError('Не удалось загрузить тренировки');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchExercises = async (workoutId) => {
    try {
      const data = await exerciseApi.getByWorkout(workoutId);
      setExercises(data);
    } catch (err) {
      console.error('Ошибка загрузки упражнений:', err);
    }
  };

  useEffect(() => {
    fetchWorkouts();
  }, []);

  useEffect(() => {
    if (editingWorkout) {
      fetchExercises(editingWorkout.id);
    } else {
      setExercises([]);
    }
    setNewExerciseName('');
  }, [editingWorkout]);

  // --- ДЕБАУНС ФУНКЦИИ ДЛЯ ОБНОВЛЕНИЯ ПОДХОДОВ НА БЭКЕНДЕ ---
  const debouncedUpdatePlannedApproach = useCallback(
    debounce(async (approachId, updatedFields) => {
      try {
        await plannedSetsApi.update(approachId, updatedFields);
      } catch (err) {
        console.error('Ошибка при дебаунс-обновлении планового подхода:', err);
      }
    }, 1000),
    []
  );

  const debouncedUpdateActualApproach = useCallback(
    debounce(async (approachId, updatedFields) => {
      try {
        await actualSetsApi.update(approachId, updatedFields);
      } catch (err) {
        console.error('Ошибка при дебаунс-обновлении фактического подхода:', err);
      }
    }, 1000),
    []
  );

  // --- ОБЩИЙ ОБРАБОТЧИК ОНЛАЙН-ВВОДА В ИНПУТЫ ---
  const handleInputChange = (exerciseId, setId, type, field, value) => {
    const numValue = value === '' ? '' : parseFloat(value);

    setExercises(prevExercises => prevExercises.map(ex => {
      if (ex.id !== exerciseId) return ex;

      if (type === 'planned') {
        const updatedSets = (ex.planned_sets || []).map(set => {
          if (set.id !== setId) return set;
          const updatedSet = { ...set, [field]: numValue };
          
          // Рассчитываем финальные валидные данные для бэка
          const target_weight = field === 'target_weight' ? (parseFloat(value) || 0) : (set.target_weight || 0);
          let target_reps = field === 'target_reps' ? (parseInt(value) || 1) : (set.target_reps || 1);
          if (target_reps < 1) target_reps = 1; // Защита от reps < 1

          debouncedUpdatePlannedApproach(setId, { target_weight, target_reps });
          return updatedSet;
        });
        return { ...ex, planned_sets: updatedSets };
      } else {
        const updatedSets = (ex.actual_sets || []).map(set => {
          if (set.id !== setId) return set;
          const updatedSet = { ...set, [field]: numValue };

          const weight = field === 'weight' ? (parseFloat(value) || 0) : (set.weight || 0);
          let reps_done = field === 'reps_done' ? (parseInt(value) || 1) : (set.reps_done || 1);
          if (reps_done < 1) reps_done = 1; // Защита от reps < 1

          debouncedUpdateActualApproach(setId, { weight, reps_done });
          return updatedSet;
        });
        return { ...ex, actual_sets: updatedSets };
      }
    }));
  };

  // --- ЛОГИКА УПРАЖНЕНИЙ ---
  const handleAddExercise = async (e) => {
    e.preventDefault();
    if (!newExerciseName.trim() || !editingWorkout) return;
    try {
      const newEx = await exerciseApi.create(editingWorkout.id, newExerciseName.trim());
      setExercises([...exercises, { ...newEx, planned_sets: [], actual_sets: [] }]);
      setNewExerciseName('');
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateExerciseName = async (exerciseId, newName) => {
    if (!newName.trim()) return;
    try {
      await exerciseApi.update(exerciseId, { exercise_name: newName.trim() });
      setExercises(exercises.map(ex => 
        ex.id === exerciseId ? { ...ex, exercise_name: newName.trim() } : ex
      ));
    } catch (err) {
      console.error('Ошибка при обновлении названия упражнения:', err);
    }
  };

  const handleDeleteExercise = async (exerciseId) => {
    try {
      await exerciseApi.delete(exerciseId);
      setExercises(exercises.filter(ex => ex.id !== exerciseId));
    } catch (err) {
      console.error(err);
    }
  };

  // --- УМНОЕ ДОБАВЛЕНИЕ ПЛАНОВОГО ПОДХОДА (КОПИРОВАНИЕ ПРЕДЫДУЩЕГО) ---
  const handleAddPlannedApproach = async (exerciseId) => {
    const currentEx = exercises.find(ex => ex.id === exerciseId);
    if (!currentEx) return;
    
    const plannedSets = currentEx.planned_sets || [];
    const nextSetNumber = plannedSets.length + 1;

    // Копируем параметры последнего существующего подхода или берем дефолты
    const lastSet = plannedSets[plannedSets.length - 1];
    const defaultWeight = lastSet ? lastSet.target_weight : 0;
    let defaultReps = lastSet ? lastSet.target_reps : 1;
    if (defaultReps < 1) defaultReps = 1;

    try {
      const newApproach = await plannedSetsApi.create(exerciseId, nextSetNumber, defaultWeight, defaultReps);
      
      setExercises(exercises.map(ex => 
        ex.id === exerciseId ? { ...ex, planned_sets: [...plannedSets, newApproach] } : ex
      ));
    } catch (err) {
      console.error('Ошибка добавления запланированного подхода:', err);
    }
  };

  const handleDeletePlannedApproach = async (exerciseId, approachId) => {
    try {
      await plannedSetsApi.delete(approachId);
      setExercises(exercises.map(ex => 
        ex.id === exerciseId 
          ? { ...ex, planned_sets: (ex.planned_sets || []).filter(a => a.id !== approachId) }
          : ex
      ));
    } catch (err) {
      console.error(err);
    }
  };

  // --- УМНОЕ ДОБАВЛЕНИЕ ФАКТИЧЕСКОГО ПОДХОДА (ИЗ ПЛАНА ИЛИ ПРЕДЫДУЩЕГО ФАКТА) ---
  const handleAddActualApproach = async (exerciseId) => {
    const currentEx = exercises.find(ex => ex.id === exerciseId);
    if (!currentEx) return;

    const actualSets = currentEx.actual_sets || [];
    const plannedSets = currentEx.planned_sets || [];
    const nextSetNumber = actualSets.length + 1;
    
    // Ищем шаблон в плановом подходе на этот же номер, либо берем прошлый факт
    const lastActual = actualSets[actualSets.length - 1];
    const template = plannedSets[nextSetNumber - 1] || lastActual || {};
    
    const weight = template.target_weight !== undefined ? template.target_weight : (template.weight || 0);
    let reps = template.target_reps !== undefined ? template.target_reps : (template.reps_done || 1);
    if (reps < 1) reps = 1;
    
    try {
      const newApproach = await actualSetsApi.create(exerciseId, nextSetNumber, weight, reps);

      setExercises(exercises.map(ex => 
        ex.id === exerciseId ? { ...ex, actual_sets: [...actualSets, newApproach] } : ex
      ));
    } catch (err) {
      console.error('Ошибка добавления фактического подхода:', err);
    }
  };

  const handleDeleteActualApproach = async (exerciseId, approachId) => {
    try {
      await actualSetsApi.delete(approachId);
      setExercises(exercises.map(ex => 
        ex.id === exerciseId 
          ? { ...ex, actual_sets: (ex.actual_sets || []).filter(a => a.id !== approachId) }
          : ex
      ));
    } catch (err) {
      console.error(err);
    }
  };

  // --- КАЛЕНДАРНАЯ МАТЕМАТИКА ---
  const getDaysInMonth = (date) => new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  const getFirstDayOfMonth = (date) => {
    const day = new Date(date.getFullYear(), date.getMonth(), 1).getDay();
    return day === 0 ? 6 : day - 1;
  };

  const isSameDay = (date1, date2) => {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  };

  const formatDateString = (year, month, day) => {
    const m = String(month + 1).padStart(2, '0');
    const d = String(day).padStart(2, '0');
    return `${year}-${m}-${d}`;
  };

  const prevMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));

  const handleDayClick = (dayString) => {
    setEditingWorkout(null);
    setSelectedDate(dayString);
    setWorkoutTitle('');
    setIsSidebarOpen(true);
  };

  const handleEditWorkout = (workout) => {
    setEditingWorkout(workout);
    const dateObj = new Date(workout.date);
    setSelectedDate(formatDateString(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate()));
    setWorkoutTitle(workout.title);
    setIsSidebarOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!workoutTitle.trim()) return;

    try {
      if (editingWorkout) {
        await workoutPlanApi.update(editingWorkout.id, { title: workoutTitle.trim() });
        setIsSidebarOpen(false);
      } else {
        const created = await workoutPlanApi.create(selectedDate, workoutTitle.trim());
        setEditingWorkout(created);
      }
      fetchWorkouts();
    } catch (err) {
      console.error(err);
      setError('Не удалось сохранить план тренировки');
    }
  };

  const handleDelete = async () => {
    if (!editingWorkout) return;
    try {
      await workoutPlanApi.delete(editingWorkout.id);
      setIsSidebarOpen(false);
      fetchWorkouts();
    } catch (err) {
      console.error(err);
      setError('Не удалось удалить тренировку');
    }
  };

  const renderDays = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDayIndex = getFirstDayOfMonth(currentDate);
    const dayCells = [];

    for (let i = 0; i < firstDayIndex; i++) {
      dayCells.push(<div key={`empty-${i}`} className="bg-zinc-950/10 border border-zinc-900/30 p-2 min-h-[100px] md:min-h-[130px]"></div>);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const targetDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const dayString = formatDateString(currentDate.getFullYear(), currentDate.getMonth(), day);
      const dayWorkouts = workouts.filter(w => isSameDay(new Date(w.date), targetDate));
      const isToday = isSameDay(new Date(), targetDate);

      dayCells.push(
        <div
          key={`day-${day}`}
          onClick={() => handleDayClick(dayString)}
          className={`border border-zinc-800/80 p-2 min-h-[100px] md:min-h-[130px] flex flex-col justify-between transition-all hover:bg-zinc-900/60 cursor-pointer ${
            isToday ? 'bg-amber-500/5 border-amber-500/40 shadow-inner shadow-amber-500/5' : 'bg-zinc-900/30'
          }`}
        >
          <div className="flex justify-between items-center mb-1">
            <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${isToday ? 'bg-amber-500 text-zinc-950' : 'text-zinc-400'}`}>
              {day}
            </span>
            {dayWorkouts.length > 0 && (
              <span className="text-[10px] text-zinc-500 font-medium">Тр: {dayWorkouts.length}</span>
            )}
          </div>

          <div className="space-y-1 flex-1 overflow-y-auto max-h-[65px] md:max-h-[90px] custom-scrollbar pt-1">
            {dayWorkouts.map((workout) => (
              <div
                key={workout.id}
                onClick={(e) => {
                  e.stopPropagation();
                  handleEditWorkout(workout);
                }}
                className="text-[10px] md:text-xs bg-zinc-900 border border-zinc-800 text-amber-400 px-2 py-1 rounded-lg truncate hover:border-amber-500/50 hover:bg-zinc-800/50 transition-all font-medium"
                title={workout.title}
              >
                ⚡ {workout.title}
              </div>
            ))}
          </div>
        </div>
      );
    }

    return dayCells;
  };

  const monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
  const weekDays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 p-4 md:p-8 relative overflow-x-hidden">
      <div className={`max-w-6xl mx-auto transition-all duration-300 ${isSidebarOpen ? 'pr-0 md:pr-[20px] opacity-60 pointer-events-none md:pointer-events-auto md:opacity-100' : ''}`}>
        
        {/* Шапка календаря */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-8 bg-zinc-900 border border-zinc-800 rounded-2xl p-4 md:p-6 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="bg-amber-500 text-zinc-950 p-2.5 rounded-xl shadow-lg shadow-amber-500/10">
              <Dumbbell size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">1.5 качка</h1>
              <p className="text-zinc-400 text-xs mt-0.5">Календарь тренировок</p>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-zinc-950 border border-zinc-800 rounded-xl p-1">
            <button onClick={prevMonth} className="p-2 hover:text-amber-500 transition-colors rounded-lg"><ChevronLeft size={18} /></button>
            <span className="text-sm font-semibold px-3 min-w-[130px] text-center text-zinc-200">
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </span>
            <button onClick={nextMonth} className="p-2 hover:text-amber-500 transition-colors rounded-lg"><ChevronRight size={18} /></button>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-xl mb-6 text-sm">
            {error}
          </div>
        )}

        {/* Сетка дней */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 shadow-xl">
          <div className="grid grid-cols-7 gap-1 text-center mb-2">
            {weekDays.map(day => (
              <div key={day} className="text-zinc-500 text-xs font-bold py-1 uppercase tracking-wider">{day}</div>
            ))}
          </div>

          {loading ? (
            <div className="text-center py-20 text-zinc-500 text-sm">Загрузка календаря...</div>
          ) : (
            <div className="grid grid-cols-7 gap-1 bg-zinc-950 p-1 rounded-xl border border-zinc-800/50">
              {renderDays()}
            </div>
          )}
        </div>
      </div>

      {/* ВЫДВИЖНАЯ ПАНЕЛЬ */}
      <div className={`fixed top-0 right-0 h-full w-full sm:max-w-lg md:max-w-xl lg:max-w-2xl bg-zinc-900 border-l border-zinc-800 p-4 md:p-6 shadow-2xl transform transition-transform duration-300 ease-in-out z-50 overflow-y-auto ${
        isSidebarOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        <div className="flex justify-between items-center mb-6 border-b border-zinc-800 pb-4">
          <h2 className="text-base md:text-lg font-bold flex items-center gap-2 text-zinc-100">
            <CalendarIcon size={20} className="text-amber-500" />
            {editingWorkout ? 'Редактировать plan' : 'Новая тренировка'}
          </h2>
          <button 
            onClick={() => setIsSidebarOpen(false)}
            className="p-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-100 rounded-lg transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Форма заголовка тренировки */}
        <form onSubmit={handleSave} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] text-zinc-400 font-bold mb-1.5 uppercase tracking-wider">Дата проведения</label>
              <input 
                type="date" 
                value={selectedDate} 
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2.5 text-zinc-100 text-xs focus:outline-none focus:border-amber-500 transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-[10px] text-zinc-400 font-bold mb-1.5 uppercase tracking-wider">Фокус дня</label>
              <input 
                type="text" 
                value={workoutTitle} 
                onChange={(e) => setWorkoutTitle(e.target.value)}
                placeholder="Например: Силовая Грудь" 
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2.5 text-zinc-100 text-xs focus:outline-none focus:border-amber-500 transition-colors placeholder-zinc-600"
                maxLength={30}
                required
              />
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button 
              type="submit" 
              className="flex-1 bg-amber-500 hover:bg-amber-600 text-zinc-950 font-bold py-2.5 px-4 rounded-xl text-xs transition-colors shadow-lg shadow-amber-500/10"
            >
              {editingWorkout ? 'Обновить название' : 'Создать тренировку'}
            </button>
            
            {editingWorkout && (
              <button 
                type="button" 
                onClick={handleDelete}
                className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 px-3 py-2.5 rounded-xl transition-colors"
                title="Удалить"
              >
                <Trash2 size={18} />
              </button>
            )}
          </div>
        </form>

        {/* КОНСТРУКТОР ДЛЯ НАПОЛНЕНИЯ ТРЕНИРОВКИ */}
        {editingWorkout && (
          <div className="mt-8 pt-6 border-t border-zinc-800 space-y-6">
            <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Список упражнений в этой тренировке</h3>
            
            {/* Форма добавления нового упражнения */}
            <form onSubmit={handleAddExercise} className="flex gap-2">
              <input 
                type="text"
                placeholder="Название упражнения (например: Жим лежа)..."
                value={newExerciseName}
                onChange={(e) => setNewExerciseName(e.target.value)}
                className="flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2.5 text-zinc-100 text-xs focus:outline-none focus:border-amber-500 transition-colors placeholder-zinc-600"
                required
              />
              <button 
                type="submit" 
                className="bg-zinc-800 hover:bg-zinc-700 text-amber-400 border border-zinc-700 px-4 py-2 rounded-xl text-xs font-bold transition-all"
              >
                + Добавить
              </button>
            </form>

            {/* Список добавленных упражнений */}
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1 custom-scrollbar">
              {exercises.length === 0 ? (
                <p className="text-xs text-zinc-500 italic text-center py-6">В плане пока пусто. Добавьте упражнение выше.</p>
              ) : (
                exercises.map((exercise) => (
                  <div key={exercise.id} className="bg-zinc-950 p-4 rounded-xl border border-zinc-850/60 space-y-3">
                    
                    {/* ШАПКА УПРАЖНЕНИЯ: С ИНЛАЙН-РЕДАКТИРОВАНИЕМ НАЗВАНИЯ */}
                    <div className="flex justify-between items-center border-b border-zinc-900/80 pb-2 gap-2">
                      <div className="flex items-center gap-1.5 flex-1 min-w-0">
                        <span className="text-xs">🏋️‍♂️</span>
                        <input 
                          type="text"
                          defaultValue={exercise.exercise_name}
                          onBlur={(e) => handleUpdateExerciseName(exercise.id, e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              e.target.blur();
                            }
                          }}
                          className="bg-transparent border-b border-transparent hover:border-zinc-800 focus:border-amber-500 focus:bg-zinc-900/60 text-xs font-bold text-amber-400 px-1 py-0.5 rounded transition-all outline-none flex-1 min-w-0 truncate"
                          title="Кликните, чтобы изменить название упражнения"
                        />
                      </div>
                      <button 
                        onClick={() => handleDeleteExercise(exercise.id)}
                        className="text-zinc-600 hover:text-red-400 transition-colors p-1 shrink-0"
                      >
                        <X size={14} />
                      </button>
                    </div>

                    {/* СЕТКА ПОДХОДОВ */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                      
                      {/* КОЛОНКА: ПЛАН */}
                      <div className="space-y-2">
                        <span className="text-[10px] text-orange-400/80 font-bold uppercase tracking-wider block border-b border-zinc-900 pb-1">📋 План</span>
                        <div className="space-y-2">
                          {(exercise.planned_sets || []).map((approach) => (
                            <div key={`p-${approach.id}`} className="flex items-center gap-1.5 text-xs">
                              <span className="text-zinc-600 font-medium w-4">{approach.set_number}.</span>
                              <input 
                                type="number" 
                                value={approach.target_weight ?? ''}
                                onChange={(e) => handleInputChange(exercise.id, approach.id, 'planned', 'target_weight', e.target.value)}
                                className="w-12 bg-zinc-900 border border-zinc-800 rounded px-1.5 py-0.5 text-center text-zinc-200 focus:border-amber-500/70 outline-none"
                              />
                              <span className="text-zinc-600">кг</span>
                              <input 
                                type="number" 
                                value={approach.target_reps ?? ''}
                                onChange={(e) => handleInputChange(exercise.id, approach.id, 'planned', 'target_reps', e.target.value)}
                                className="w-10 bg-zinc-900 border border-zinc-800 rounded px-1.5 py-0.5 text-center text-zinc-200 focus:border-amber-500/70 outline-none"
                              />
                              <span className="text-zinc-600">повт</span>
                              <button 
                                type="button" 
                                onClick={() => handleDeletePlannedApproach(exercise.id, approach.id)}
                                className="text-zinc-700 hover:text-red-400 ml-auto p-0.5"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                        <button 
                          type="button" 
                          onClick={() => handleAddPlannedApproach(exercise.id)}
                          className="w-full mt-2 py-1.5 bg-zinc-900 hover:bg-zinc-800 text-[10px] font-bold text-zinc-400 hover:text-zinc-200 rounded-lg border border-zinc-800 transition-all uppercase tracking-wider"
                        >
                          + Добавить подход
                        </button>
                      </div>

                      {/* КОЛОНКА: ВЫПОЛНЕНИЕ (ФАКТ) */}
                      <div className="space-y-2">
                        <span className="text-[10px] text-emerald-400/80 font-bold uppercase tracking-wider block border-b border-zinc-900 pb-1">✅ Выполнение</span>
                        <div className="space-y-2">
                          {(exercise.actual_sets || []).map((approach) => (
                            <div key={`a-${approach.id}`} className="flex items-center gap-1.5 text-xs">
                              <span className="text-zinc-600 font-medium w-4">{approach.set_number}.</span>
                              <input 
                                type="number" 
                                value={approach.weight ?? ''}
                                onChange={(e) => handleInputChange(exercise.id, approach.id, 'actual', 'weight', e.target.value)}
                                className="w-12 bg-zinc-900 border border-zinc-800 rounded px-1.5 py-0.5 text-center text-zinc-200 focus:border-emerald-500/70 outline-none"
                              />
                              <span className="text-zinc-600">кг</span>
                              <input 
                                type="number" 
                                value={approach.reps_done ?? ''}
                                onChange={(e) => handleInputChange(exercise.id, approach.id, 'actual', 'reps_done', e.target.value)}
                                className="w-10 bg-zinc-900 border border-zinc-800 rounded px-1.5 py-0.5 text-center text-zinc-200 focus:border-emerald-500/70 outline-none"
                              />
                              <span className="text-zinc-600">повт</span>
                              <button 
                                type="button" 
                                onClick={() => handleDeleteActualApproach(exercise.id, approach.id)}
                                className="text-zinc-700 hover:text-red-400 ml-auto p-0.5"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                        <button 
                          type="button" 
                          onClick={() => handleAddActualApproach(exercise.id)}
                          className="w-full mt-2 py-1.5 bg-zinc-900 hover:bg-zinc-800 text-[10px] font-bold text-zinc-400 hover:text-emerald-400 rounded-lg border border-zinc-800 transition-all uppercase tracking-wider"
                        >
                          💪 Засчитать подход
                        </button>
                      </div>

                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}