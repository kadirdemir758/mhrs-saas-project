import React, { useState, useEffect } from 'react';
import api from '../api';

export default function AppointmentStepper() {
  const [step, setStep] = useState(1);
  
  // State
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [appointmentData, setAppointmentData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fake auth user ID for Phase 8
  const patientId = 1; 

  // 1. Fetch Doctors automatically
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    api.get('/doctors/')
      .then(res => setDoctors(res.data.doctors || []))
      .catch(err => console.error("Doktorlar yüklenemedi", err));
  }, []);

  // 2. Fetch Slots when Date & Doctor changes
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    if (selectedDoctor && selectedDate) {
      setLoading(true);
      api.get('/slots/available', { params: { doctor_id: selectedDoctor.id, date: selectedDate } })
        .then(res => setAvailableSlots(res.data || []))
        .catch(err => console.error("Slotlar yüklenemedi", err))
        .finally(() => setLoading(false));
    }
  }, [selectedDoctor, selectedDate]);

  const handleCreateAppointment = async () => {
    try {
      setLoading(true);
      const payload = {
        doctor_id: selectedDoctor.id,
        clinic_id: selectedDoctor.clinic_id,
        appointment_datetime: `${selectedDate}T${selectedSlot}:00Z` // ISO Formatında Saat dilimsiz
      };

      const res = await api.post('/appointments/', payload, { params: { patient_id: patientId } });
      setAppointmentData(res.data);
      setStep(3);
    } catch (err) {
      alert("Randevu alınamadı: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!appointmentData) return;
    try {
      const res = await api.get(`/appointments/${appointmentData.id}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `MHRS_Randevu_${appointmentData.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("PDF İndirme hatası");
    }
  };

  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  return (
    <div className="w-full">
      {/* İlerleme Çubuğu */}
      <div className="flex items-center justify-between mb-10 relative px-4 md:px-0 max-w-2xl mx-auto">
        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-full h-1.5 bg-gray-100 -z-10 rounded"></div>
        <div 
           className="absolute left-0 top-1/2 transform -translate-y-1/2 h-1.5 bg-[#1A56DB] -z-10 transition-all duration-500 rounded" 
           style={{ width: step === 1 ? '0%' : step === 2 ? '50%' : '100%' }}
        ></div>
        
        {['Hekim Seçimi', 'Zaman Seçimi', 'Onay'].map((label, idx) => {
          const num = idx + 1;
          const isActive = step >= num;
          return (
            <div key={num} className="flex flex-col items-center">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-colors border-4 ${isActive ? 'bg-[#1A56DB] border-blue-200 text-white shadow-md' : 'bg-white border-gray-200 text-gray-400'}`}>
                {num}
              </div>
              <span className={`mt-2 text-xs md:text-sm font-semibold hidden sm:block ${isActive ? 'text-[#1A56DB]' : 'text-gray-400'}`}>{label}</span>
            </div>
          )
        })}
      </div>

      {/* Adım 1: Doktor Seçimi */}
      {step === 1 && (
        <div className="animate-fade-in">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {doctors.map(doc => (
              <div 
                key={doc.id}
                onClick={() => setSelectedDoctor(doc)}
                className={`p-5 rounded-xl cursor-pointer transition-all ${selectedDoctor?.id === doc.id ? 'bg-[#1A56DB] text-white shadow-lg transform -translate-y-1' : 'bg-gray-50 hover:bg-white hover:shadow-md border border-gray-100 text-gray-800'}`}
              >
                <div className="flex items-center mb-3">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl mr-4 ${selectedDoctor?.id === doc.id ? 'bg-white/20' : 'bg-blue-100 text-[#1A56DB]'}`}>
                    {doc.name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="font-bold text-lg">{doc.title} {doc.name}</h4>
                    <p className={`text-sm ${selectedDoctor?.id === doc.id ? 'text-blue-100' : 'text-gray-500'}`}>{doc.specialization}</p>
                  </div>
                </div>
              </div>
            ))}
            {doctors.length === 0 && <p className="text-gray-500 col-span-full text-center py-8">Sistemde aktif hekim bulunmuyor. Fastapi panelden hekim ekleyin.</p>}
          </div>
          
          <div className="mt-8 flex justify-end">
            <button 
              disabled={!selectedDoctor}
              onClick={() => setStep(2)}
              className="bg-[#1A56DB] hover:bg-blue-800 disabled:bg-gray-200 disabled:text-gray-400 text-white font-bold py-3 px-8 rounded-xl transition-colors shadow-md flex items-center gap-2"
            >
              Tarih Seçimine İlerle &rarr;
            </button>
          </div>
        </div>
      )}

      {/* Adım 2: Tarih ve Slot */}
      {step === 2 && (
        <div className="animate-fade-in">
          <div className="bg-gray-50 p-4 rounded-xl flex items-center justify-between border border-gray-100 mb-8">
             <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-[#1A56DB] text-white rounded-lg flex items-center justify-center font-bold">
                  {selectedDoctor?.name.charAt(0)}
                </div>
                <div>
                  <p className="text-sm text-gray-500">Seçilen Hekim</p>
                  <p className="font-bold text-gray-800">{selectedDoctor?.title} {selectedDoctor?.name}</p>
                </div>
             </div>
             <button onClick={() => setStep(1)} className="text-sm font-semibold text-[#1A56DB] hover:underline px-3 py-1 rounded bg-blue-50">Değiştir</button>
          </div>

          <div className="mb-8">
            <label className="block text-gray-700 font-semibold mb-3">Randevu Tarihi Seçiniz</label>
            <input 
              type="date" 
              className="w-full md:w-1/2 lg:w-1/3 p-3.5 bg-white border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] outline-none shadow-sm transition-all text-gray-700 font-medium"
              value={selectedDate}
              onChange={(e) => { setSelectedDate(e.target.value); setSelectedSlot(''); }}
              min={getMinDate()}
            />
          </div>

          {selectedDate && (
            <div className="bg-white border top-2 border-gray-100 rounded-2xl p-6 shadow-sm">
              <p className="text-gray-800 font-bold mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Müsait Saatler
              </p>
              
              {loading ? (
                 <div className="flex justify-center py-8">
                   <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#1A56DB]"></div>
                 </div>
              ) : (
                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
                  {availableSlots.length > 0 ? availableSlots.map(slot => (
                    <button
                      key={slot}
                      onClick={() => setSelectedSlot(slot)}
                      className={`py-2.5 px-1 rounded-xl font-bold text-sm transition-all duration-200 border-2 ${selectedSlot === slot ? 'bg-[#1A56DB] border-[#1A56DB] text-white shadow-md transform scale-105' : 'bg-gray-50 text-gray-700 border-transparent hover:border-blue-200 hover:bg-blue-50'}`}
                    >
                      {slot}
                    </button>
                  )) : (
                    <div className="col-span-full flex flex-col items-center justify-center p-8 bg-red-50 text-red-600 rounded-xl border border-red-100">
                      <svg className="w-10 h-10 mb-2 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                      <span className="font-semibold">Bu tarihte uygun randevu saati bulunmuyor.</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="mt-8 flex flex-col max-md:gap-3 md:flex-row md:justify-between items-center">
            <button 
              onClick={() => setStep(1)}
              className="w-full md:w-auto bg-white border-2 border-gray-200 hover:bg-gray-50 text-gray-700 font-bold py-3 px-8 rounded-xl transition-colors"
            >
              Geri Git
            </button>
            <button 
              disabled={!selectedDate || !selectedSlot || loading}
              onClick={handleCreateAppointment}
              className="w-full md:w-auto bg-green-600 hover:bg-green-700 disabled:bg-gray-200 disabled:text-gray-400 text-white font-bold py-3 px-10 rounded-xl transition-all shadow-md flex justify-center"
            >
              {loading ? 'Onaylanıyor...' : 'Randevuyu Onayla'}
            </button>
          </div>
        </div>
      )}

      {/* Adım 3: Başarılı & PDF İndirme */}
      {step === 3 && (
        <div className="animate-fade-in text-center py-12 px-4 bg-green-50/50 rounded-2xl border border-green-100">
          <div className="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg shadow-green-200">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900 mb-3">Randevunuz Onaylandı!</h2>
          <p className="text-gray-600 text-lg mb-8 max-w-lg mx-auto">
            İşleminiz başarıyla kaydedildi. Hastaneye girişte kullanacağınız randevu belgenizi aşağıdan PDF olarak indirebilirsiniz.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
             <button 
                onClick={handleDownloadPDF}
                className="w-full sm:w-auto bg-[#1A56DB] hover:bg-blue-800 flex items-center justify-center text-white font-bold py-3.5 px-8 rounded-xl shadow-md transition-transform hover:scale-105"
             >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                PDF Belgesini İndir
             </button>
             <button 
                onClick={() => {
                  setStep(1);
                  setSelectedDoctor(null);
                  setSelectedDate('');
                  setSelectedSlot('');
                }}
                className="w-full sm:w-auto bg-white border-2 border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300 font-bold py-3.5 px-8 rounded-xl transition-colors"
             >
                Yeni Randevu
             </button>
          </div>
        </div>
      )}
    </div>
  );
}
