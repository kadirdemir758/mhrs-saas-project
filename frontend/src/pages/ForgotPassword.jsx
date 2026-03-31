import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post('/auth/forgot-password', { email });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="flex flex-col items-center justify-center py-20 animate-fade-in px-4">
        <div className="bg-white p-8 md:p-12 rounded-3xl shadow-xl w-full max-w-md text-center">
          <div className="w-16 h-16 bg-green-50 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-extrabold text-gray-800 mb-4">Mail Gönderildi!</h2>
          <p className="text-gray-600 mb-8">Eğer <b>{email}</b> sitemizde kayıtlıysa, şifrenizi sıfırlamanız için 6 haneli bir kod gönderdik.</p>
          <Link to={`/reset-password?email=${email}`} className="block w-full bg-[#1A56DB] text-white font-bold py-4 rounded-xl">
            Sıfırlama Ekranına Git
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-20 animate-fade-in px-4">
      <div className="bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-gray-100 max-w-md w-full relative">
        <h2 className="text-2xl font-extrabold text-gray-800 text-center mb-4">Şifremi Unuttum</h2>
        <p className="text-gray-500 text-center text-sm mb-8">Endişelenmeyin! E-posta adresinizi girin, size hemen bir sıfırlama kodu gönderelim.</p>
        
        {error && <div className="mb-6 p-4 bg-red-50 text-red-700 text-sm font-medium rounded-lg border-l-4 border-red-500">{error}</div>}

        <form onSubmit={handleSubmit} className="flex flex-col space-y-5">
          <div>
            <label className="block text-gray-700 font-bold mb-2 text-sm">E-posta Adresi</label>
            <input type="email" required placeholder="ornek@mail.com" className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none transition-all" value={email} onChange={e => setEmail(e.target.value)} />
          </div>
          
          <button type="submit" disabled={loading} className="w-full bg-[#1A56DB] hover:bg-blue-800 text-white font-bold py-4 rounded-xl mt-4 border-2 border-transparent">
            {loading ? 'Gönderiliyor...' : 'Sıfırlama Kodu Gönder'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm">
          <Link to="/login" className="text-gray-500 hover:text-[#1A56DB] font-bold transition-colors">Giriş Yap sayfasına dön</Link>
        </div>
      </div>
    </div>
  );
}
