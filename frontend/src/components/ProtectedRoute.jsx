import React, { useState, useEffect } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';

const ProtectedRoute = ({ children, requiredRole }) => {
  const token = localStorage.getItem('token');
  const navigate = useNavigate();
  const [redirect, setRedirect] = useState(false);
  
  // Senkron rol kontrolü (Component render edilmeden önce yapılır ki içerik hiç gözükmesin)
  let role = 'patient';
  let isAuthorized = false;

  if (token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));

      const payload = JSON.parse(jsonPayload);
      role = payload.role || 'patient';
      
      if (!requiredRole || role === requiredRole) {
        isAuthorized = true;
      }
    } catch (error) {
      console.error("Token çözme hatası:", error);
    }
  }

  useEffect(() => {
    if (token && !isAuthorized) {
      const timer = setTimeout(() => {
        setRedirect(true);
      }, 3000);
      return () => clearTimeout(timer);
    }
    if (!token) {
      navigate('/login', { replace: true });
    }
  }, [token, isAuthorized, navigate]);
  
  if (!token) {
    return null; // let useEffect redirect
  }
  
  if (!isAuthorized) {
    if (redirect) {
      return <Navigate to="/" replace />;
    }
    return (
      <div className="flex items-center justify-center min-h-[60vh] animate-fade-in px-4">
        <div className="bg-white border text-center p-12 max-w-lg rounded-3xl shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-3 bg-red-500"></div>
          <div className="w-24 h-24 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm border-4 border-white ring-4 ring-red-50">
            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          </div>
          <h2 className="text-3xl font-black text-gray-800 mb-4">Yetkisiz Erişim!</h2>
          <p className="text-gray-600 font-medium mb-8 text-lg">Bu sayfaya giriş yetkiniz bulunmamaktadır.</p>
          <div className="inline-block px-4 py-2 bg-red-50 text-red-600 rounded-full text-sm font-bold animate-pulse border border-red-100">
            Ana sayfaya yönlendiriliyorsunuz...
          </div>
        </div>
      </div>
    );
  }
  
  return children;
};

export default ProtectedRoute;
