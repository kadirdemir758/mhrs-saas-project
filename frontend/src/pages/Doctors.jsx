import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function Doctors() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Debounce (Sunucuyu Aşırı Yüklenmeden Koruyan Geciktirme) Motoru
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const limit = 12;

  const navigate = useNavigate();

  // Search Debounce Engine
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setPage(1); // Yeni bir şey aranınca hep 1. sayfadan başlat
    }, 500);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  // Fetch Logic (API İsteği)
  useEffect(() => {
    const fetchDoctors = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      setLoading(true);
      try {
        const skip = (page - 1) * limit;
        const res = await api.get(`/doctors/?skip=${skip}&limit=${limit}&search=${debouncedSearch}`);
        setDoctors(res.data.doctors || []);
        setTotalCount(res.data.total || 0);
      } catch (err) {
        if (err.response?.status === 401 || err.response?.status === 403) {
          navigate('/login');
        } else {
          console.error("Doktor verileri çekilemedi:", err);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchDoctors();
  }, [page, debouncedSearch, navigate]);

  const totalPages = Math.ceil(totalCount / limit) || 1;

  // Randevu Al Tuşu Yönlendirmesi
  const handleAppointmentClick = () => {
    navigate('/new-appointment');
  };

  // Modern Doktor Profil Kartı Modülü
  const renderCard = (doctor) => (
    <div key={doctor.id} className="bg-white border border-gray-100 rounded-3xl p-6 shadow-md hover:shadow-2xl transition-all group flex flex-col justify-between h-full">
         <div>
            <div className="flex items-center gap-4 mb-5">
               <div className="w-16 h-16 rounded-full bg-blue-50 text-[#1A56DB] flex items-center justify-center text-2xl font-bold shadow-inner flex-shrink-0">
                 {doctor.name.charAt(0)}
               </div>
               <div>
                  <h3 className="text-xl font-extrabold text-gray-800 line-clamp-1" title={doctor.name}>{doctor.title} {doctor.name}</h3>
                  <p className="text-[#1A56DB] font-semibold text-sm line-clamp-1">{doctor.specialization}</p>
               </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100 mb-4">
                <p className="text-sm font-bold text-gray-700 truncate" title={doctor.clinic ? doctor.clinic.name : 'Genel Poliklinik'}>
                  {doctor.clinic ? doctor.clinic.name : 'Genel Poliklinik'}
                </p>
                <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                     <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                     {doctor.clinic ? `${doctor.clinic.city} - ${doctor.clinic.district}` : 'Türkiye'}
                </p>
                <div className="border-t border-gray-200 my-2"></div>
                
                {/* Seed dosyanızdan yansıtılan Çalışma Saatleri ve Diller */}
                <div className="flex items-center justify-between text-xs font-semibold text-gray-400 mt-2">
                   <span>Çalışma Saatleri:</span>
                   <span className="text-gray-700 bg-white px-2 py-1 rounded-md shadow-sm border border-gray-100">{doctor.working_hours || '09:00 - 17:00'}</span>
                </div>
                <div className="flex items-center justify-between text-xs font-semibold text-gray-400 mt-2">
                   <span>Yabancı Dil:</span>
                   <span className="text-gray-700">{doctor.languages || 'Türkçe'}</span>
                </div>
            </div>
         </div>
         
         <button onClick={handleAppointmentClick} className="w-full bg-[#1A56DB] hover:bg-blue-800 text-white font-bold py-3 rounded-xl shadow-md transition-colors mt-auto">
            Randevu Al
         </button>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto py-10 px-4 animate-fade-in relative z-10 min-h-screen flex flex-col">
      <div className="mb-10 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-800 tracking-tight">Hekimlerimiz</h1>
        <p className="text-gray-500 font-medium mt-3 max-w-2xl mx-auto">
          Türkiye çapında görev yapan binlerce uzman hekimimiz arasında arama yapın, size en uygun uzmanı saniyeler içerisinde bulun.
        </p>
      </div>

      {/* Modern Arama Çubuğu (Search Bar) */}
      <div className="max-w-3xl mx-auto w-full mb-12 relative">
          <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
            <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input 
            type="text" 
            className="w-full bg-white text-lg pl-14 pr-6 py-5 rounded-full border-2 border-gray-100 shadow-xl focus:outline-none focus:border-[#1A56DB] focus:ring-4 focus:ring-blue-50 transition-all font-medium text-gray-800 placeholder-gray-400"
            placeholder="Doktor adı veya Uzmanlık alanına göre arama yapın (Örn: Kardiyoloji, Ayşe...)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
      </div>

      {/* Doktor Grid */}
      <div className="flex-grow">
          {loading ? (
             <div className="flex justify-center items-center py-32">
                 <div className="animate-spin w-12 h-12 border-4 border-[#1A56DB] border-t-transparent rounded-full shadow-md"></div>
             </div>
          ) : doctors.length > 0 ? (
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                 {doctors.map(renderCard)}
             </div>
          ) : (
             <div className="text-center p-16 bg-white rounded-3xl shadow-sm border border-dashed border-gray-300 max-w-2xl mx-auto">
                 <svg className="w-20 h-20 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                 <h3 className="text-2xl font-bold text-gray-800 mb-2">Hekim Bulunamadı</h3>
                 <p className="text-lg text-gray-500 font-medium">Böyle bir kelimeyle eşleşen uzmanlık veya hekim kaydı sistemimizde yok. Lütfen farklı kelimelerle tekrar deneyin.</p>
             </div>
          )}
      </div>

      {/* Pagination (Sayfalama Modülü) */}
      {!loading && totalCount > 0 && (
         <div className="mt-16 mb-8 flex flex-col sm:flex-row justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
             <span className="text-sm font-bold text-gray-500 mb-4 sm:mb-0">
                 Toplam <span className="text-[#1A56DB] text-lg mx-1">{totalCount}</span> hekim bulundu.
             </span>
             
             <div className="flex items-center gap-3">
                 <button 
                     onClick={() => setPage(p => Math.max(1, p - 1))}
                     disabled={page === 1}
                     className="px-6 py-2.5 rounded-xl font-bold text-sm bg-gray-50 border border-gray-200 text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                 >
                     ← Önceki Sayfa
                 </button>
                 
                 <div className="px-4 py-2 rounded-xl bg-blue-50 text-[#1A56DB] font-extrabold shadow-inner min-w-[3rem] text-center border border-blue-100">
                     {page} / {totalPages}
                 </div>
                 
                 <button 
                     onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                     disabled={page >= totalPages}
                     className="px-6 py-2.5 rounded-xl font-bold text-sm bg-gray-50 border border-gray-200 text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                 >
                     Sonraki Sayfa →
                 </button>
             </div>
         </div>
      )}
    </div>
  );
}
