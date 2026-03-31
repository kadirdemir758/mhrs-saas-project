import React, { useState } from 'react';
import api from '../api';

export default function SymptomAnalyzer() {
  const [symptom, setSymptom] = useState('');
  const [suggestion, setSuggestion] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (symptom.trim().length < 3) return;
    
    setLoading(true);
    try {
      const res = await api.post('/analyze', { symptom_text: symptom });
      setSuggestion(res.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Sol Panel: Şikayet Girişi */}
      <div className="bg-white p-6 md:p-8 rounded-2xl shadow-lg border border-gray-100 flex flex-col h-full transform transition-all duration-300 hover:shadow-xl">
        <div className="flex items-center mb-6">
          <div className="w-10 h-10 rounded-full bg-blue-50 text-[#1A56DB] flex items-center justify-center mr-4 shadow-sm">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <h2 className="text-xl md:text-2xl font-bold text-gray-800">Akıllı Şikayet Asistanı</h2>
        </div>
        <p className="text-gray-500 text-sm md:text-base mb-6 leading-relaxed">
          Şikayetlerinizi kısaca yazın, yapay zeka destekli sistemimiz size en uygun polikliniği anında önersin.
        </p>
        
        <form onSubmit={handleAnalyze} className="flex-1 flex flex-col">
          <textarea
            className="w-full flex-1 min-h-[140px] p-4 bg-gray-50 border border-gray-200 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-[#1A56DB] focus:bg-white outline-none resize-none transition-all text-gray-700 placeholder-gray-400"
            placeholder="Örn: Dünden beri şiddetli baş ağrım var ve bulanık görüyorum..."
            value={symptom}
            onChange={(e) => setSymptom(e.target.value)}
          ></textarea>
          <button 
            type="submit" 
            disabled={loading || symptom.trim().length < 3}
            className="mt-6 w-full bg-[#1A56DB] hover:bg-blue-800 disabled:bg-blue-300 disabled:cursor-not-allowed text-white font-bold py-3.5 px-4 rounded-xl transition-all shadow-md hover:shadow-lg flex justify-center items-center gap-2 transform active:scale-95"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : null}
            {loading ? 'Analiz Ediliyor...' : 'Hangi Polikliniğe Gitmeliyim?'}
          </button>
        </form>
      </div>

      {/* Sağ Panel: Analiz Sonucu */}
      <div className={`p-6 md:p-8 rounded-2xl shadow-lg border flex flex-col justify-center items-center text-center transition-all duration-500 h-full ${suggestion ? 'bg-blue-50/50 border-blue-200' : 'bg-white border-gray-100 hover:shadow-xl'}`}>
        {!suggestion ? (
          <div className="text-gray-400 flex flex-col items-center">
            <svg className="w-20 h-20 mb-6 opacity-30" fill="none" stroke="currentColor" strokeWidth="1" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
            <p className="text-lg font-medium text-gray-500">Analiz sonucu burada görüntülenecek.</p>
            <p className="text-sm mt-2 max-w-xs">Sol taraftaki asistanı kullanarak hemen test edebilirsiniz.</p>
          </div>
        ) : (
          <div className="animate-fade-in w-full">
            <div className="inline-block px-4 py-1.5 rounded-full bg-green-100 text-green-700 text-xs font-bold uppercase tracking-wider mb-6">
              Eşleşme Bulundu
            </div>
            <h3 className="text-3xl md:text-5xl font-extrabold text-[#1A56DB] mb-6">{suggestion.recommended_clinic}</h3>
            <div className="p-5 bg-white rounded-xl shadow-sm border border-blue-100 text-gray-700 text-left relative">
              <div className="absolute top-0 right-0 -mt-2 -mr-2 bg-yellow-100 text-yellow-800 text-[10px] font-bold px-2 py-1 rounded-full shadow-sm">AI</div>
              <p className="flex items-start text-sm md:text-base leading-relaxed mt-2">
                <span className="text-blue-500 mr-3 mt-0.5"><svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"></path></svg></span>
                {suggestion.description}
              </p>
            </div>
            <button 
              className="mt-8 font-semibold text-[#1A56DB] hover:text-blue-800 transition-colors inline-flex items-center group"
              onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })}
            >
              Randevu Oluştur
              <svg className="w-5 h-5 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
            </button>
          </div>
        )}
      </div>
    </>
  );
}
