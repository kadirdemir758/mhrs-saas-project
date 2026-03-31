import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import api from '../api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const portalRole = searchParams.get('role') || searchParams.get('type') || 'patient';

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Backend'deki auth.py LoginRequest Pydantic modelini (JSON formatı) kullanıyor.
      const payload = { email, password };
      
      const res = await api.post('/auth/login', payload);
      const token = res.data.access_token;
      
      // Token'i sakla
      localStorage.setItem('token', token);
      
      // Kullanıcı adını almak için profil uç noktasına istek atalım
      const meRes = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      localStorage.setItem('user_name', meRes.data.name);
      
      // Navbar'a anında bildirim gönder
      window.dispatchEvent(new Event('login-success'));
      
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));

      const payloadDecoded = JSON.parse(jsonPayload);
      const userRole = payloadDecoded.role || 'patient';

      if (userRole !== portalRole) {
        localStorage.removeItem('token');
        localStorage.removeItem('user_name');
        
        let userTitle = 'Hasta';
        if (userRole === 'doctor') userTitle = 'Hekim';
        if (userRole === 'admin') userTitle = 'Yönetici';
        
        let portalTitle = 'Hasta';
        if (portalRole === 'doctor') portalTitle = 'Hekim';
        if (portalRole === 'admin') portalTitle = 'Yönetici';
        
        const errorMsg = `Hata: ${userTitle} hesabı ile ${portalTitle} portalına giriş yapamazsınız. Lütfen ${userTitle} Girişi'ni kullanın.`;
        setError(errorMsg);
        alert(errorMsg); // SweetAlert veya Toast yoksa native alert
        
        setLoading(false);
        return;
      }

      if (userRole === 'admin') navigate('/admin-dashboard');
      else if (userRole === 'doctor') navigate('/doctor-dashboard');
      else navigate('/');
    } catch (err) {
      console.error("Giriş Hatası Detayı:", err);
      // 403 hatası fırlatılırsa (is_verified = False) bunu kullanıcıya anlaşılır şekilde görelim
      setError(err.response?.data?.detail || "Giriş işlemi başarısız. Lütfen bilgilerinizi kontrol ediniz.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-20 animate-fade-in px-4">
      <div className="bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-gray-100 max-w-md w-full relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-2 bg-[#1A56DB]"></div>
        
        <div className="w-16 h-16 bg-blue-50 text-[#1A56DB] rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4"></path></svg>
        </div>
        
        <h2 className="text-3xl font-extrabold text-gray-800 text-center mb-8">
          {portalRole === 'doctor' ? 'Hekim Girişi' : portalRole === 'admin' ? 'Yönetici Girişi' : 'Hasta Girişi'}
        </h2>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm font-medium rounded-r">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="flex flex-col space-y-5">
          <div>
            <label className="block text-gray-700 font-bold mb-2 text-sm" htmlFor="email">E-posta Adresi</label>
            <input 
              id="email"
              type="email" 
              required
              placeholder="E-postanızı giriniz"
              className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] focus:bg-white outline-none transition-all text-gray-700"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-gray-700 font-bold mb-2 text-sm" htmlFor="password">Şifre</label>
            <input 
              id="password"
              type="password" 
              required
              placeholder="Şifrenizi giriniz"
              className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] focus:bg-white outline-none transition-all text-gray-700"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          
          <div className="flex justify-end mt-1">
            <Link to="/forgot-password" className="text-sm text-[#1A56DB] font-semibold hover:underline">
              Şifremi Unuttum
            </Link>
          </div>
          
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-[#1A56DB] hover:bg-blue-800 text-white font-bold py-4 rounded-xl shadow-md hover:shadow-lg transition-transform transform active:scale-95 flex items-center justify-center gap-2 mt-4"
          >
            {loading ? <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span> : null}
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>

        {portalRole === 'patient' && (
          <div className="mt-8 text-center text-sm text-gray-500">
            Hesabınız yok mu?{' '}
            <Link to="/register" className="text-[#1A56DB] font-bold hover:underline">
              Hemen Kayıt Olun
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
