import React, { useState } from 'react';
import { User, Lock, Dumbbell, AlertCircle, Eye, EyeOff } from 'lucide-react';

export default function Login({ onNavigate }) {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false); // Состояние для показа пароля

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      alert('Вход успешен!');
      onNavigate('calendar'); 
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-xl">
        
        {/* Логотип */}
        <div className="flex flex-col items-center mb-8">
          <div className="bg-amber-500 text-zinc-950 p-3 rounded-xl mb-3 shadow-lg shadow-amber-500/20">
            <Dumbbell size={32} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Вход в систему</h1>
          <p className="text-zinc-400 text-sm mt-1">Твой личный спортивный календарь</p>
        </div>

        {/* Ошибка */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-xl flex items-center gap-2 mb-6 text-sm">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Форма */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Имя пользователя</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
              <input
                type="text"
                name="username"
                required
                value={formData.username}
                onChange={handleChange}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-10 pr-4 py-3 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-amber-500 transition-colors text-sm"
                placeholder="Ivan_Gym"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">Пароль</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
              <input
                type={showPassword ? 'text' : 'password'} // Меняем тип динамически
                name="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-10 pr-12 py-3 text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-amber-500 transition-colors text-sm"
                placeholder="••••••••"
              />
              {/* Кнопка-глазик */}
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 transition-colors focus:outline-none"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-amber-500 hover:bg-amber-600 text-zinc-950 font-semibold py-3 px-4 rounded-xl transition-colors shadow-lg shadow-amber-500/10 focus:outline-none text-sm mt-2"
          >
            Войти
          </button>
        </form>

        <p className="text-center text-zinc-500 text-xs mt-6">
          Ещё нет аккаунта?{' '}
          <button type="button" onClick={() => onNavigate('register')} className="text-amber-500 hover:underline bg-transparent border-none cursor-pointer">
            Создать аккаунт
          </button>
        </p>
      </div>
    </div>
  );
}