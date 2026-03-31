import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function Verify() {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const location = useLocation();
  const navigate = useNavigate();
  
  // Register.jsx'den state ile gelen e-postayı alıyoruz
  const email = location.state?.email || "";

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!email) {
      setError("Doğrulanacak e-posta adresi bulunamadı. Lütfen kayıt ekranına dönün.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // Backend /verify bekliyor. Şema VerifyEmailRequest (email, code)
      await api.post('/auth/verify', { email, code });
      
      // Başarılı olursa login sayfasına at
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || "Geçersiz veya süresi dolmuş kod.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-20 animate-fade-in px-4">
      <div className="bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-gray-100 max-w-md w-full relative overflow-hidden text-center">
        <div className="absolute top-0 left-0 w-full h-2 bg-yellow-400"></div>
        
        <div className="w-16 h-16 bg-yellow-50 text-yellow-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
        </div>
        
        <h2 className="text-3xl font-extrabold text-gray-800 mb-3">Hesabı Doğrula</h2>
        
        {email ? (
          <p className="text-gray-500 mb-8">
            <strong className="text-gray-900 border-b border-gray-300 pb-0.5">{email}</strong> adresinize gönderilen 6 haneli kodu lütfen aşağıya giriniz.
          </p>
        ) : (
          <div className="mb-6 p-4 bg-orange-50 border-l-4 border-orange-500 text-orange-700 text-sm font-medium rounded-r text-left">
            Güvenlik e-postası bulunamadı. Tarayıcınızı yenilediyseniz lütfen tekrar kayıt olun veya giriş yapmayı deneyin.
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm font-medium rounded-r text-left">
             {error}
          </div>
        )}

        <form onSubmit={handleVerify} className="flex flex-col space-y-6">
          <div>
            <input 
              type="text" 
              maxLength="6"
              required
              placeholder="000000"
              className="w-full text-center text-3xl tracking-[0.5em] p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] outline-none transition-all font-bold text-gray-700 font-mono"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, ''))}
              disabled={!email}
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading || !email || code.length !== 6}
            className="w-full bg-[#1A56DB] hover:bg-blue-800 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl shadow-md transition-all flex justify-center items-center"
          >
            {loading ? 'Doğrulanıyor...' : 'Doğrula & Aktifleştir'}
          </button>
        </form>

        <div className="mt-8 text-sm">
          <Link to="/register" className="text-gray-400 hover:text-gray-600 hover:underline transition-colors">
            Farklı bir e-posta ile kayıt ol
          </Link>
        </div>
      </div>
    </div>
  );
}
