import React, { useState, useEffect } from 'react';
import AddDoctorModal from '../components/AddDoctorModal';
import api from '../api';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [showModal, setShowModal] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  
  // States for real data
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total_patients: 0, total_appointments: 0, total_doctors: 0 });
  const [popularClinics, setPopularClinics] = useState([]);
  const [clinics, setClinics] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);

  const handleSuccess = (msg) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(''), 5000);
    if (activeTab === 'doctors') {
      fetchDoctors();
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'overview') {
        const [statsRes, popularRes] = await Promise.all([
          api.get('/admin/stats/summary'),
          api.get('/admin/stats/popular-clinics')
        ]);
        setStats(statsRes.data);
        setPopularClinics(popularRes.data);
      } else if (activeTab === 'clinics') {
        const clinicsRes = await api.get('/doctors/clinics/list');
        setClinics(clinicsRes.data);
      } else if (activeTab === 'doctors') {
        fetchDoctors();
      } else if (activeTab === 'appointments') {
        const apptsRes = await api.get('/admin/appointments');
        setAppointments(apptsRes.data);
      }
    } catch (err) {
      console.error("Yönetici verileri alınamadı", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDoctors = async () => {
    try {
      const docsRes = await api.get('/doctors/?limit=100');
      setDoctors(docsRes.data.doctors || []);
    } catch(err) {
      console.error(err);
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-8 animate-fade-in relative min-h-screen">
      
      {/* Sidebar */}
      <div className="w-full md:w-64 bg-white rounded-3xl shadow-xl border border-gray-100 p-6 flex flex-col gap-2 h-max sticky top-8">
        <div className="flex items-center gap-3 mb-8 px-2">
           <div className="w-12 h-12 bg-purple-100 text-purple-600 rounded-2xl flex items-center justify-center text-xl shadow-inner">⚙️</div>
           <div>
             <h2 className="text-xl font-black text-gray-800 tracking-tight">Admin</h2>
             <p className="text-xs font-bold text-gray-400">Kontrol Paneli</p>
           </div>
        </div>
        
        <button 
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-3 p-4 rounded-2xl font-bold transition-all ${activeTab === 'overview' ? 'bg-[#1A56DB] text-white shadow-md' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'}`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
          Genel Bakış
        </button>
        <button 
          onClick={() => setActiveTab('clinics')}
          className={`flex items-center gap-3 p-4 rounded-2xl font-bold transition-all ${activeTab === 'clinics' ? 'bg-[#1A56DB] text-white shadow-md' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'}`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
          Poliklinikler
        </button>
        <button 
          onClick={() => setActiveTab('doctors')}
          className={`flex items-center gap-3 p-4 rounded-2xl font-bold transition-all ${activeTab === 'doctors' ? 'bg-[#1A56DB] text-white shadow-md' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'}`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
          Doktor İşlemleri
        </button>
        <button 
          onClick={() => setActiveTab('appointments')}
          className={`flex items-center gap-3 p-4 rounded-2xl font-bold transition-all ${activeTab === 'appointments' ? 'bg-[#1A56DB] text-white shadow-md' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'}`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          Sistem Randevuları
        </button>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col gap-6">
        {/* Başarı Mesajı */}
        {successMsg && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-5 py-4 rounded-2xl mb-2 font-bold animate-fade-in flex items-center gap-3 shadow-sm">
            <div className="bg-emerald-100 text-emerald-600 p-1.5 rounded-full">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
            </div>
            {successMsg}
          </div>
        )}

        {loading ? (
           <div className="flex justify-center items-center py-32">
             <div className="animate-spin w-12 h-12 border-4 border-[#1A56DB] border-t-transparent rounded-full shadow-md"></div>
           </div>
        ) : (
          <>
            {/* OVERVIEW TAB */}
            {activeTab === 'overview' && (
              <>
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 mb-2">
                  <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight">Sistem Özeti</h1>
                  <p className="text-gray-500 font-medium mt-1">Sistemdeki güncel istatistikler ve veriler.</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Stats Cards */}
                  <div className="bg-gradient-to-br from-blue-500 to-[#1A56DB] p-8 rounded-3xl shadow-lg relative overflow-hidden text-white group">
                    <div className="absolute -right-6 -bottom-6 opacity-20 transform group-hover:scale-110 transition-transform duration-500">
                      <span className="text-9xl font-black">👤</span>
                    </div>
                    <p className="text-blue-100 font-bold mb-2 uppercase tracking-wider text-sm">Kayıtlı Hasta</p>
                    <h2 className="text-5xl font-black">{stats.total_patients}</h2>
                  </div>
                  
                  <div className="bg-gradient-to-br from-emerald-400 to-emerald-600 p-8 rounded-3xl shadow-lg relative overflow-hidden text-white group">
                    <div className="absolute -right-6 -bottom-6 opacity-20 transform group-hover:scale-110 transition-transform duration-500">
                      <span className="text-9xl font-black">📅</span>
                    </div>
                    <p className="text-emerald-100 font-bold mb-2 uppercase tracking-wider text-sm">Alınan Randevu</p>
                    <h2 className="text-5xl font-black">{stats.total_appointments}</h2>
                  </div>
                  
                  <div className="bg-gradient-to-br from-purple-500 to-indigo-600 p-8 rounded-3xl shadow-lg relative overflow-hidden text-white group">
                    <div className="absolute -right-6 -bottom-6 opacity-20 transform group-hover:scale-110 transition-transform duration-500">
                      <span className="text-9xl font-black">🩺</span>
                    </div>
                    <p className="text-purple-100 font-bold mb-2 uppercase tracking-wider text-sm">Aktif Doktor</p>
                    <h2 className="text-5xl font-black">{stats.total_doctors}</h2>
                  </div>
                </div>

                <div className="mt-6 bg-white rounded-3xl shadow-sm border border-gray-100 p-8">
                  <h3 className="text-xl font-extrabold text-gray-800 mb-6 flex items-center gap-2">
                    <span className="w-3 h-8 bg-amber-400 rounded-md"></span> En Yüksek Talep Gören Poliklinikler
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {popularClinics.map((pc, idx) => (
                      <div key={idx} className="bg-gray-50 border border-gray-100 p-6 rounded-2xl flex flex-col justify-center shadow-inner">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="bg-amber-100 text-amber-600 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm">#{idx+1}</span>
                          <p className="font-extrabold text-gray-800">{pc.clinic_name}</p>
                        </div>
                        <p className="text-sm font-bold text-gray-500 ml-11">{pc.appointment_count} Toplam Randevu</p>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* CLINICS TAB */}
            {activeTab === 'clinics' && (
              <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
                <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight mb-8 flex items-center gap-3">
                  <span className="w-3 h-8 bg-[#1A56DB] rounded-md"></span> Sistemdeki Poliklinikler
                </h1>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="text-gray-400 text-sm uppercase tracking-wider border-b-2 border-gray-100">
                        <th className="pb-4 font-bold">Klinik Adı / Branş</th>
                        <th className="pb-4 font-bold">İl</th>
                        <th className="pb-4 font-bold">İlçe</th>
                        <th className="pb-4 font-bold">Bağlı Hastane</th>
                      </tr>
                    </thead>
                    <tbody className="text-gray-700 font-medium">
                      {clinics.map(c => (
                        <tr key={c.id} className="border-b border-gray-50 hover:bg-blue-50/30 transition-colors">
                          <td className="py-5 font-bold text-gray-900">{c.name}</td>
                          <td className="py-5">{c.city}</td>
                          <td className="py-5">{c.district}</td>
                          <td className="py-5 text-gray-500 text-sm">Merkez Hastanesi</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* DOCTORS TAB */}
            {activeTab === 'doctors' && (
              <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
                  <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight flex items-center gap-3">
                    <span className="w-3 h-8 bg-[#1A56DB] rounded-md"></span> Doktor Veritabanı
                  </h1>
                  <button 
                    onClick={() => setShowModal(true)}
                    className="bg-[#1A56DB] hover:bg-blue-800 text-white font-bold py-3.5 px-6 rounded-xl shadow-md transition-transform transform active:scale-95 flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                    Yeni Doktor Ekle
                  </button>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {doctors.map(d => (
                    <div key={d.id} className="border border-gray-100 p-5 rounded-2xl shadow-sm hover:shadow-md transition-shadow bg-gray-50 flex items-start gap-4">
                       <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-xl flex-shrink-0">
                         {d.name.charAt(0)}
                       </div>
                       <div>
                         <h3 className="font-extrabold text-gray-800">{d.title} {d.name}</h3>
                         <p className="text-[#1A56DB] text-sm font-bold mb-2">{d.specialization}</p>
                         <div className="text-xs font-semibold text-gray-500 bg-white px-2 py-1 rounded-md inline-block border border-gray-200">
                           {d.clinic?.name || 'Klinik Atanmamış'}
                         </div>
                       </div>
                    </div>
                  ))}
                  {doctors.length === 0 && (
                    <div className="col-span-full p-8 text-center text-gray-500 font-medium">Sistemde henüz doktor bulunmuyor.</div>
                  )}
                </div>
              </div>
            )}

            {/* APPOINTMENTS TAB */}
            {activeTab === 'appointments' && (
              <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
                <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight mb-8 flex items-center gap-3">
                  <span className="w-3 h-8 bg-[#1A56DB] rounded-md"></span> Sistem Randevuları
                </h1>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="text-gray-400 text-sm uppercase tracking-wider border-b-2 border-gray-100">
                        <th className="pb-4 font-bold">Randevu Zamanı</th>
                        <th className="pb-4 font-bold">Hasta Adı</th>
                        <th className="pb-4 font-bold">Doktor Adı</th>
                        <th className="pb-4 font-bold">Durum</th>
                      </tr>
                    </thead>
                    <tbody className="text-gray-700 font-medium">
                      {appointments.map(a => {
                        const dateObj = new Date(a.appointment_datetime);
                        const dateStr = dateObj.toLocaleDateString('tr-TR');
                        const timeStr = dateObj.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
                        return (
                        <tr key={a.id} className="border-b border-gray-50 hover:bg-blue-50/30 transition-colors">
                          <td className="py-4 font-bold">{dateStr} <span className="text-[#1A56DB] ml-1">{timeStr}</span></td>
                          <td className="py-4 font-bold text-gray-900">{a.patient_name || `Hasta #${a.patient_id}`}</td>
                          <td className="py-4 font-bold text-gray-900">Dr. {a.assoc_doctor_name || (a.doctor && a.doctor.name) || 'Bilinmiyor'}</td>
                          <td className="py-4">
                             <span className={`px-3 py-1 rounded-full text-xs font-bold ${a.status === 'completed' ? 'bg-green-100 text-green-700' : a.status === 'cancelled' ? 'bg-red-100 text-red-700' : a.status === 'no_show' ? 'bg-gray-200 text-gray-700' : 'bg-blue-100 text-blue-700'}`}>{a.status}</span>
                          </td>
                        </tr>
                        );
                      })}
                      {appointments.length === 0 && (
                        <tr><td colSpan="4" className="py-8 text-center text-gray-500">Sistemde henüz randevu kaydı yok.</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
      
      {/* Modal is kept outside to render on top */}
      <AddDoctorModal 
        isOpen={showModal} 
        onClose={() => setShowModal(false)} 
        onSuccess={handleSuccess} 
      />
    </div>
  );
}
