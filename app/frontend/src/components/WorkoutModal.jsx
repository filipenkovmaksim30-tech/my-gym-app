import React, { useState, useEffect } from 'react';

const WorkoutModal = ({ workout, date, onClose, onSave, onDelete }) => {
  const [title, setTitle] = useState('');

  useEffect(() => {
    if (workout) {
      setTitle(workout.title);
    } else {
      setTitle('');
    }
  }, [workout]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    onSave(title);
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl w-full max-w-sm shadow-2xl text-zinc-100 animate-in fade-in zoom-in-95 duration-150">
        <h3 className="text-base font-bold tracking-tight text-zinc-200 mb-1">
          {workout ? 'Редактировать тренировку' : 'Запланировать тренировку'}
        </h3>
        <p className="text-xs text-zinc-500 mb-5">Дата: {date}</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 rounded-xl p-3 mb-5 text-sm focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500/50 transition-all placeholder:text-zinc-600"
            placeholder="Например: День груди / Ноги"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={30}
            required
            autoFocus
          />
          
          <div className="flex justify-between items-center gap-3">
            {workout ? (
              <button
                type="button"
                onClick={onDelete}
                className="bg-red-950/40 border border-red-900/50 hover:bg-red-900/60 text-red-400 px-3 py-2 rounded-xl text-xs font-semibold transition-colors"
              >
                Удалить
              </button>
            ) : (
              <div />
            )}

            <div className="flex gap-2">
              <button
                type="button"
                onClick={onClose}
                className="bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200 px-4 py-2 rounded-xl text-xs font-semibold transition-colors"
              >
                Отмена
              </button>
              <button
                type="submit"
                className="bg-amber-500 hover:bg-amber-600 text-zinc-950 px-4 py-2 rounded-xl text-xs font-bold shadow-lg shadow-amber-500/10 transition-colors"
              >
                Сохранить
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default WorkoutModal;