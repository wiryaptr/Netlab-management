# NetLab Manager — Versi dan Penguncian Dependency

**Versi:** 1.4 (Node 24.22.1 dikunci; toolchain frontend dan resolusi backend terverifikasi pada scaffold)
**Tanggal:** 26 Oktober 2026
**Sumber:** keputusan OD-12 A (ADR-021), `spec.md` v1.3 §1
**Status:** Dokumentasi. Sejak 28 Oktober 2026 toolchain frontend dan resolusi backend diverifikasi pada scaffold sekali pakai (bagian 8.1). Lockfile **proyek** belum dibuat.

## 1. Batas bukti

Seluruh tabel di bawah didasarkan pada **metadata** PyPI dan npm (versi, tanggal rilis, `requires_python`, `engines`, peer dependency, classifier) yang dibaca pada 26 Oktober 2026, ditambah dokumen dukungan resmi bila disebut. Ini mendukung pemilihan versi, tetapi **bukan bukti kompatibilitas runtime**.

Satu-satunya bukti runtime yang pernah ada adalah spike sekali pakai di sandbox (sudah dihapus): Django 5.2.18 dan 6.1.2 dengan `psycopg` 3.3.6 pada PostgreSQL 16.15, mencakup custom user, exclusion constraint, constraint ekspresi, `RunSQL`, dan role runtime (DATA_MODEL 16.5). Itu tidak mencakup DRF, drf-spectacular, django-filter, gunicorn, maupun frontend. Bukti tambahan 28 Oktober 2026 (instalasi dan build pada scaffold, bukan aplikasi proyek) ada di 8.1.

## 2. Baseline

| Komponen | Baseline | Dukungan | Sumber |
| --- | --- | --- | --- |
| PostgreSQL | 16 (minor terkini: **16.15**) | Rilis akhir 9 November 2028 | postgresql.org/support/versioning, dibaca 26 Oktober 2026: mencantumkan 16.15 sebagai minor terkini dan 9 November 2028 sebagai rilis akhir. Minor dirilis tiap triwulan, jadi konfirmasi ulang saat mengunci image. |
| Django | 5.2 LTS (**5.2.18**) | Dukungan lanjutan (perbaikan keamanan dan kehilangan data) sampai April 2028; dukungan utama berakhir Desember 2025 | djangoproject.com/download |

Caddy (reverse proxy, DP-01) belum dipin; versi dan tag image ditentukan pada Phase 0.

Konsekuensi: Django 5.2 berakhir sebelum PostgreSQL 16 (April vs November 2028). Rencana peningkatan ke LTS berikutnya harus dibuat sebelum April 2028.

## 3. Aturan pemilihan pin

1. Pilih rilis stabil terbaru yang berumur **minimal 20 hari** pada 26 Oktober 2026 (lebih ketat dari 14 hari), agar rilis yang terlanjur bermasalah atau berbahaya sempat terdeteksi (VR-06).
2. Pengecualian hanya untuk patch keamanan yang mendesak, dengan prosedur dan daftar pengecualian di 3.1.
3. Peer dependency dan rentang `engines` harus saling memenuhi.
4. Dependency transitif dikunci oleh lockfile pada Phase 0, bukan di dokumen ini.

### 3.1 Pengecualian patch keamanan mendesak

Aturan umur 20 hari boleh dikesampingkan **hanya** bila semua syarat berikut terpenuhi:

1. Rilis memuat perbaikan keamanan untuk komponen yang sudah dipilih dan dipakai proyek; bukan fitur baru dan bukan komponen baru.
2. Advisori resmi dari proyek hulu (halaman keamanan proyek atau GitHub Security Advisory) sudah dibaca. Sumber sekunder saja tidak cukup untuk mengaktifkan pengecualian.
3. Versi yang dipilih adalah yang **terendah** yang memuat perbaikan pada jalur mayor/minor yang sama.
4. Asal rilis diverifikasi (kanal resmi; checksum atau tanda tangan bila tersedia).
5. Pemeriksaan normal tetap berlaku: instalasi bersih, lint, test, build, dan pemindaian lulus. Pengecualian hanya melonggarkan umur rilis, bukan kompatibilitas.
6. Alasan, versi, umur rilis saat dipilih, tautan advisori, dan pemberi persetujuan dicatat pada daftar berikut. Aturan normal berlaku lagi pada pembaruan berikutnya.

**Aturan umur rilis (VR-06 dan VR-06a, disetujui 27 Oktober 2026):**

- Rilis normal: minimal 20 hari.
- Patch keamanan mendesak: boleh dikecualikan dari batas 20 hari setelah advisori resmi diverifikasi dan kompatibilitas diuji (syarat 1–6 di atas).
- Lantai umum untuk pengecualian: 72 jam sejak rilis.
- Rilis yang lebih muda dari 72 jam hanya boleh dipilih bila **eksploitasi aktif terkonfirmasi**, dengan alasan, bukti eksploitasi, hasil pengujian, dan persetujuan dicatat pada daftar pengecualian. Risiko keamanan yang mendesak tanpa eksploitasi aktif terkonfirmasi **tidak cukup**; gunakan jalur pengecualian umum dengan lantai 72 jam.

| ID | Komponen | Versi | Umur saat dipilih | Alasan | Sumber advisori | Status |
| --- | --- | --- | --- | --- | --- | --- |
| EX-01 | Node.js 24 | 24.22.1 | 6 hari saat dinilai (27 Oktober), 7 hari saat dikunci (28 Oktober); rilis 21 Oktober 2026; di atas lantai 72 jam | Rilis keamanan terkoordinasi 21 Oktober 2026 untuk 22.x, 24.x, dan 26.x. Advisori memuat sepuluh kerentanan (delapan di antaranya memengaruhi 24.x menurut ringkasan sekunder) berperingkat High, Medium, dan Low dari proyek Node.js. Yang High pada 24.x mencakup out-of-bounds write pada decoder Brotli yang memungkinkan eksekusi kode jarak jauh (CVE-2026-111497) dan bypass validasi hostname TLS. Rilis 24.x sebelum 24.22.1 tidak memuat perbaikannya. | Advisori resmi `nodejs.org/en/blog/vulnerability/october-2026-security-releases` **dibaca pemilik proyek** (konfirmasi 27 Oktober: 24.22.1 berstatus LTS, 26.12.1 Current). Verifikasi independen saya terbatas: kutipan advisori itu pada daftar oss-security (`openwall.com/lists/oss-security/2026/10/22/8`) mencantumkan URL resmi, daftar versi, dan peringkat tersebut; halaman nodejs.org sendiri tidak dapat saya baca. Peringkat berasal dari proyek Node.js; skor CVSS belum terverifikasi. | **Disetujui dan dikunci (28 Oktober 2026):** advisori terpenuhi (dibaca pemilik proyek); clean install, lint, test, dan build lulus pada scaffold (8.1). |

Catatan EX-01: Node dipakai proyek hanya untuk build dan test frontend, bukan sebagai server produksi (spec §12), sehingga paparan lebih rendah daripada aplikasi yang menjalankan Node. Pengecualian tetap dinilai wajar karena CI dan mesin pengembang menjalankan Node; keputusan akhir ada pada pemilik proyek.

## 4. Runtime

| Runtime | Pilihan | Bukti | Status |
| --- | --- | --- | --- |
| Python | **3.12** | Metadata Django 5.2.18, DRF 3.18.3, `psycopg` 3.3.6, dan django-filter 26.2 menyatakan dukungan 3.12 (django-filter mensyaratkan ≥ 3.11) | Usulan VR-01. Jadwal akhir dukungan Python 3.12 tidak diperiksa pada sesi ini. |
| Node.js | **Dikunci: Node 24 LTS, patch 24.22.1** (memuat rilis keamanan 21 Oktober 2026; pengecualian EX-01 di 3.1). **Node 26** (Current, bukan LTS) tidak dipakai; dievaluasi ulang hanya bila kompatibilitas tooling dan kebijakan proyek membenarkannya dan status LTS resminya terkonfirmasi. | Syarat metadata: `jsdom` 30.1.2 `^22.22.2 \|\| ^24.15.0 \|\| >=26`; Vitest 5.0.3 `^22.12 \|\| ^24 \|\| >=26`; ESLint 10.12.0 `^20.19 \|\| ^22.13 \|\| >=24`; Vite 8.3.3 `^20.19 \|\| >=22.12`. 24.22.1 memenuhi seluruhnya (≥ 24.15.0). Status rilis: nodejs.org per 27 Oktober 2026 menampilkan Node 26 sebagai Current dan Node 24 sebagai LTS, dan advisori keamanan 21 Oktober sudah dibaca pemilik proyek (konfirmasi pemilik proyek; halaman nodejs.org belum dapat saya baca langsung). Sumber sekunder: Node 24 Maintenance sejak 20 Oktober 2026 dengan dukungan keamanan sampai 30 April 2028; Node 26 diperkirakan masuk LTS sekitar 28 Oktober 2026 (**belum terkonfirmasi resmi; jangan disebut LTS**) dengan keamanan sampai 30 April 2029. | VR-03 diselesaikan 28 Oktober 2026: Node 24.22.1 dikunci setelah clean install, lint, test, dan build berhasil pada scaffold (8.1), dengan syarat npm ≥ 11 (temuan 8.1). Bila memakai image kontainer, tag eksak harus dibangun ulang dengan menarik image terbaru agar patch keamanan masuk (sumber sekunder). |

Node hanya dipakai untuk membangun dan menguji frontend; aset hasil build disajikan statis (spec §12).

## 5. Pin backend

Umur dihitung terhadap 26 Oktober 2026.

| Paket | Versi | Dirilis | Umur | Bukti kompatibilitas (metadata) | Dasar |
| --- | --- | --- | --- | --- | --- |
| Django | **5.2.18** | 2026-10-06 | 20 hari | Python ≥ 3.10 (classifier sampai 3.14); bergantung `asgiref>=3.9.1`, `sqlparse>=0.5.0` | OD-12 A |
| djangorestframework | **3.18.3** | 2026-10-06 | 20 hari | `django>=5.2`; classifier Django 5.2, 6.0, 6.1; Python ≥ 3.10. Versi 3.18.2 dirilis pada hari yang sama; baca catatan rilis saat mengunci. | spec §1 |
| psycopg | **3.3.6** (`psycopg[binary]`, tarik `psycopg-binary==3.3.6`) | 2026-09-18 | 38 hari | Python ≥ 3.10; classifier sampai 3.14. Dipakai pada spike dengan Django 5.2.18. | spec §1 |
| ruff | **0.16.10** | 2026-10-01 | 25 hari | Pra-1.0; minor dapat mengubah aturan, jadi dikunci eksak | spec §1 |
| drf-spectacular | **0.30.0** | 2026-07-06 | 112 hari | `Django>=2.2`, `djangorestframework>=3.10.3`; classifier Django 5.2 dan 6.0 | **Usulan VR-02** |
| django-filter | **26.2** | 2026-10-03 | 23 hari | `Django>=5.2`; classifier Django 5.2, 6.0, 6.1; Python ≥ 3.11 | **Usulan VR-02** |
| gunicorn | **26.2.0** | 2026-08-24 | 63 hari | Python ≥ 3.10 | **Usulan VR-02** |

Tidak dipin: backend test runner (diputuskan Django test framework tanpa dependency tambahan, VR-07), alat pembuat lockfile backend (VR-05), dan varian `psycopg` (VR-04); dua yang terakhir diputuskan pada Phase 0 setelah uji instal bersih.

Dependensi transitif yang ter-resolve pada verifikasi 28 Oktober 2026 antara lain `asgiref` 3.13.0 dan `sqlparse` 0.6.0 (daftar lengkap 20 paket di `docs/evidence/backend-resolution-freeze.txt`); versi akhirnya dikunci oleh lockfile proyek.

## 6. Pin frontend

| Paket | Versi | Dirilis | Umur | Bukti (engines/peer) |
| --- | --- | --- | --- | --- |
| react | **19.3.0** | 2026-09-09 | 47 hari | — |
| react-dom | **19.3.0** | 2026-09-09 | 47 hari | peer `react ^19.3.0` |
| typescript | **6.0.3** | 2026-04-16 | 193 hari | **Bukan 7.0.2** (lihat 7.1) |
| vite | **8.3.3** | 2026-10-06 | 20 hari | node `^20.19.0 \|\| >=22.12.0` |
| @vitejs/plugin-react | **6.1.2** | 2026-10-05 | 21 hari | peer `vite ^8.0.0` |
| vitest | **5.0.3** | 2026-09-30 | 26 hari | peer `vite ^6.4 \|\| ^7 \|\| ^8`; `jsdom`; node `^22.12 \|\| ^24 \|\| >=26` |
| @testing-library/react | **16.3.3** | 2026-08-27 | 60 hari | peer `react ^18 \|\| ^19`, `@testing-library/dom ^10` |
| @testing-library/dom | **10.4.2** | 2026-09-13 | 43 hari | — |
| jsdom | **30.1.2** | 2026-10-04 | 22 hari | node `^22.22.2 \|\| ^24.15.0 \|\| >=26` |
| eslint | **10.12.0** | 2026-10-02 | 24 hari | node `^20.19 \|\| ^22.13 \|\| >=24` |
| typescript-eslint | **8.71.1** | 2026-10-05 | 21 hari | peer `eslint ^8.57 \|\| ^9 \|\| ^10`, `typescript >=4.8.4 <6.1.0` |
| @types/react | **19.3.0** | — | — | Terpasang saat verifikasi (dibutuhkan TypeScript strict dengan React). Tanggal rilis dan aturan umur 20 hari **belum diperiksa**. |
| @types/react-dom | **19.3.0** | — | — | Sama seperti di atas. |

Paket frontend lain (router, pengambilan data, generator klien dari OpenAPI) **belum dipilih** dan membutuhkan keputusan dan ADR sebelum dipin (VR-08; spec §12 hanya mensyaratkan klien API bertipe yang konsisten dengan OpenAPI).

## 7. Catatan kompatibilitas

### 7.1 TypeScript 7 tidak dipakai

`typescript` 7.0.2 adalah rilis terbaru, tetapi seluruh rilis `typescript-eslint` yang diperiksa (8.71.1 sampai 8.72.0) menyatakan peer `typescript <6.1.0`. Memasang TypeScript 7 akan melanggar peer dependency. Pin 6.0.3 mengikuti batas itu. Tinjau ulang saat `typescript-eslint` mendukung TypeScript 7.

### 7.2 Patch Node dibatasi oleh jsdom

Syarat `jsdom` 30.1.2 menaikkan batas bawah Node 24 menjadi 24.15.0, lebih tinggi daripada syarat Vitest atau Vite saja.

### 7.3 Django 5.2 dalam dukungan lanjutan

Sejak Desember 2025 hanya perbaikan keamanan dan kehilangan data. Fitur baru dan perbaikan bug biasa tidak lagi di-backport.

### 7.4 Banyak mayor baru pada frontend

Vite 8, ESLint 10, dan Vitest 5 adalah rilis mayor yang relatif baru. Risiko regresi tooling lebih tinggi daripada backend; tidak ada bukti runtime.

### 7.5 Django 6.1 bukan baseline

Django 6.1 (Agustus 2026) didukung oleh DRF 3.18.3 dan django-filter 26.2 menurut metadata, dan lolos pada spike, tetapi bukan baseline (OD-12 A).

## 8. Bukti verifikasi dan yang belum terbukti

### 8.1 Bukti (28 Oktober 2026)

Semua dijalankan di sandbox sekali pakai (Linux x64, Python 3.12.3). Ini adalah **scaffold minimal**, bukan aplikasi proyek.

**Lingkungan:** Node 24.22.1 dipasang dari paket npm `node-linux-x64@24.22.1`, bukan dari nodejs.org; checksum biner tidak dibandingkan dengan nodejs.org. npm 11.21.1 dipakai sebagai pengganti npm bawaan Node 24 (versi bundel persisnya tidak diperiksa).

**Frontend** (satu komponen React, satu tes, konfigurasi eslint, tsc, dan vite):
- Clean install seluruh pin di bagian 6 **tanpa `--legacy-peer-deps`**: berhasil, tanpa konflik peer, 183 paket.
- Lint, test (1 lulus), dan build (`tsc -b` + `vite build`): berhasil.
- `npm ci` dari lockfile pada salinan bersih: berhasil, dengan lint, test, dan build yang sama.
- Sebelas pin tingkat atas sama dengan versi pada lockfile.
- `npm audit`: 0 kerentanan (hanya toolchain frontend; bukan pemindaian proyek).
- **Temuan:** npm 10.9.7 (bawaan Node 22) **gagal** pada instalasi yang sama dengan `Cannot read properties of null (reading 'edgesOut')` (galat Arborist saat memuat peer set). Baseline karena itu mensyaratkan npm 11 atau lebih baru; versi npm harus dikunci pada Phase 0.
- Paket di luar daftar pin yang ikut terpasang: `@types/react` dan `@types/react-dom` 19.3.0 (ditambahkan ke bagian 6).

**Backend** (venv Python 3.12.3): instalasi bersih tujuh pin di bagian 5 berhasil; `pip check` tidak menemukan requirement rusak; seluruh paket dapat diimpor dan melaporkan versi yang sama dengan pin. Tidak ada perilaku runtime yang diuji.

**Berkas bukti** (bukan lockfile proyek): `docs/evidence/backend-resolution-freeze.txt` (sha256 awal `78bc124c83dbde33`), `docs/evidence/frontend-toolchain.package.json` (`0ab05456b0c924be`), dan `docs/evidence/frontend-toolchain.package-lock.json` (`ed84319a6a3c61c9`). Lockfile proyek dibuat di repository dan harus menghasilkan versi tingkat atas yang sama.

**DDL:** uji ulang setelah `vlan_number` ada di DATA_MODEL 16.7.

**Batas bukti:** scaffold tidak menguji CSP, klien API bertipe dari OpenAPI, TypeScript strict pada kode proyek, image kontainer, arsitektur selain x64, maupun penandatanganan paket.

### 8.2 Belum terbukti

1. Dependensi transitif dan hash pada lockfile proyek.
2. Perilaku runtime DRF 3.18.3, drf-spectacular, django-filter, dan gunicorn dengan Django 5.2.18 (baru resolusi dan impor).
3. Tag image kontainer untuk Python, Node, PostgreSQL, dan reverse proxy.
4. Tag image PostgreSQL 16.15 (minor itu sendiri terkonfirmasi dari postgresql.org).
5. Jadwal akhir dukungan Python 3.12.
6. Versi npm yang dibundel Node 24 dan pin npm.
7. Pemindaian kerentanan penuh (dependency backend dan secret).

## 9. Prosedur penguncian pada Phase 0

1. Setujui VR-01 s.d. VR-08.
2. Buat lockfile backend dengan hash (alat sesuai VR-05) dan `package-lock.json` frontend dengan `npm ci` di CI.
3. Pasang seluruh pin pada lingkungan bersih; catat konflik; jangan mengubah pin tanpa memperbarui dokumen ini dan ADR-021.
4. Jalankan lint, typecheck, test, dan build minimal (spec §16 Phase 0).
5. Jalankan pemindaian kerentanan dan secret (SECURITY.md bagian 10).
6. Konfirmasi tag image dan minor PostgreSQL 16 terbaru.

## 10. Keputusan dan statusnya

Status per 28 Oktober 2026: **VR-02 disetujui bersyarat** (resolusi berhasil, 8.1; uji runtime belum); **VR-03 diselesaikan:** Node 24.22.1 dikunci setelah clean install, lint, test, dan build berhasil pada scaffold (8.1), Node 26 tidak dipakai; **VR-06 dan VR-06a disetujui** (umur rilis normal minimal 20 hari; pengecualian patch keamanan mendesak dengan lantai 72 jam, kecuali eksploitasi aktif terkonfirmasi; 3.1, daftar EX-xx); **VR-07 disetujui** (Django test framework). VR-01, VR-04, VR-05, dan VR-08 default diterima.

| ID | Usulan |
| --- | --- |
| VR-01 | Python 3.12. |
| VR-02 | Menambah dependency yang tidak disebut spec: drf-spectacular (skema OpenAPI), django-filter (filter server-side), gunicorn (application server). |
| VR-03 | Node 24 LTS untuk tooling frontend (diselesaikan: 24.22.1 dikunci, 8.1). Node 26 tidak dipakai; dievaluasi ulang hanya bila status LTS resminya terkonfirmasi dan tooling membenarkan. |
| VR-04 | Varian `psycopg`: `binary` atau dibangun dari sumber (`c`) untuk produksi. Belum diverifikasi pada sesi ini; tidak ada usulan. |
| VR-05 | Alat pembuat lockfile backend (belum dipilih). |
| VR-06 | Aturan umur rilis minimal 20 hari. |
| VR-07 | Backend test runner: Django test framework atau pytest (spec §1 membiarkan terbuka). |
| VR-08 | Pustaka frontend tambahan (router, data fetching, klien OpenAPI) dipilih lewat ADR sebelum dipin. |

## 11. Catatan revisi

**1.4:** Node 24.22.1 dikunci (EX-01 disetujui); bukti clean install, lint, test, build, dan `npm ci` pada scaffold; resolusi pin backend; temuan npm 10.9.7 gagal; `@types/react` dan `@types/react-dom` ditambahkan; berkas bukti di `docs/evidence/`; bagian 8 disusun ulang.

**1.3:** VR-06a disetujui (lantai 72 jam untuk pengecualian; lebih cepat hanya bila eksploitasi aktif terkonfirmasi dan tercatat; dikonfirmasi 27 Oktober: risiko mendesak tanpa eksploitasi aktif tidak cukup untuk memilih rilis di bawah 72 jam); EX-01 diperbarui: syarat advisori resmi terpenuhi (dibaca pemilik proyek), tetap belum dikunci.

**1.2:** VR-03 diperbarui (Node 24.22.1 kandidat, Node 26 tidak disebut LTS sebelum terkonfirmasi resmi); VR-06 diberi prosedur dan daftar pengecualian patch keamanan (3.1, EX-01 kandidat); tidak ada pin Node.

**1.1:** VR-01 s.d. VR-08 diputuskan; PostgreSQL 16.15 terkonfirmasi dari postgresql.org; Node diperbarui menurut endoflife.date (Node 24 kini Maintenance; Node 26 menunggu LTS); tidak ada pin Node.

**1.0:** dokumen awal; pin berdasarkan metadata 26 Oktober 2026.
