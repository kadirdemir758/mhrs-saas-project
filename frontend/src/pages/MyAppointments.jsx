import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function MyAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('upcoming');
  
  const navigate = useNavigate();

  const fetchAppointments = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const res = await api.get('/appointments/me');
      setAppointments(res.data.appointments || []);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        navigate('/login');
      } else {
        console.error("Randevular yüklenemedi", err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, [navigate]);

  const handleCancel = async (id) => {
    if (window.confirm("Bu randevuyu iptal etmek istediğinize emin misiniz? İşlem geri alınamaz.")) {
      try {
        await api.patch(`/appointments/${id}/cancel`);
        fetchAppointments(); // Listeyi yenile statüyü kırmızı iptale çek
      } catch (err) {
        alert(err.response?.data?.detail || "Randevu iptal edilemedi.");
      }
    }
  };

  const handleDownload = async (id) => {
    try {
        const res = await api.get(`/appointments/${id}/download`, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Randevu_${id}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    } catch(err) {
        alert("PDF indirilemedi.");
    }
  }

  // Yaklaşanlar ve Geçmiş Sekme Ayrımı
  const now = new Date();
  const upcoming = appointments.filter(a => new Date(a.appointment_datetime) > now && a.status !== 'cancelled');
  const pastOrCancelled = appointments.filter(a => new Date(a.appointment_datetime) <= now || a.status === 'cancelled');

  if (loading) {
    return (
      <div className="flex justify-center items-center py-32">
        <div className="animate-spin w-12 h-12 border-4 border-[#1A56DB] border-t-transparent rounded-full shadow-md"></div>
      </div>
    );
  }

  // Modern Randevu Kart Tasarımı
  const renderCard = (appt, isUpcoming) => {
    const dateObj = new Date(appt.appointment_datetime);
    const dateStr = dateObj.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
    const timeStr = dateObj.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
    
    return (
      <div key={appt.id} className="bg-white border border-gray-100 rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all relative overflow-hidden group">
         <div className={`absolute top-0 left-0 w-full h-1.5 ${appt.status === 'cancelled' ? 'bg-red-500' : isUpcoming ? 'bg-green-500' : 'bg-gray-400'}`}></div>
         
         <div className="flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
            <div className="flex items-center gap-5">
               <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold shadow-inner ${appt.status === 'cancelled' ? 'bg-red-50 text-red-500' : isUpcoming ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-500'}`}>
                 {dateObj.getDate()}
               </div>
               <div>
                  <h3 className="text-xl font-extrabold text-gray-800">{appt.doctor ? `${appt.doctor.title} ${appt.doctor.name}` : `Doktor Bilinmiyor`}</h3>
                  <p className="text-[#1A56DB] font-semibold">{appt.clinic ? appt.clinic.name : 'Genel Poliklinik'}</p>
                  <p className="text-sm text-gray-500 mt-1 flex items-center gap-1">
                     <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                     {appt.clinic ? `${appt.clinic.city} - ${appt.clinic.district}` : 'Konum Belirtilmemiş'}
                  </p>
                  {appt.status === 'cancelled' && <span className="inline-block mt-2 px-3 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full">İPTAL EDİLMİŞTİR</span>}
               </div>
            </div>

            <div className="flex flex-col items-start md:items-end gap-3 w-full md:w-auto mt-4 md:mt-0">
               <div className="text-left md:text-right bg-gray-50 px-4 py-2 rounded-xl border border-gray-100 w-full md:w-auto">
                 <p className="text-sm text-gray-500 font-medium">Randevu Zamanı</p>
                 <p className="text-lg font-bold text-gray-900">{dateStr} <span className="text-[#1A56DB] ml-1">{timeStr}</span></p>
               </div>
               
               <div className="flex gap-2 w-full md:w-auto justify-end">
                 {appt.status !== 'cancelled' && (
                   <button onClick={() => handleDownload(appt.id)} className="bg-blue-50 hover:bg-blue-100 text-blue-600 p-2.5 rounded-xl transition-colors font-bold shadow-sm" title="PDF Düzenle">
                     <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                   </button>
                 )}
                 {isUpcoming && appt.status !== 'cancelled' && (
                   <button onClick={() => handleCancel(appt.id)} className="bg-red-50 hover:bg-red-100 text-red-600 px-4 py-2.5 rounded-xl font-bold shadow-sm transition-colors border border-red-100 text-sm">
                     Randevuyu İptal Et
                   </button>
                 )}
               </div>
            </div>
         </div>
      </div>
    );
  };

  return (
    <div className="max-w-5xl mx-auto py-10 px-4 animate-fade-in relative z-10">
      <div className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight">Randevularım</h1>
          <p className="text-gray-500 font-medium mt-2">Geçmiş ve gelecek tüm hastane ziyaretlerinizi buradan yönetebilirsiniz.</p>
        </div>
        
        <button onClick={() => navigate('/new-appointment')} className="bg-[#1A56DB] hover:bg-blue-800 text-white px-8 py-3 rounded-full font-bold shadow-lg transition-transform transform hover:scale-105 active:scale-95">
           + Yeni Randevu Al
        </button>
      </div>

      <div className="flex gap-4 mb-8 border-b-2 border-gray-100 pb-1 overflow-x-auto">
        <button 
           onClick={() => setActiveTab('upcoming')}
           className={`pb-3 px-2 font-bold text-lg whitespace-nowrap border-b-4 transition-all ${activeTab === 'upcoming' ? 'border-[#1A56DB] text-[#1A56DB]' : 'border-transparent text-gray-400 hover:text-gray-600 hover:border-gray-300'}`}
        >
          Yaklaşan Randevular ({upcoming.length})
        </button>
        <button 
           onClick={() => setActiveTab('past')}
           className={`pb-3 px-2 font-bold text-lg whitespace-nowrap border-b-4 transition-all ${activeTab === 'past' ? 'border-gray-800 text-gray-800' : 'border-transparent text-gray-400 hover:text-gray-600 hover:border-gray-300'}`}
        >
          Geçmiş / İptal Edilenler ({pastOrCancelled.length})
        </button>
      </div>

      <div className="space-y-6">
        {activeTab === 'upcoming' && (
          upcoming.length > 0 ? upcoming.map(a => renderCard(a, true)) : (
            <div className="text-center p-16 bg-gray-50 rounded-3xl border border-dashed border-gray-300">
               <svg className="w-20 h-20 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
               <p className="text-xl text-gray-500 font-medium">Yaklaşan hiçbir randevunuz bulunmuyor.</p>
            </div>
          )
        )}

        {activeTab === 'past' && (
          pastOrCancelled.length > 0 ? pastOrCancelled.map(a => renderCard(a, false)) : (
            <div className="text-center p-16 bg-gray-50 rounded-3xl border border-dashed border-gray-300">
               <svg className="w-20 h-20 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
               <p className="text-xl text-gray-500 font-medium">Geçmiş randevu kaydınız bulunmuyor.</p>
            </div>
          )
        )}
      </div>
    </div>
  );
}
