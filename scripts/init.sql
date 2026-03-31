-- ════════════════════════════════════════════════════════════════════
-- MHRS SaaS — Initial Database Seed (runs on container first start)
-- ════════════════════════════════════════════════════════════════════

-- Ensure we're working on the right DB
USE mhrs_db;

-- ── Seed Clinics ──────────────────────────────────────────────────────────────
INSERT INTO clinics (name, city, district, clinic_type, address, phone, is_active)
VALUES
  ('Istanbul Kalp Hastanesi',    'Istanbul',  'Sisli',      'cardiology',       'Halaskargazi Cad. No:38',      '+90-212-555-1001', 1),
  ('Ankara Beyin Merkezi',       'Ankara',    'Cankaya',    'neurology',        'Ataturk Bulvari No:125',       '+90-312-555-2001', 1),
  ('Izmir Göz Kliniği',         'Izmir',     'Konak',      'ophthalmology',    'Cumhuriyet Bulvari No:67',     '+90-232-555-3001', 1),
  ('Bursa Ortopedi Merkezi',     'Bursa',     'Osmangazi',  'orthopedics',      'Hamitler Mah. No:15',          '+90-224-555-4001', 1),
  ('Istanbul Sindirim Kliniği', 'Istanbul',  'Kadikoy',    'gastroenterology', 'Moda Cad. No:12',              '+90-216-555-5001', 1),
  ('Genel Sağlık Polikliniği',  'Istanbul',  'Uskudar',    'general_practice', 'Baglarbaşi Mah. No:5',         '+90-216-555-6001', 1),
  ('Ankara Deri Merkezi',        'Ankara',    'Yenimahalle','dermatology',      'Konya Yolu No:88',             '+90-312-555-7001', 1),
  ('Izmir Akciğer Kliniği',     'Izmir',     'Bornova',    'pulmonology',      'Fevzi Cakmak Cad. No:44',      '+90-232-555-8001', 1),
  ('Istanbul KBB Merkezi',       'Istanbul',  'Fatih',      'ent',              'Divanyolu Cad. No:22',         '+90-212-555-9001', 1),
  ('Ankara Endokrin Merkezi',    'Ankara',    'Kecioren',  'endocrinology',    'Atatürk Mah. No:3',            '+90-312-555-1101', 1);

-- ── Seed Doctors ─────────────────────────────────────────────────────────────
INSERT INTO doctors (name, title, specialization, clinic_id, rating, total_ratings, working_hours, is_active)
VALUES
  ('Ahmet Yılmaz',   'Prof. Dr.', 'Cardiology',             1, 4.8, 120, 'Mon-Fri 09:00-17:00', 1),
  ('Fatma Kaya',     'Doç. Dr.', 'Cardiology',             1, 4.6, 85,  'Mon-Wed 09:00-15:00', 1),
  ('Mehmet Demir',   'Dr.',      'Neurology',              2, 4.7, 200, 'Mon-Fri 08:00-16:00', 1),
  ('Ayşe Çelik',    'Prof. Dr.', 'Ophthalmology',          3, 4.9, 310, 'Tue-Sat 10:00-18:00', 1),
  ('Ali Arslan',     'Dr.',      'Orthopedics',            4, 4.5, 90,  'Mon-Fri 09:00-17:00', 1),
  ('Zeynep Şahin',  'Doç. Dr.', 'Gastroenterology',       5, 4.6, 150, 'Mon-Thu 09:00-17:00', 1),
  ('Hasan Bozkurt',  'Dr.',      'General Practice',       6, 4.4, 210, 'Mon-Sat 08:00-20:00', 1),
  ('Selin Yıldız',  'Dr.',      'Dermatology',            7, 4.7, 175, 'Mon-Fri 09:00-17:00', 1),
  ('Kemal Güneş',   'Prof. Dr.', 'Pulmonology',            8, 4.8, 140, 'Tue-Fri 09:00-17:00', 1),
  ('Rabia Erdoğan', 'Doç. Dr.', 'ENT (Ear, Nose, Throat)', 9, 4.5, 130, 'Mon-Fri 09:00-17:00', 1);
