import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    new_password: '',
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showPasswordFields, setShowPasswordFields] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const res = await api.get('/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(res.data);
      setFormData({
        name: res.data.name || '',
        email: res.data.email || '',
        phone: res.data.phone || '',
        new_password: '',
      });
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user_name');
        navigate('/login');
        return;
      }
      setMessage({ type: 'error', text: 'Profil bilgileri alınamadı.' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    const payload = {};
    if (formData.name !== profile.name) payload.name = formData.name;
    if (formData.email !== profile.email) payload.email = formData.email;
    if (formData.phone !== profile.phone) payload.phone = formData.phone;
    if (showPasswordFields && formData.new_password) payload.new_password = formData.new_password;

    if (Object.keys(payload).length === 0) {
      setMessage({ type: 'info', text: 'Herhangi bir değişiklik yapmadınız.' });
      setSaving(false);
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const res = await api.patch('/users/me', payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(res.data);
      
      if (payload.name) {
        localStorage.setItem('user_name', res.data.name);
        window.dispatchEvent(new Event('storage'));
      }
      
      setFormData({ ...formData, new_password: '' });
      setShowPasswordFields(false);
      setMessage({ type: 'success', text: 'Profiliniz başarıyla güncellendi!' });
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user_name');
        navigate('/login');
        return;
      }
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setMessage({ type: 'error', text: detail.map(e => e.msg.replace('Value error, ', '')).join(' | ') });
      } else {
        setMessage({ type: 'error', text: detail || "Güncelleme sırasında bir hata oluştu." });
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="w-12 h-12 border-4 border-[#1A56DB] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-10 max-w-6xl animate-fade-in">
      <h1 className="text-3xl font-extrabold text-gray-900 mb-8 border-b pb-4">Profilim</h1>
      
      {message.text && (
        <div className={`mb-6 p-4 text-sm font-bold rounded-xl border-l-4 shadow-sm ${
          message.type === 'success' ? 'bg-green-50 text-green-700 border-green-500' : 
          message.type === 'info' ? 'bg-blue-50 text-blue-700 border-blue-500' :
          'bg-red-50 text-red-700 border-red-500'
        }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div className="lg:col-span-1">
          <div className="bg-white rounded-3xl shadow-lg border border-gray-100 p-8 text-center sticky top-24">
            <div className="w-32 h-32 bg-gradient-to-tr from-blue-100 to-blue-50 rounded-full flex items-center justify-center mx-auto mb-6 shadow-inner border-4 border-white">
              <span className="text-5xl font-black text-[#1A56DB]">{profile?.name?.charAt(0)}</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-1">{profile?.name}</h2>
            <div className="inline-block px-3 py-1 bg-green-50 border border-green-200 text-green-700 rounded-full text-xs font-bold uppercase tracking-wide mb-6">
              Aktif Hesap
            </div>
            
            <div className="space-y-4 text-left mt-4 border-t pt-6 border-gray-100">
              <div>
                <p className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-1">T.C. Kimlik Numarası</p>
                <p className="font-semibold text-gray-700">{profile?.tc_no}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-1">E-posta Adresi</p>
                <p className="font-semibold text-gray-700 break-all">{profile?.email}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="bg-white rounded-3xl shadow-lg border border-gray-100 p-8">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <svg className="w-6 h-6 text-[#1A56DB]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
              Bilgileri Güncelle
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-gray-700 font-bold mb-2 text-sm">Ad Soyad</label>
                  <input type="text" name="name" value={formData.name} onChange={handleInputChange} className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none transition-all" required />
                </div>
                <div>
                  <label className="block text-gray-700 font-bold mb-2 text-sm">Telefon Numarası</label>
                  <input type="tel" name="phone" value={formData.phone} onChange={handleInputChange} placeholder="05XXXXXXXXX" className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none transition-all" />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-gray-700 font-bold mb-2 text-sm">E-posta Adresi</label>
                  <input type="email" name="email" value={formData.email} onChange={handleInputChange} className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none transition-all" required />
                </div>
              </div>

              <div className="border-t border-gray-100 pt-6 mt-8">
                <button 
                  type="button" 
                  onClick={() => setShowPasswordFields(!showPasswordFields)}
                  className="text-[#1A56DB] font-bold text-sm flex items-center gap-2 hover:underline focus:outline-none"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  Şifre Değiştirmek İstiyorum
                </button>

                {showPasswordFields && (
                  <div className="mt-4 p-5 bg-blue-50/50 rounded-2xl border border-blue-100 animate-fade-in">
                    <div>
                      <label className="block text-gray-700 font-bold mb-2 text-sm">Yeni Şifre</label>
                      <input 
                        type="password" 
                        name="new_password" 
                        value={formData.new_password} 
                        onChange={handleInputChange} 
                        placeholder="En az 8 karakter, 1 büyük harf ve 1 rakam"
                        className="w-full p-3.5 bg-white border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 outline-none transition-all" 
                      />
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end pt-4">
                <button 
                  type="submit" 
                  disabled={saving}
                  className="bg-[#1A56DB] hover:bg-blue-800 text-white font-bold py-3.5 px-8 rounded-xl shadow-md transition-all flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed border-2 border-transparent"
                >
                  {saving ? (
                    <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                  )}
                  {saving ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
                </button>
              </div>
            </form>
          </div>
        </div>

      </div>
    </div>
  );
}
