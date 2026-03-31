import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';

export default function Register() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    tc_no: '',
    password: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    
    try {
      // JSON Olarak Register Endpoint'e gönder
      const res = await api.post('/auth/register', formData);
      setSuccessMsg(res.data.message || "Gerçekleşti! Kod ekranına yönlendiriliyorsunuz...");
      
      // Kayıt başarılıysa, state ile birlikte Verify sayfasına yönlendir
      setTimeout(() => {
        navigate('/verify', { state: { email: formData.email } });
      }, 1500);
      
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic'ten gelen "Value error, Şifre en..." kısmındaki "Value error, " metnini silip temiz listele
        const messages = detail.map(e => e.msg.replace('Value error, ', ''));
        setError(messages.join(' | '));
      } else {
        setError(detail || "Sisteme kayıt olurken beklenmeyen bir hata oluştu.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="flex flex-col items-center justify-center py-16 animate-fade-in px-4">
      <div className="bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-gray-100 max-w-lg w-full relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-2 bg-green-500"></div>
        
        <h2 className="text-3xl font-extrabold text-gray-800 text-center mb-8">Aramıza Katılın!</h2>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm font-medium rounded-r">
             {error}
          </div>
        )}
        
        {successMsg && (
          <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 text-green-700 text-sm font-medium rounded-r flex flex-col gap-2">
            <span className="font-bold flex items-center">
               <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
               Kayıt Başarılı
            </span>
            {successMsg} 
            <span className="text-xs text-green-600 mt-2">* Not: Test ortamında iseniz, doğrulama kodunu DB'den manuel 'is_verified=True' yapabilirsiniz.</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="flex flex-col space-y-4">
          <div>
             <label className="block text-gray-700 font-bold mb-2 text-sm" htmlFor="name">Ad Soyad</label>
             <input type="text" id="name" name="name" required placeholder="Tam Adınız" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none" value={formData.name} onChange={handleChange} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div>
                <label className="block text-gray-700 font-bold mb-2 text-sm" htmlFor="tc_no">TC Kimlik No</label>
                <input type="text" id="tc_no" name="tc_no" required placeholder="11 Haneli TC Kimlik" maxLength={11} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none" value={formData.tc_no} onChange={handleChange} />
             </div>
             <div>
                <label className="block text-gray-700 font-bold mb-2 text-sm" htmlFor="email">E-posta</label>
                <input type="email" id="email" name="email" required placeholder="Kayıtlı Mail" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none" value={formData.email} onChange={handleChange} />
             </div>
          </div>
          <div>
             <label className="block text-gray-700 font-bold mb-2 text-sm" htmlFor="password">Şifre</label>
             <input type="password" id="password" name="password" required placeholder="Güclü Bir Şifre Oluşturun" className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none" value={formData.password} onChange={handleChange} />
          </div>
          
          <button 
            type="submit" 
            disabled={loading || successMsg}
            className="w-full bg-[#1A56DB] hover:bg-blue-800 text-white font-bold py-4 rounded-xl shadow-md transition-transform flex justify-center items-center mt-6 disabled:opacity-70"
          >
            {loading ? 'Kayıt Olunuyor...' : 'Güvenli Kayıt Oluştur'}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-gray-500 border-t pt-5">
          Zaten bir hesabınız var mı?{' '}
          <Link to="/login" className="text-[#1A56DB] font-bold hover:underline">
            Giriş Yapın
          </Link>
        </div>
      </div>
    </div>
  );
}
