import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function Navbar() {
  const [userName, setUserName] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const navigate = useNavigate();

  const checkAuth = () => {
    const token = localStorage.getItem('token');
    const name = localStorage.getItem('user_name');
    if (token && name) {
      setUserName(name);
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUserRole(payload.role || 'patient');
      } catch (e) {
        setUserRole('patient');
      }
    } else {
      setUserName(null);
      setUserRole(null);
    }
  };

  useEffect(() => {
    checkAuth();
    // Storage eventi - Diğer sekmelerde çıkış yapıldığında bu sekmeyi de güvenli tutar
    window.addEventListener('storage', checkAuth);
    // Custom event - Aynı sekmedeki Login sayfasından atılan login trigger'ını yakalar
    window.addEventListener('login-success', checkAuth);
    
    return () => {
      window.removeEventListener('storage', checkAuth);
      window.removeEventListener('login-success', checkAuth);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_name');
    checkAuth();
    navigate('/login');
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 max-w-7xl flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#1A56DB] rounded-xl flex items-center justify-center text-white font-extrabold text-xl shadow-md">
            +
          </div>
          <span className="text-2xl font-bold tracking-tight text-gray-900">E-MHRS</span>
        </Link>
        
        <nav className="hidden md:flex gap-8 font-semibold text-gray-600">
          <Link to="/" className="text-[#1A56DB] hover:text-blue-800 transition-colors">Ana Sayfa</Link>
          
          {(!userRole || userRole === 'patient') && (
            <>
              <Link to="/new-appointment" className="hover:text-[#1A56DB] transition-colors">Yeni Randevu Al</Link>
              <Link to="/appointments" className="hover:text-[#1A56DB] transition-colors">Randevularım</Link>
              <Link to="/doctors" className="hover:text-[#1A56DB] transition-colors">Hekimlerimiz</Link>
            </>
          )}

          {userRole === 'doctor' && (
            <>
              <Link to="/doctor-dashboard" className="hover:text-[#1A56DB] transition-colors">Doktor Paneli</Link>
              <Link to="/patients" className="hover:text-[#000000] opacity-50 cursor-not-allowed transition-colors" title="Yakında eklenecek">Hastalarım</Link>
            </>
          )}

          {userRole === 'admin' && (
            <>
              <Link to="/admin-dashboard" className="hover:text-[#1A56DB] transition-colors">Yönetici Paneli</Link>
              <Link to="/settings" className="hover:text-[#000000] opacity-50 cursor-not-allowed transition-colors" title="Yakında eklenecek">Sistem Ayarları</Link>
            </>
          )}
        </nav>

        <div className="flex items-center gap-4">
          {userName ? (
             <div className="flex items-center gap-5 animate-fade-in">
               <span className="text-gray-700 font-medium hidden sm:block">
                 Hoş geldin, <span className="font-bold text-[#1A56DB]">{userName}</span>
               </span>
               <Link 
                 to="/profile" 
                 className="text-[#1A56DB] font-semibold hover:text-blue-800 transition-colors flex items-center gap-1"
               >
                 <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                 Profilim
               </Link>
               <button 
                 onClick={handleLogout}
                 className="bg-red-50 hover:bg-red-100 text-red-600 px-4 py-2.5 rounded-lg font-bold shadow-sm transition-all text-sm border border-red-100 flex items-center gap-2"
               >
                 Çıkış Yap
               </button>
             </div>
          ) : (
             <>
               <Link to="/register" className="hidden sm:inline-block font-semibold text-gray-600 hover:text-gray-900 transition-colors">
                 Kayıt Ol
               </Link>
               <Link to="/login" className="bg-[#1A56DB] hover:bg-blue-800 text-white px-5 py-2.5 rounded-lg font-bold shadow-sm transition-all text-sm relative overflow-hidden group block">
                 <span className="relative z-10">Giriş Yap</span>
                 <div className="absolute inset-0 h-full w-full bg-blue-900 scale-x-0 group-hover:scale-x-100 transform origin-left transition-transform duration-300 ease-out z-0"></div>
               </Link>
             </>
          )}
        </div>
      </div>
    </header>
  );
}
