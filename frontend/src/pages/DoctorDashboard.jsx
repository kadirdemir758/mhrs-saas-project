import React, { useState, useEffect } from 'react';

export default function DoctorDashboard() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/doctors/me/appointments', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAppointments(data.appointments);
      } else {
        console.error("Failed to fetch appointments");
      }
    } catch (error) {
      console.error("Error fetching appointments:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (id, status) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/appointments/${id}/status`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      });
      
      if (response.ok) {
        setAppointments(prev => prev.map(appt => appt.id === id ? { ...appt, status } : appt));
      } else {
        const err = await response.json();
        alert(`Güncelleme başarısız: ${err.detail || 'Bilinmeyen hata'}`);
      }
    } catch (error) {
      console.error("Error updating status:", error);
      alert("Hata oluştu.");
    }
  };

  const statusMap = {
    pending: { label: "Bekliyor", classes: "bg-blue-100 text-[#1A56DB]" },
    confirmed: { label: "Onaylandı", classes: "bg-purple-100 text-purple-700" },
    completed: { label: "Tamamlandı", classes: "bg-emerald-100 text-emerald-700" },
    no_show: { label: "Gelmedi", classes: "bg-gray-100 text-gray-700" },
    cancelled: { label: "İptal", classes: "bg-red-100 text-red-700" }
  };

  return (
    <div className="animate-fade-in flex flex-col gap-6">
      
      {/* Üst Bilgi Başlığı */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
        <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center text-3xl">👤</div>
        <div>
          <h1 className="text-2xl font-extrabold text-gray-800">Hekim Paneli</h1>
          <p className="text-gray-500 text-sm">Çalışma takviminizi ve hastalarınızı buradan yönetebilirsiniz.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        
        {/* Bugünkü Randevularım */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-md border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <span className="w-3 h-8 bg-[#1A56DB] rounded-md"></span>
            Bugünkü Randevularım
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 text-gray-500 text-sm uppercase tracking-wide border-b border-gray-200">
                  <th className="p-4 font-bold rounded-tl-xl whitespace-nowrap">Saat</th>
                  <th className="p-4 font-bold whitespace-nowrap">Hasta Adı</th>
                  <th className="p-4 font-bold whitespace-nowrap">Şikayet</th>
                  <th className="p-4 font-bold whitespace-nowrap">Durum</th>
                  <th className="p-4 font-bold rounded-tr-xl whitespace-nowrap">İşlem</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="5" className="p-4 text-center text-gray-500 font-medium">Yükleniyor...</td>
                  </tr>
                ) : appointments.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="p-4 text-center text-gray-500 font-medium">Bugün için randevunuz bulunmamaktadır.</td>
                  </tr>
                ) : (
                  appointments.map((appt) => {
                    const timeStr = new Date(appt.appointment_datetime).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
                    const statusInfo = statusMap[appt.status] || { label: appt.status, classes: "bg-gray-100 text-gray-600" };
                    return (
                      <tr key={appt.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="p-4 font-bold text-gray-700">{timeStr}</td>
                        <td className="p-4 font-semibold text-gray-800">{appt.patient_name || 'Bilinmiyor'}</td>
                        <td className="p-4 text-gray-500 text-sm">{appt.complaint || 'Belirtilmedi'}</td>
                        <td className="p-4">
                          <span className={`${statusInfo.classes} px-3 py-1 rounded-full text-xs font-bold inline-block`}>
                            {statusInfo.label}
                          </span>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <button 
                              onClick={() => handleUpdateStatus(appt.id, 'completed')}
                              disabled={appt.status === 'completed' || appt.status === 'cancelled'}
                              className="bg-emerald-100 hover:bg-emerald-200 text-emerald-700 font-bold py-1.5 px-3 rounded-xl text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                              title="Tamamlandı Olarak İşaretle"
                            >
                              ✅ Tamamlandı
                            </button>
                            <button 
                              onClick={() => handleUpdateStatus(appt.id, 'no_show')}
                              disabled={appt.status === 'no_show' || appt.status === 'cancelled' || appt.status === 'completed'}
                              className="bg-red-100 hover:bg-red-200 text-red-700 font-bold py-1.5 px-3 rounded-xl text-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                              title="Tıklandığında Gelmedi Olarak İşaretle"
                            >
                              ❌ Gelmedi
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
          <div className="mt-6 text-center">
            <button className="text-[#1A56DB] font-bold text-sm hover:underline">Tüm Randevuları Gör &rarr;</button>
          </div>
        </div>

        {/* Hasta Geçmişi Sorgula */}
        <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <span className="w-3 h-8 bg-emerald-500 rounded-md"></span>
            Hasta Geçmişi Sorgula
          </h2>
          <div className="mb-4">
            <label className="block text-gray-700 font-bold mb-2 text-sm">T.C. Kimlik / Dosya No</label>
            <input 
              type="text" 
              placeholder="11 Haneli TC Kimlik No" 
              className="w-full p-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-emerald-100 outline-none transition-all"
            />
          </div>
          <button className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3.5 rounded-xl shadow-md transition-all flex justify-center items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            Sorgula
          </button>
          
          <div className="mt-8 p-4 bg-gray-50 rounded-xl border border-gray-100 text-center text-sm text-gray-500">
            Hasta bilgilerine erişmek için T.C. Kimlik numarası ile arama yapınız. Randevusu olmayan hastaların dosyaları görüntülenmez.
          </div>
        </div>

      </div>
    </div>
  );
}
