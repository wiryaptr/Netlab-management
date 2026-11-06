# NetLab Manager — Security

**Versi:** 1.2 (SD-01 s.d. SD-08 diputuskan; pengecualian patch keamanan dirujuk; belum divalidasi)
**Tanggal:** 26 Oktober 2026
**Sumber:** `prd.md` §8–9, `design.md` §11, `spec.md` v1.3 §5, §11, §13, `docs/DATA_MODEL.md` v1.2, `docs/RBAC_MATRIX.md`
**Status:** Dokumentasi saja. Tidak ada kontrol di bawah yang sudah diimplementasikan atau diuji, kecuali yang disebut eksplisit pada bagian 12.

Penanda **SD-xx** menunjuk keputusan dokumen ini; statusnya ada di bagian 13. Dokumen ini merangkum dan merinci kontrol yang sudah ada di dokumen lain; bila bertentangan, dokumen utama menang.

## 1. Ruang lingkup

Aplikasi web internal satu laboratorium. Aset yang dilindungi: integritas data inventaris/IPAM, audit log, kredensial pengguna, dan secret konfigurasi. Di luar cakupan MVP: akses ke perangkat jaringan (ADR-008), penyimpanan credential perangkat, dan multi-tenant.

## 2. Ancaman dan kontrol

| Ancaman | Kontrol | Rujukan |
| --- | --- | --- |
| Tebak/curi password (credential stuffing) | Throttle login per IP dan per username; pesan login gagal seragam; validator kekuatan password | spec §5; API AP-10; 3 |
| Pembajakan sesi | Cookie `HttpOnly`, `Secure`, `SameSite`; HTTPS; logout mengakhiri sesi server-side | 3, 8 |
| CSRF | Token `X-CSRFToken` pada semua request pengubah state; satu origin | API 2; spec §4 |
| Eskalasi hak / IDOR | Otorisasi di backend per endpoint dan objek; deny-by-default; uji lintas peran lewat API langsung | RBAC |
| SQL injection | Hanya ORM dan query berparameter; role runtime berhak minimum | 7 |
| XSS | React menghindari injeksi HTML; tanpa `dangerouslySetInnerHTML`; CSP; tidak ada konten HTML dari pengguna | 8 |
| CSV berbahaya atau berlebihan | Batas ukuran dan baris; UTF-8; sel berawalan `=`, `+`, `-`, `@` dianggap teks; file tidak disimpan | API 7.2, 9 |
| Perusakan audit | Trigger append-only; role runtime tanpa `UPDATE`/`DELETE`/`TRUNCATE` pada audit; tidak ada endpoint tulis | DATA_MODEL 5.11, 8.7 |
| Kebocoran secret lewat log | Daftar larangan log dan redaksi | 6 |
| Race condition merusak integritas | Constraint, trigger penjaga, kunci baris | DATA_MODEL 6.5, 8.5 |
| Dependency berbahaya | Pin eksak, umur rilis minimal, lockfile, pemindaian | VERSIONS; 10 |
| Kebocoran backup | Akses terbatas dan enkripsi | 9; DEPLOYMENT 8 |
| DBA/pemilik skema menyalahgunakan akses | Tidak dapat dicegah di database; dibatasi lewat pemisahan role dan akses server | DATA_MODEL R-01 |

## 3. Autentikasi, sesi, dan password

1. Django session dengan penyimpanan database (DATA_MODEL bagian 10); tidak ada token bearer pada MVP (ADR-005).
2. Cookie sesi: `HttpOnly`, `Secure` (HTTPS), `SameSite=Lax` (SD-03). Cookie CSRF mengikuti pengaturan yang sama; token juga dikembalikan di body `GET /auth/csrf/` dan disimpan di memori aplikasi, bukan local storage.
3. Masa sesi: 8 jam absolut tanpa batas idle (SD-01, disetujui). Logout dan kedaluwarsa sesi wajib diuji.
4. Password: validator Django `UserAttributeSimilarityValidator`, `MinimumLengthValidator` dengan panjang minimum 12, `CommonPasswordValidator`, `NumericPasswordValidator` (SD-02). Hasher bawaan Django (PBKDF2-SHA256); Argon2 tidak diwajibkan.
5. Login gagal selalu `401 invalid_credentials` tanpa membedakan penyebab. Akun nonaktif ditolak.
6. `must_change_password`: password sementara wajib diganti sebelum endpoint lain dapat dipakai (RBAC 6.1).
7. Throttle: login 5 percobaan per menit per IP dan per username; ganti/reset password 5 per menit per pengguna; impor 10 per jam per pengguna; tulis 120 per menit; baca 300 per menit (spec §5, dapat dikonfigurasi). `429` menyertakan `Retry-After`.
8. Respons API menyertakan `Cache-Control: no-store`.

## 4. Otorisasi

Mengikuti `docs/RBAC_MATRIX.md`: deny-by-default, permission hanya pada Group, tanpa `delete_*`, penegakan di backend. `is_superuser` hanya untuk bootstrap; Django admin site dinonaktifkan di production karena melewati service dan audit (DATA_MODEL A-12).

## 5. Validasi input dan impor CSV

1. Validasi server-side pada setiap endpoint; frontend hanya membantu pengalaman pengguna.
2. Parameter query tak dikenal ditolak (`invalid_parameter`).
3. Impor CSV: batas default 2 MB dan 1.000 baris, UTF-8, header persis, kolom tak dikenal ditolak, commit atomik dengan validasi ulang, jalur service yang sama dengan API (constraint dan audit identik), file tidak disimpan, audit `import.commit` tanpa isi file.
4. Data uji tidak memakai data sensitif lab nyata tanpa izin (PRD §9).

## 6. Audit dan logging

1. Audit event mencatat aktor, aksi, objek, waktu, dan `safe_metadata`; daftar 43 aksi wajib di DATA_MODEL 4.12; tidak ada retensi atau penghapusan pada MVP (D-24).
2. `safe_metadata` dan log **tidak boleh** memuat: password, token, session ID, cookie, private key, secret, isi file CSV, isi `description`/`body`, dan username yang diketik pada login gagal dengan akun tidak dikenal.
3. Event `auth.*` boleh mencatat alamat IP klien (DATA_MODEL A-11).
4. Log aplikasi dipisah dari audit event dan tidak menyimpan header `Authorization`, `Cookie`, `Set-Cookie`, atau body request autentikasi. Log error tidak mengembalikan traceback ke klien.
5. Retensi log aplikasi: SD-06 (usulan 90 hari).

## 7. Database

1. Dua role: `netlab_owner` (migrasi, backup/restore) dan `netlab_app` (runtime) dengan hak seperti DATA_MODEL 8.7. Aplikasi tidak pernah memakai kredensial owner saat runtime.
2. Trigger append-only dan trigger penjaga integritas (DATA_MODEL 8.5); fungsi `SECURITY DEFINER` memakai `search_path` tetap dan dimiliki owner (DATA_MODEL R-04).
3. Isolation level `READ COMMITTED`; mengubahnya membutuhkan kajian ulang (DATA_MODEL C-11).
4. Port PostgreSQL tidak diekspos di luar jaringan internal Compose. Lalu lintas aplikasi–database tidak dienkripsi TLS di dalam jaringan internal itu (SD-07).
5. Akses DBA/owner dibatasi, dicatat di luar aplikasi, dan ditinjau berkala (R-01).
6. Setiap tabel atau trigger baru memperbarui grant dalam migrasi yang sama.

## 8. Transport dan header

1. HTTPS untuk semua akses lewat jaringan; sumber sertifikat ditentukan di DEPLOYMENT (DP-03).
2. Satu origin: tidak ada CORS dan `CSRF_TRUSTED_ORIGINS`/`ALLOWED_HOSTS` diisi eksplisit.
3. Header yang disetel reverse proxy/aplikasi (SD-04, SD-05): `Strict-Transport-Security` (setelah HTTPS stabil), `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `Content-Security-Policy` ketat (`default-src 'self'`, `object-src 'none'`, `base-uri 'self'`, `frame-ancestors 'none'`), dan pencegahan framing.
4. Aplikasi mengenali HTTPS di balik proxy lewat pengaturan header proxy yang dipercaya (rincian implementasi).

## 9. Secret dan backup

1. Secret hanya lewat environment atau secret store; `.env` tidak masuk Git; `.env.example` hanya berisi nilai contoh non-rahasia.
2. Secret yang ada: `DJANGO_SECRET_KEY`, kredensial dua role database, kredensial bootstrap administrator, kunci enkripsi backup. Mengganti `DJANGO_SECRET_KEY` membatalkan sesi aktif.
3. Backup dibatasi aksesnya dan dienkripsi sesuai risiko (alat dan retensi: DEPLOYMENT DP-04). Berkas backup memuat audit dan hash password, sehingga diperlakukan sebagai data sensitif.
4. Secret scanning pada repository dan riwayatnya (alat ditentukan di Phase 0).

## 10. Rantai pasok

1. Versi dikunci eksak dengan lockfile berhash (`docs/VERSIONS.md`); aturan umur rilis minimal 20 hari dengan pengecualian patch keamanan mendesak yang terdokumentasi (VERSIONS 3.1; VR-06).
2. Pemindaian kerentanan dependency dan secret pada CI. Alat belum dipilih (SD-08); persyaratannya wajib sebelum Phase 0 dinyatakan lolos.
3. Pembaruan keamanan Django 5.2 (dukungan lanjutan sampai April 2028) dan PostgreSQL 16 dipantau; minor PostgreSQL diterapkan dengan backup sebelumnya.

## 11. Operasional

1. **Bootstrap administrator:** akun pertama dibuat satu kali lewat prosedur terkontrol (superuser darurat), lalu administrator berbasis Group dibuat; password awal wajib diganti. Prosedur rinci di DEPLOYMENT 5.
2. Admin site Django dinonaktifkan di production.
3. Jangan menjalankan perintah ad hoc yang menulis data lewat shell; semua penulisan lewat service layer agar audit tidak terlewat.
4. Insiden keamanan: bekukan akses akun terdampak (`is_active = false`), ganti secret relevan, periksa audit dan log server; prosedur formal di luar cakupan MVP.

## 12. Status validasi

| Kontrol | Status |
| --- | --- |
| Constraint dan trigger append-only pada skema contoh; hak role runtime (ditolak `DELETE`, `TRUNCATE`, `DISABLE TRIGGER`, `UPDATE` audit) | Diuji pada PostgreSQL 16.15 di sandbox dan diuji ulang pada DDL terbaru setelah penggantian nama `vlan_number` (28 Oktober 2026; DATA_MODEL 16.7) |
| Pemetaan nama constraint ke error melalui ORM Django; `DELETE` ditolak untuk role runtime | Diuji pada spike sekali pakai (Django 5.2.18 dan 6.1.2) |
| Pemindaian kerentanan dependency | `npm audit` pada scaffold toolchain frontend: 0 kerentanan (informatif, bukan pemindaian proyek); dependency backend dan pemindaian secret belum dijalankan |
| Seluruh kontrol lain di dokumen ini | **Belum diimplementasikan dan belum diuji** |

## 13. Keputusan dan statusnya

Status per 26 Oktober 2026: SD-01 disetujui; SD-02 s.d. SD-08 default diterima.

| ID | Keputusan | Status dan syarat |
| --- | --- | --- |
| SD-01 | Masa sesi 8 jam absolut tanpa batas idle. | Disetujui sebagai baseline; uji logout dan kedaluwarsa sesi. |
| SD-02 | Panjang minimum password 12 karakter dan keempat validator bawaan Django; hasher bawaan. | Default diterima. |
| SD-03 | `SameSite=Lax` untuk cookie sesi dan CSRF. | Default diterima. |
| SD-04 | HSTS diaktifkan setelah HTTPS stabil; nilai dan cakupan ditentukan di DEPLOYMENT. | Default diterima; bergantung pada jalur sertifikat DP-03 yang masih bersyarat. |
| SD-05 | CSP ketat seperti 8.3. | Default diterima sebagai target; wajib diuji terhadap hasil build Vite. |
| SD-06 | Retensi log aplikasi 90 hari (audit tetap di database tanpa batas). | Default diterima. |
| SD-07 | Tanpa TLS antara aplikasi dan database di dalam jaringan internal Compose. | Default diterima selama database satu host dengan aplikasi; bila dipindah host, TLS wajib dikaji ulang. |
| SD-08 | Alat pemindaian dependency dan secret dipilih pada Phase 0. | Default diterima; persyaratan pemindaian tetap wajib. |

## 14. Daftar uji keamanan (diwajibkan spec §13)

1. Uji akses lintas peran dan tanpa login (RBAC bagian 8).
2. Uji perilaku CSRF dan sesi, termasuk akun nonaktif dan `must_change_password`.
3. Uji input tidak valid dan akses objek yang tidak berhak.
4. Uji rate limiting login.
5. Uji hak akses role runtime dan trigger append-only terhadap database sesungguhnya.
6. Uji race condition dengan transaksi paralel (DATA_MODEL 16.4 sebagai acuan).
7. Pemindaian kerentanan dependency dan secret.
8. Verifikasi tidak ada secret pada log atau respons error.

## 15. Catatan revisi

**1.2:** merujuk prosedur pengecualian patch keamanan (VERSIONS 3.1).

**1.1:** SD-01 s.d. SD-08 diputuskan.

**1.0:** dokumen awal.
