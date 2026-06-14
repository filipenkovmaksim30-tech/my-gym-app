import React, { useState, useEffect } from 'react';
import { Dumbbell, Plus, Calendar as CalendarIcon, ChevronLeft, ChevronRight, Trash2, X } from 'lucide-react';
import { workoutPlanApi } from '../api/client';

export default function Calendar({ onNavigate }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [workouts, setWorkouts] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // Управление боковой панелью (Drawer) вместо старых модалок
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState('');
  const [workoutTitle, setWorkoutTitle] = useState('');
  const [editingWorkout, setEditingWorkout] = useState(null);

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

  useEffect(() => {
    fetchWorkouts();
  }, []);

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
        await workoutPlanApi.update(editingWorkout.id, { title: workoutTitle, date: selectedDate });
      } else {
        await workoutPlanApi.create(selectedDate, workoutTitle);
      }
      setIsSidebarOpen(false);
      fetchWorkouts();
    } catch (err) {
      console.error(err);
      setError('Не удалось сохранить план');
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
              <span className="text-[10px] text-zinc-500 font-medium">
                Тр: {dayWorkouts.length}
              </span>
            )}
          </div>

          {/* Список планов на этот день */}
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
        
        {/* Шапка */}
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

        {/* Сетка */}
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

      {/* ВЫДВИЖНАЯ БОКОВАЯ ПАНЕЛЬ (DRAWER) */}
      <div className={`fixed top-0 right-0 h-full w-full max-w-md bg-zinc-900 border-l border-zinc-800 p-6 shadow-2xl transform transition-transform duration-300 ease-in-out z-50 ${
        isSidebarOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        <div className="flex justify-between items-center mb-6 border-b border-zinc-800 pb-4">
          <h2 className="text-lg font-bold flex items-center gap-2 text-zinc-100">
            <CalendarIcon size={20} className="text-amber-500" />
            {editingWorkout ? 'Редактировать план' : 'Новая тренировка'}
          </h2>
          <button 
            onClick={() => setIsSidebarOpen(false)}
            className="p-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-100 rounded-lg transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-5 flex flex-col h-[calc(100%-80px)] justify-between">
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-zinc-400 font-bold mb-2 uppercase tracking-wider">Дата проведения</label>
              <input 
                type="date" 
                value={selectedDate} 
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-zinc-100 text-sm focus:outline-none focus:border-amber-500 transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-xs text-zinc-400 font-bold mb-2 uppercase tracking-wider">Название или Фокус дня</label>
              <input 
                type="text" 
                value={workoutTitle} 
                onChange={(e) => setWorkoutTitle(e.target.value)}
                placeholder="Например: Грудь + Спина (Силовая)" 
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-zinc-100 text-sm focus:outline-none focus:border-amber-500 transition-colors placeholder-zinc-600"
                required
                autoFocus
              />
            </div>

            {/* ТУТ В БУДУЩЕМ БУДЕТ НАШ КОНСТРУКТОР УПРАЖНЕНИЙ */}
            <div className="p-4 bg-zinc-950/40 border border-zinc-800/60 rounded-xl border-dashed flex flex-col items-center justify-center text-center py-8 text-zinc-500">
              <Plus size={24} className="mb-2 text-zinc-600" />
              <p className="text-xs">Конструктор подходов будет доступен после обновления БД бэкенда</p>
            </div>
          </div>

          <div className="flex gap-2 pt-4 border-t border-zinc-800">
            <button 
              type="submit" 
              className="flex-1 bg-amber-500 hover:bg-amber-600 text-zinc-950 font-bold py-3 px-4 rounded-xl text-sm transition-colors shadow-lg shadow-amber-500/10"
            >
              {editingWorkout ? 'Сохранить' : 'Создать план'}
            </button>
            
            {editingWorkout && (
              <button 
                type="button" 
                onClick={handleDelete}
                className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 px-3 py-3 rounded-xl transition-colors"
                title="Удалить"
              >
                <Trash2 size={18} />
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}