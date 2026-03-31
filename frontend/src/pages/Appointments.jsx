import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function Appointments() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  // States for Cascading (Akıllı Açılır Menüler)
  const [clinicsData, setClinicsData] = useState([]);
  
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedClinic, setSelectedClinic] = useState(null);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedSlot, setSelectedSlot] = useState('');
  
  // Lists
  const [cities, setCities] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [filteredClinics, setFilteredClinics] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [slots, setSlots] = useState([]);
  const [bookedTimes, setBookedTimes] = useState([]);
  
  const [step, setStep] = useState(1);
  const [appointmentMade, setAppointmentMade] = useState(null);

  // 1. Auth Check & Fetch Initial Clinics
  useEffect(() => {
    const fetchInit = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const meRes = await api.get('/auth/me');
        setUser(meRes.data);
        
        // Klinikleri listele: JWT interceptor ile otomatik olarak doğrulanır.
        const clinicRes = await api.get('/doctors/clinics/list');
        const allClinics = clinicRes.data;
        setClinicsData(allClinics);
        
        // Türkiye İllerini API'den çek
        const provRes = await api.get('/locations/provinces');
        setCities(provRes.data);
        
        setLoading(false);
      } catch (err) {
        console.error("Yetkisiz erişim", err);
        navigate('/login');
      }
    };
    fetchInit();
  }, [navigate]);

  // 2. İl seçildiğinde İlçeleri API'den yükle
  useEffect(() => {
    if (selectedCity) {
      // Find the ID of the selected city string
      const cityObj = cities.find(c => c.name === selectedCity);
      if (cityObj) {
        api.get(`/locations/districts?province_id=${cityObj.id}`)
           .then(res => setDistricts(res.data))
           .catch(err => console.error("İlçeler çekilemedi", err));
      }
      setSelectedDistrict('');
      setSelectedClinic(null);
      setSelectedDoctor(null);
    }
  }, [selectedCity, cities]);

  // 3. İlçe Seçildiğinde Klinikleri filtrele
  useEffect(() => {
    if (selectedCity && selectedDistrict) {
      const finalClinics = clinicsData.filter(c => c.city === selectedCity && c.district === selectedDistrict);
      setFilteredClinics(finalClinics);
      setSelectedClinic(null);
      setSelectedDoctor(null);
    }
  }, [selectedDistrict, selectedCity, clinicsData]);

  // 4. Klinik seçildiğinde Hekimleri getir (Backend ?clinic_id filter)
  useEffect(() => {
    if (selectedClinic) {
      api.get(`/doctors/?clinic_id=${selectedClinic.id}`)
         .then(res => setDoctors(res.data.doctors || []))
         .catch(err => console.error("Doktorlar yüklenemedi", err));
    }
  }, [selectedClinic]);

  // 5. Hekim ve Tarih seçildiğinde uygun Slotları ve Dolu saatleri getir
  useEffect(() => {
    if (selectedDoctor && selectedDate) {
      // 1. Tüm slot listesini getir
      api.get('/slots/available', { params: { doctor_id: selectedDoctor.id, date: selectedDate } })
         .then(res => setSlots(res.data || []))
         .catch(err => console.error("Slotlar yüklenemedi", err));
         
      // 2. Dolu saatlerin dizisini (array) DB üzerinden getir (örn: ["09:00", "09:30"])
      api.get('/appointments/booked-slots', { params: { doctor_id: selectedDoctor.id, date: selectedDate } })
         .then(res => setBookedTimes(res.data || []))
         .catch(err => console.error("Dolu saatler çekilemedi", err));
    }
  }, [selectedDoctor, selectedDate]);

  // GÖNDER & ONAYLA
  const handleConfirm = async () => {
    try {
      const payload = {
        doctor_id: selectedDoctor.id,
        clinic_id: selectedClinic.id,
        appointment_datetime: `${selectedDate}T${selectedSlot}:00Z`
      };
      
      const res = await api.post('/appointments/', payload, { params: { patient_id: user.id } });
      setAppointmentMade(res.data);
      setStep(5);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
      
      // Hata doluluk kaynaklıysa (400) yeni dolu saatleri güncelleyip butonu iptal edelim
      setSelectedSlot('');
      if (selectedDoctor && selectedDate) {
        api.get('/appointments/booked-slots', { params: { doctor_id: selectedDoctor.id, date: selectedDate } })
           .then(res => setBookedTimes(res.data || []));
      }
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const res = await api.get(`/appointments/${appointmentMade.id}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `MHRS_Randevu_${appointmentMade.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("PDF indirilemedi");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-32">
        <div className="animate-spin w-12 h-12 border-4 border-[#1A56DB] border-t-transparent rounded-full shadow-md"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 animate-fade-in relative">
      <div className="absolute top-10 right-10 -z-10 opacity-30">
        <svg className="w-64 h-64 text-blue-100" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/><path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z"/></svg>
      </div>

      <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-200">
         <div className="flex items-center gap-4">
           <div className="w-14 h-14 bg-[#1A56DB] text-white rounded-2xl flex items-center justify-center shadow-lg">
             <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
           </div>
           <div>
             <h1 className="text-3xl lg:text-4xl font-extrabold text-gray-800 tracking-tight">Akıllı Randevu Ekranı</h1>
             <p className="text-gray-500 font-medium mt-1">Hoş geldin <span className="text-[#1A56DB]">{user?.name}</span>, sırasıyla filtreleri uygulayınız.</p>
           </div>
         </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-8 items-start">
        
        {/* Sol Panel: Cascading (Kademeli) Filtreler */}
        <div className="w-full lg:w-1/3 bg-white p-6 md:p-8 rounded-3xl shadow-xl border border-gray-100 flex flex-col gap-6">
           
           <div>
             <label className="flex items-center text-sm font-bold text-gray-700 mb-2 gap-2"><div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">1</div> İl Seçimi</label>
             <select 
                className="w-full p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] active:border-[#1A56DB] outline-none transition-all cursor-pointer font-medium"
                value={selectedCity}
                onChange={e => setSelectedCity(e.target.value)}
             >
                <option value="">-- Şehir Belirleyin --</option>
                {cities.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
             </select>
           </div>
           
           <div>
             <label className={`flex items-center text-sm font-bold transition-colors mb-2 gap-2 ${selectedCity ? 'text-gray-700' : 'text-gray-400'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${selectedCity ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'}`}>2</div> İlçe Seçimi
             </label>
             <select 
                className="w-full p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] outline-none transition-all disabled:opacity-50 cursor-pointer font-medium"
                value={selectedDistrict}
                onChange={e => setSelectedDistrict(e.target.value)}
                disabled={!selectedCity}
             >
                <option value="">-- İlçe Seçin --</option>
                {districts.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
             </select>
           </div>

           <div>
             <label className={`flex items-center text-sm font-bold mb-2 transition-colors gap-2 ${selectedDistrict ? 'text-gray-700' : 'text-gray-400'}`}>
               <div className={`w-6 h-6 rounded-full flex items-center justify-center ${selectedDistrict ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'}`}>3</div> Klinik (Poliklinik)
             </label>
             <select 
                className="w-full p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] outline-none transition-all disabled:opacity-50 cursor-pointer font-medium"
                value={selectedClinic?.id || ''}
                onChange={e => {
                  const cId = parseInt(e.target.value);
                  setSelectedClinic(filteredClinics.find(c => c.id === cId) || null);
                  setSelectedDoctor(null);
                }}
                disabled={!selectedDistrict}
             >
                <option value="">-- Klinik Arayın --</option>
                {filteredClinics.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
             </select>
             {selectedDistrict && filteredClinics.length === 0 && <p className="text-xs text-red-500 mt-2 font-medium">Bu bölgede henüz kayıtlı klinik bulunamadı.</p>}
           </div>

           <div>
             <label className={`flex items-center text-sm font-bold mb-2 transition-colors gap-2 ${selectedClinic ? 'text-gray-700' : 'text-gray-400'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${selectedClinic ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'}`}>4</div> Hekim Belirleyin
             </label>
             <select 
                className="w-full p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] outline-none transition-all disabled:opacity-50 cursor-pointer font-medium"
                value={selectedDoctor?.id || ''}
                onChange={e => {
                  const dId = parseInt(e.target.value);
                  setSelectedDoctor(doctors.find(d => d.id === dId) || null);
                  setSelectedDate('');
                  setSelectedSlot('');
                }}
                disabled={!selectedClinic || doctors.length === 0}
             >
                <option value="">-- Hekim Seçin --</option>
                {doctors.map(d => <option key={d.id} value={d.id}>{d.title} {d.name} ({d.specialization})</option>)}
             </select>
             {selectedClinic && doctors.length === 0 && <p className="text-xs text-red-500 mt-2 font-medium">Seçili kliniğe atanmış bir doktor bulunmuyor.</p>}
           </div>
        </div>

        {/* Sağ Panel: Takvim ve Aksiyonlar */}
        <div className="w-full lg:w-2/3 bg-white p-6 md:p-10 rounded-3xl shadow-xl border border-gray-100 min-h-[480px] flex flex-col items-center justify-center relative overflow-hidden">
           
           {step === 5 ? (
              // BİTİŞ & İNDİRME EKRANI
              <div className="text-center animate-fade-in z-10 w-full px-4">
                <div className="w-28 h-28 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-6 shadow-inner ring-4 ring-green-100">
                  <svg className="w-14 h-14 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                </div>
                <h2 className="text-4xl font-extrabold text-gray-900 mb-3">Randevu Başarılı</h2>
                <p className="text-gray-500 mb-10 max-w-lg mx-auto text-lg leading-relaxed">
                  Randevunuz sistemlerimize kaydedilmiştir. Hastane personeline kolaylık sağlaması adına PDF barkodunuzu hemen indirebilirsiniz.
                </p>
                <div className="flex flex-col sm:flex-row gap-5 justify-center mt-6">
                   <button onClick={handleDownloadPDF} className="bg-[#1A56DB] hover:bg-blue-800 text-white font-bold py-4 px-10 rounded-2xl shadow-xl shadow-blue-200 transition-transform transform active:scale-95 flex items-center justify-center gap-3">
                     <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                     PDF Randevu Belgesi
                   </button>
                   <button onClick={() => window.location.reload()} className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-4 px-8 rounded-2xl shadow-sm">
                     Yeni Randevu Al
                   </button>
                </div>
              </div>
           ) : !selectedDoctor ? (
              // DURAKLAMA EKRANI
              <div className="text-center text-gray-400 p-8 animate-pulse">
                 <svg className="w-28 h-28 mx-auto mb-6 opacity-20" fill="none" stroke="currentColor" strokeWidth={1} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                 <p className="text-xl font-medium tracking-wide">Lütfen sol panelden bilgileri eksiksiz doldurunuz.</p>
              </div>
           ) : (
             // RANDEVU GÜN VE SAAT SEÇİCİSİ
              <div className="w-full h-full animate-fade-in flex flex-col justify-start relative z-10">
                 {/* Seçilen Doktor Header */}
                 <div className="mb-6 flex justify-between items-center bg-blue-50/50 p-6 rounded-2xl border border-blue-50">
                    <div className="flex gap-4 items-center">
                       <div className="w-16 h-16 bg-white shadow-sm text-[#1A56DB] flex items-center justify-center rounded-2xl font-bold text-2xl border border-gray-100">
                         {selectedDoctor.name.charAt(0)}
                       </div>
                       <div>
                         <h3 className="text-2xl font-bold text-gray-800">{selectedDoctor.title} {selectedDoctor.name}</h3>
                         <p className="text-[#1A56DB] font-medium">{selectedClinic.name} • {selectedCity}/{selectedDistrict}</p>
                       </div>
                    </div>
                 </div>

                 <div className="mb-6">
                    <label className="block text-gray-700 font-bold mb-3 text-lg">Hangi gün geleceksiniz?</label>
                    <input 
                      type="date" 
                      className="w-full md:w-2/3 p-4 bg-white border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] outline-none text-gray-800 font-bold transition-all shadow-sm"
                      value={selectedDate}
                      onChange={(e) => { setSelectedDate(e.target.value); setSelectedSlot(''); }}
                      min={new Date().toISOString().split('T')[0]}
                    />
                 </div>

                 {selectedDate && (
                   <div className="flex-1 animate-fade-in mt-4">
                      <p className="text-gray-800 font-bold mb-4 text-lg flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        Müsait Saat Dilimleri
                      </p>
                      {slots.length > 0 ? (
                        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-4 mb-10 overflow-y-auto max-h-60 pr-2">
                          {slots.map(slot => {
                            const isBooked = bookedTimes.includes(slot);
                            return (
                              <button
                                key={slot}
                                onClick={() => setSelectedSlot(slot)}
                                disabled={isBooked}
                                className={`py-3 px-2 rounded-xl font-extrabold text-base transition-all duration-300 border-2 
                                  ${isBooked ? 'bg-gray-200 text-gray-400 cursor-not-allowed line-through border-transparent' : 
                                  selectedSlot === slot ? 'bg-[#1A56DB] border-[#1A56DB] text-white shadow-lg transform -translate-y-1' : 
                                  'bg-gray-50 text-gray-600 border-transparent hover:border-[#1A56DB] hover:bg-blue-50 hover:text-[#1A56DB]'}`}
                              >
                                {slot}
                              </button>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="p-6 bg-red-50 text-red-600 rounded-2xl border border-red-100 text-center font-bold text-lg">
                           Bu tarihte hekimin uygun randevu saati bulunmuyor.
                        </div>
                      )}
                   </div>
                 )}

                 {/* Sticky Footer */}
                 <div className="mt-auto pt-6 border-t border-gray-100 flex justify-end">
                    <button 
                      disabled={!selectedDate || !selectedSlot}
                      onClick={handleConfirm}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed disabled:shadow-none text-white font-extrabold py-5 px-12 rounded-2xl shadow-xl shadow-green-200 transition-all w-full sm:w-auto text-lg flex items-center justify-center gap-2"
                    >
                      {selectedSlot ? `Saat ${selectedSlot} İçin Onayla` : 'Randevuyu Onayla'}
                    </button>
                 </div>
              </div>
           )}
        </div>
      </div>
    </div>
  );
}
