import React, { useState } from 'react';
import Login from './pages/Login';
import Register from './pages/Register';
import Calendar from './pages/Calendar';

export default function App() {
  // По умолчанию теперь открывается страница входа (login)
  const [screen, setScreen] = useState('login');

  return (
    <>
      {screen === 'login' && <Login onNavigate={setScreen} />}
      {screen === 'register' && <Register onNavigate={setScreen} />}
      {screen === 'calendar' && <Calendar />}
    </>
  );
}