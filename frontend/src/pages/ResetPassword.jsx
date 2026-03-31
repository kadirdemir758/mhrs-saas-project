import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import api from '../api';

export default function ResetPassword() {
  const [email, setEmail] = useState('');
  const [resetCode, setResetCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState('');

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Navigate url üzerinden email query string yakalanıyor: (?email=ornek@mail.com)
    const params = new URLSearchParams(location.search);
    const emailParam = params.get('email');
    if (emailParam) setEmail(emailParam);
  }, [location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg('');

    try {
      const res = await api.post('/auth/reset-password', {
        email: email,
        reset_code: resetCode,
        new_password: newPassword
      });
      setSuccessMsg(res.data.message || "Şifreniz başarıyla sıfırlandı!");
      setTimeout(() => navigate('/login'), 2500);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(e => e.msg.replace('Value error, ', '')).join(' | '));
      } else {
        setError(detail || "Geçersiz kod veya bir hata oluştu.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-20 animate-fade-in px-4">
      <div className="bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-gray-100 max-w-md w-full relative">
        <h2 className="text-2xl font-extrabold text-gray-800 text-center mb-6">Yeni Şifre Belirleme</h2>
        
        {error && <div className="mb-6 p-4 bg-red-50 text-red-700 text-sm font-medium rounded-lg border-l-4 border-red-500">{error}</div>}
        {successMsg && <div className="mb-6 p-4 bg-green-50 text-green-700 text-sm font-medium rounded-lg border-l-4 border-green-500">{successMsg} Yönlendiriliyorsunuz...</div>}

        <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
          <div>
            <label className="block text-gray-700 font-bold mb-2 text-sm">Hesap (E-posta)</label>
            <input type="email" required readOnly={!!email} className="w-full p-3.5 bg-gray-100 border border-gray-200 rounded-xl text-gray-600 outline-none" value={email} onChange={e => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="block text-gray-700 font-bold mb-2 text-sm">Postanıza Gelen 6 Haneli Kod</label>
            <input type="text" maxLength={6} required className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none text-center tracking-widest font-bold" value={resetCode} onChange={e => setResetCode(e.target.value)} />
          </div>
          <div>
            <label className="block text-gray-700 font-bold mb-2 text-sm">Sıfırdan Yepyeni Bir Şifre</label>
            <input type="password" required className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none" value={newPassword} onChange={e => setNewPassword(e.target.value)} />
          </div>
          
          <button type="submit" disabled={loading || successMsg} className="w-full bg-[#1A56DB] hover:bg-blue-800 text-white font-bold py-4 rounded-xl mt-4">
            {loading ? 'Sıfırlanıyor...' : 'Şifremi Sıfırla ve Kaydet'}
          </button>
        </form>
      </div>
    </div>
  );
}
