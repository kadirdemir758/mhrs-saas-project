import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import SymptomAnalyzer from '../components/SymptomAnalyzer';
import AppointmentStepper from '../components/AppointmentStepper';
import DoctorDashboard from './DoctorDashboard';
import AdminDashboard from './AdminDashboard';

export default function Home() {
  const token = localStorage.getItem('token');
  const [isLoggedIn] = useState(!!token);
  const [role] = useState(() => {
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.role || 'patient';
      } catch (e) {
        return 'patient';
      }
    }
    return null;
  });

  if (isLoggedIn && role === 'doctor') {
    return <DoctorDashboard />;
  }

  if (isLoggedIn && role === 'admin') {
    return <AdminDashboard />;
  }

  return (
    <>
      {/* Giriş Portalları (Sadece Giriş Yapılmamışsa) */}
      {!isLoggedIn && (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-14">
        <Link to="/login?role=patient" className="bg-white hover:bg-blue-50 border-2 border-transparent hover:border-[#1A56DB] p-8 rounded-3xl shadow-lg transition-all transform hover:-translate-y-2 text-center group">
          <div className="w-20 h-20 bg-blue-100 text-[#1A56DB] rounded-full flex items-center justify-center mx-auto mb-4 text-4xl group-hover:scale-110 transition-transform">🩺</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Hasta Girişi</h3>
          <p className="text-sm text-gray-500">Randevu alın, tahlil sonuçlarınıza bakın.</p>
        </Link>
        <Link to="/login?role=doctor" className="bg-white hover:bg-emerald-50 border-2 border-transparent hover:border-emerald-500 p-8 rounded-3xl shadow-lg transition-all transform hover:-translate-y-2 text-center group">
          <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl group-hover:scale-110 transition-transform">👤</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Hekim Girişi</h3>
          <p className="text-sm text-gray-500">Çalışma takviminizi ve hastalarınızı yönetin.</p>
        </Link>
        <Link to="/login?role=admin" className="bg-white hover:bg-purple-50 border-2 border-transparent hover:border-purple-500 p-8 rounded-3xl shadow-lg transition-all transform hover:-translate-y-2 text-center group">
          <div className="w-20 h-20 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl group-hover:scale-110 transition-transform">⚙️</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Yönetici Girişi</h3>
          <p className="text-sm text-gray-500">Sistem ayarlarını ve yetkileri düzenleyin.</p>
        </Link>
      </div>
      )}

      {(!isLoggedIn || role === 'patient') && (
        <>
          {/* Akıllı Asistan (Symptom Analyzer) */}
          <section className="mb-14">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
              <SymptomAnalyzer />
            </div>
          </section>

      {/* Randevu Modülü (Stepper) */}
      <section className="bg-white rounded-2xl shadow-xl p-6 lg:p-10 border border-gray-100 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-4 -mr-4 w-32 h-32 bg-blue-50 rounded-full opacity-50 pointer-events-none"></div>
        
        <div className="mb-8 border-b border-gray-100 pb-5">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-800 flex items-center">
            <span className="bg-[#1A56DB] w-2 h-8 rounded shrink-0 mr-3"></span>
            Randevu Oluştur
          </h2>
        </div>
        
        <AppointmentStepper />
      </section>
        </>
      )}
    </>
  );
}
