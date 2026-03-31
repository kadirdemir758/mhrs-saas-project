import React, { useState, useEffect } from 'react';
import api from '../api';

const citiesData = {
  "İstanbul": ["Kadıköy", "Şişli", "Beşiktaş", "Üsküdar", "Maltepe"],
  "Ankara": ["Çankaya", "Keçiören", "Yenimahalle", "Mamak", "Etimesgut"],
  "İzmir": ["Buca", "Karşıyaka", "Bornova", "Konak", "Karabağlar"],
  "Bursa": ["Osmangazi", "Nilüfer", "Yıldırım", "İnegöl"],
  "Antalya": ["Muratpaşa", "Kepez", "Konyaaltı", "Alanya"]
};

export default function AddDoctorModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    specialization: 'Dahiliye',
    city: '',
    district: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [clinics, setClinics] = useState([]);

  useEffect(() => {
    if (isOpen) {
      api.get('/doctors/clinics/list').then(res => setClinics(res.data)).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'city') {
      setFormData({ ...formData, city: value, district: '' });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      // If no clinic is selected, fallback to 1 (but it's better to force user to select if clinics exist)
      const clinicId = formData.clinic_id ? parseInt(formData.clinic_id) : (clinics.length > 0 ? clinics[0].id : 1);

      await api.post('/admin/doctors', 
        { ...formData, clinic_id: clinicId }, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      onSuccess("Doktor başarıyla eklendi!");
      
      // Formu temizle ve kapat
      setFormData({ name: '', email: '', password: '', specialization: 'Dahiliye', clinic_id: '', city: '', district: '' });
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Bir hata oluştu. Veritabanında klinik bulunmayabilir.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-3xl w-full max-w-md overflow-hidden shadow-2xl">
        <div className="bg-[#1A56DB] p-6 text-white flex justify-between items-center">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
            Yeni Doktor Ekle
          </h2>
          <button onClick={onClose} className="hover:bg-blue-800 p-1 rounded-full transition-colors font-black text-xl leading-none">
            &times;
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          {error && <div className="mb-4 bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-100 font-medium">{error}</div>}
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-1">Ad Soyad</label>
              <input type="text" name="name" required value={formData.name} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Örn: Dr. Ahmet Yılmaz" />
            </div>
            
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-1">E-posta</label>
              <input type="email" name="email" required value={formData.email} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none" placeholder="ahmet@hastane.com" />
            </div>
            
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-1">Şifre</label>
              <input type="text" name="password" required value={formData.password} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Geçici şifre belirleyin" />
            </div>
            
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-1">Branş / Uzmanlık</label>
              <select name="specialization" value={formData.specialization} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none font-medium">
                <option value="Dahiliye">Dahiliye</option>
                <option value="Göz Hastalıkları">Göz Hastalıkları</option>
                <option value="Kardiyoloji">Kardiyoloji</option>
                <option value="Ortopedi">Ortopedi</option>
                <option value="Nöroloji">Nöroloji</option>
                <option value="Kulak Burun Boğaz">Kulak Burun Boğaz</option>
                <option value="Psikiyatri">Psikiyatri</option>
              </select>
            </div>
            
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-bold text-gray-700 mb-1">Şehir</label>
                <select name="city" required value={formData.city} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none font-medium text-gray-700">
                  <option value="">İl Seçiniz</option>
                  {Object.keys(citiesData).map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex-1">
                <label className="block text-sm font-bold text-gray-700 mb-1">İlçe</label>
                <select name="district" required disabled={!formData.city} value={formData.district} onChange={handleChange} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none font-medium text-gray-700 disabled:opacity-50 disabled:bg-gray-100">
                  <option value="">İlçe Seçiniz</option>
                  {formData.city && citiesData[formData.city]?.map(district => (
                    <option key={district} value={district}>{district}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          
          <div className="mt-8 flex gap-3">
            <button type="button" onClick={onClose} className="flex-1 py-3 text-gray-600 font-bold bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors">
              İptal
            </button>
            <button type="submit" disabled={loading} className="flex-1 py-3 text-white font-bold bg-[#1A56DB] hover:bg-blue-800 rounded-xl shadow-md transition-colors flex justify-center items-center">
              {loading ? <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span> : 'Kaydet'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
