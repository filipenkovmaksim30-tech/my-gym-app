import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Plus, ClipboardCopy } from 'lucide-react';

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  
  // Временные данные для демонстрации работы календаря
  const [workouts, setWorkouts] = useState({
    '2026-06-15': { title: 'День груди и брусьев', exercises: [] }
  });

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ];
  const daysOfWeek = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  const firstDayOfMonth = new Date(year, month, 1).getDay();
  const blanks = firstDayOfMonth === 0 ? 6 : firstDayOfMonth - 1;
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

  const handleDayClick = (day) => {
    setSelectedDate(new Date(year, month, day));
  };

  const formatDateKey = (dateObj) => {
    const offset = dateObj.getTimezoneOffset();
    const adjustedDate = new Date(dateObj.getTime() - (offset * 60 * 1000));
    return adjustedDate.toISOString().split('T')[0];
  };

  const selectedKey = formatDateKey(selectedDate);
  const activeWorkout = workouts[selectedKey];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 p-4 md:p-8 flex flex-col items-center">
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* СЕТКА КАЛЕНДАРЯ */}
        <div className="md:col-span-2 bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-xl h-fit">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-2">
              <CalendarIcon className="text-amber-500" size={20} />
              <h2 className="text-lg font-bold tracking-tight">
                {monthNames[month]} {year}
              </h2>
            </div>
            <div className="flex gap-2">
              <button onClick={prevMonth} className="p-2 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 rounded-xl transition-colors">
                <ChevronLeft size={18} />
              </button>
              <button onClick={nextMonth} className="p-2 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 rounded-xl transition-colors">
                <ChevronRight size={18} />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-1 text-center mb-2">
            {daysOfWeek.map((day) => (
              <div key={day} className="text-zinc-500 text-xs font-semibold py-1">
                {day}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-1">
            {Array(blanks).fill(null).map((_, i) => (
              <div key={`blank-${i}`} className="aspect-square" />
            ))}
            
            {Array(daysInMonth).fill(null).map((_, i) => {
              const day = i + 1;
              const thisDate = new Date(year, month, day);
              const dateStr = formatDateKey(thisDate);
              const isSelected = formatDateKey(selectedDate) === dateStr;
              const isToday = formatDateKey(new Date()) === dateStr;
              const hasWorkout = !!workouts[dateStr];

              return (
                <button
                  key={`day-${day}`}
                  onClick={() => handleDayClick(day)}
                  className={`aspect-square rounded-xl flex flex-col justify-between p-2 text-sm font-medium border transition-all relative
                    ${isSelected 
                      ? 'bg-amber-500 text-zinc-950 border-amber-500 shadow-lg shadow-amber-500/10' 
                      : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-200'
                    }
                    ${isToday && !isSelected ? 'ring-2 ring-amber-500/30 border-amber-500/50' : ''}
                  `}
                >
                  <span>{day}</span>
                  {hasWorkout && (
                    <span className={`w-1.5 h-1.5 rounded-full absolute bottom-2 right-2 ${isSelected ? 'bg-zinc-950' : 'bg-amber-500'}`} />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* ПАНЕЛЬ ВЫБРАННОГО ДНЯ */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between min-h-[350px]">
          <div>
            <div className="text-zinc-400 text-xs font-semibold uppercase tracking-wider mb-1">Выбранная дата</div>
            <div className="text-base font-bold mb-4 text-zinc-100">
              {selectedDate.toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })}
            </div>

            <hr className="border-zinc-800 my-4" />

            {activeWorkout ? (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-amber-500 text-lg">{activeWorkout.title}</h3>
                  <button 
                    title="Копировать тренировку"
                    className="p-1.5 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-100 rounded-lg transition-colors"
                  >
                    <ClipboardCopy size={16} />
                  </button>
                </div>
                <p className="text-zinc-400 text-sm">Упражнений в этот день пока нет. Давай добавим первое упражнение и подходы!</p>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-zinc-500 text-sm mb-4">На этот день тренировка не запланирована</p>
                <button className="inline-flex items-center gap-2 bg-zinc-950 hover:bg-zinc-800 border border-zinc-800 text-zinc-200 text-sm font-semibold py-2 px-4 rounded-xl transition-colors">
                  <Plus size={16} />
                  <span>Создать план</span>
                </button>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}