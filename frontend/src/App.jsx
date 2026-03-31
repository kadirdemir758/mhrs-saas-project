import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Appointments from './pages/Appointments';
import MyAppointments from './pages/MyAppointments';
import Doctors from './pages/Doctors';
import Verify from './pages/Verify';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Profile from './pages/Profile';
import DoctorDashboard from './pages/DoctorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 text-gray-800 font-sans flex flex-col">
        {/* Üst Menü her sayfada sabit kalır */}
        <Navbar />

        {/* Ana İçerik Rotası */}
        <main className="flex-1 container mx-auto px-4 py-8 lg:py-12 max-w-7xl">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify" element={<Verify />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/new-appointment" element={<Appointments />} />
            <Route path="/appointments" element={<MyAppointments />} />
            <Route path="/doctors" element={<Doctors />} />
            
            {/* Protected Role-Based Routes */}
            <Route path="/doctor-dashboard" element={
              <ProtectedRoute requiredRole="doctor">
                <DoctorDashboard />
              </ProtectedRoute>
            } />
            <Route path="/admin-dashboard" element={
              <ProtectedRoute requiredRole="admin">
                <AdminDashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </main>

        {/* Footer her sayfada sabit kalır */}
        <footer className="bg-slate-900 text-slate-300 py-8 text-center border-t-4 border-[#1A56DB] mt-auto">
          <div className="container mx-auto px-4">
            <p className="font-semibold text-white mb-2">MHRS SaaS Platformu © 2026</p>
            <p className="text-sm opacity-75">Sağlıklı ve mutlu günler dileriz.</p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
