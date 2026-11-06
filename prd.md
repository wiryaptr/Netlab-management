# NetLab Manager — Product Requirements Document (PRD)

**Versi:** 1.3
**Tanggal:** 25 Oktober 2026
**Status:** Draft untuk validasi sebelum implementasi

**Hierarki dokumen:** `prd.md` (kebutuhan produk) → `design.md` (rancangan) → `spec.md` (persyaratan teknis) → `docs/` (kontrak rinci: `DATA_MODEL.md`, `RBAC_MATRIX.md`, `API_SPEC.md`, `SECURITY.md`, `DEPLOYMENT.md`, `ADR.md`). Dokumen di `docs/` merinci, bukan menggantikan. Jika ada pertentangan, berhenti dan laporkan.

## 1. Ringkasan Produk

NetLab Manager adalah aplikasi web untuk mengelola inventaris dan dokumentasi operasional laboratorium jaringan. Sistem memusatkan data perangkat, lokasi, antarmuka jaringan, subnet, alamat IP, VLAN, koneksi, insiden, dan riwayat perubahan.

MVP berfokus pada pencatatan dan pengelolaan data secara terkontrol. Sistem **bukan** network scanner, bukan pengganti router/switch, dan belum melakukan monitoring real-time atau perubahan konfigurasi perangkat secara otomatis.

## 2. Masalah yang Ingin Diselesaikan

Informasi laboratorium dapat tersebar di spreadsheet, catatan pribadi, dan dokumentasi yang tidak seragam. Hal ini menyulitkan pengelola untuk:

- mengetahui inventaris dan lokasi perangkat;
- memeriksa dokumentasi IP, subnet, dan VLAN;
- memahami hubungan antarmuka dan koneksi;
- menelusuri gangguan serta tindakan perbaikan;
- membatasi perubahan data sesuai tanggung jawab pengguna;
- mengaudit perubahan operasional.

## 3. Tujuan dan Ukuran Keberhasilan

### Tujuan

1. Menyediakan sumber data terpusat untuk inventaris laboratorium.
2. Mengurangi konflik dan ketidakkonsistenan alokasi alamat IP.
3. Mendokumentasikan subnet, VLAN, interface, dan koneksi.
4. Mencatat insiden serta riwayat penanganannya.
5. Menerapkan autentikasi, otorisasi berbasis peran, dan audit.
6. Memindahkan data awal dari spreadsheet dengan impor CSV yang tervalidasi.
7. Menyediakan deployment yang dapat direproduksi dan prosedur backup/restore.

### Kriteria keberhasilan MVP

- Pengguna berwenang dapat membuat, mencari, melihat, mengubah, dan mengarsipkan aset.
- Sistem menolak alokasi IP yang bertentangan, termasuk pada request bersamaan.
- Sistem menolak subnet yang overlap dengan subnet aktif lain.
- Sistem menolak koneksi fisik kedua pada interface yang sama, termasuk pada request bersamaan.
- Data subnet, VLAN, interface, dan koneksi tervalidasi di backend.
- Pengguna tanpa izin tidak dapat melakukan tindakan terlarang dengan memanggil API secara langsung.
- Perubahan penting dapat ditelusuri melalui audit log tanpa merekam secret.
- Data awal dapat diimpor dari CSV dengan preview dan laporan error per baris.
- Aplikasi dapat dijalankan mengikuti dokumentasi dan database dapat dipulihkan dari backup yang telah diuji.

## 4. Pengguna dan Peran

Peran diimplementasikan sebagai Django Groups dengan permission eksplisit. Matriks rinci ada di `docs/RBAC_MATRIX.md`.

### Administrator

Mengelola akun, status pengguna, peran, konfigurasi sistem, dan seluruh operasi administratif yang diizinkan.

### Lab Manager

Mengelola inventaris, lokasi, IPAM, VLAN, koneksi, insiden, impor CSV, serta meninjau audit sesuai kebijakan.

### Lab Assistant

Melihat data operasional dan memperbarui data atau menangani insiden sesuai permission yang diberikan.

### Viewer

Melihat data yang diizinkan tanpa melakukan perubahan.

Otorisasi wajib ditegakkan di backend. Menyembunyikan tombol pada frontend tidak dianggap sebagai kontrol keamanan.

## 5. Ruang Lingkup MVP

### Termasuk

- Login, logout, endpoint identitas pengguna, dan ganti password sendiri.
- Manajemen pengguna dan peran oleh administrator.
- Inventaris aset dan lokasi.
- Interface perangkat (CRUD).
- Subnet IPv4/IPv6 (dengan relasi opsional ke satu VLAN) dan alamat IP.
- VLAN (nomor 1–4094, kecuali 1002–1005).
- Dokumentasi koneksi antarmuka.
- Insiden dan catatan penanganan, dengan relasi opsional ke aset.
- Audit log untuk tindakan penting (daftar event wajib ada di `spec.md`).
- Impor CSV (lokasi, aset, subnet, alamat IP) dengan preview, validasi, dan laporan error.
- Dashboard ringkasan operasional.
- Pencarian, filter, pagination, validasi, dan pesan error konsisten.
- Dokumentasi OpenAPI.
- Deployment lokal/laboratorium, konfigurasi environment, backup, dan restore.

### Tidak termasuk

- Network discovery atau pemindaian jaringan otomatis.
- Agent yang dipasang pada setiap PC.
- Monitoring CPU, bandwidth, uptime, atau status perangkat secara real-time.
- SSH otomatis ke router/switch.
- Perubahan konfigurasi perangkat secara otomatis.
- Topologi interaktif dengan auto-discovery.
- Integrasi dengan InfraTrack.
- Multi-tenant lintas organisasi dan multi-VRF pada MVP.
- Impor CSV untuk VLAN (CSV subnet hanya merujuk VLAN yang sudah ada).
- Kubernetes atau microservices.

## 6. Alur Pengguna Utama

### Mengelola aset

1. Pengguna berwenang membuka daftar aset.
2. Pengguna mencari atau memfilter aset.
3. Pengguna menambahkan atau memperbarui data.
4. Backend memvalidasi input dan izin.
5. Data disimpan dan tindakan penting dicatat dalam audit log.

### Mengalokasikan IP

1. Pengguna memilih subnet yang sesuai.
2. Pengguna memasukkan alamat IP dan hubungan aset/interface jika ada.
3. Backend memvalidasi alamat terhadap subnet dan kebijakan alokasi.
4. Database mencegah alokasi ganda.
5. Sistem mengembalikan hasil sukses atau konflik yang dapat dipahami.

### Menangani insiden

1. Pengguna membuat tiket dengan judul, deskripsi, tingkat keparahan, dan aset terkait (opsional).
2. Insiden diberi status dan penanggung jawab.
3. Setiap perubahan status atau tindakan penting menambahkan event.
4. Pengguna berwenang meninjau riwayat insiden.

### Mengimpor data dari CSV

1. Pengguna berwenang memilih jenis data dan mengunggah file CSV.
2. Sistem menjalankan preview: validasi seluruh baris tanpa menyimpan, lalu menampilkan ringkasan dan error per baris.
3. Pengguna memperbaiki file bila ada error, lalu mengunggah ulang.
4. Pengguna mengonfirmasi commit; sistem memvalidasi ulang dan menyimpan semua baris dalam satu transaksi (all-or-nothing).
5. Hasil impor dicatat dalam audit log.

## 7. Kebutuhan Fungsional

- **FR-01 Auth:** pengguna dapat login/logout dan mengganti password sendiri; akun nonaktif ditolak.
- **FR-02 User/RBAC:** administrator dapat membuat, mengubah, dan menonaktifkan akun serta menetapkan peran. Akun tidak dihapus fisik.
- **FR-03 Asset:** sistem mendukung CRUD/arsip aset, pencarian, filter, dan pagination.
- **FR-04 Location:** aset dapat dikaitkan dengan lokasi.
- **FR-05 Interface:** interface (CRUD) terikat pada aset dan memiliki identitas yang tervalidasi.
- **FR-06 Subnet:** sistem menyimpan CIDR, gateway opsional (informasi, tidak otomatis menjadi alokasi IP), VLAN opsional, dan deskripsi; subnet aktif tidak boleh overlap. VLAN yang dirujuk harus aktif.
- **FR-07 IP address:** alamat IP dapat dicatat dan dialokasikan dengan pemeriksaan konflik; pelepasan alamat dicatat.
- **FR-08 VLAN:** Nomor VLAN, nama, deskripsi, dan status dapat dikelola. VLAN yang masih dirujuk subnet aktif tidak dapat diarsipkan.
- **FR-09 Connection:** sistem mendokumentasikan hubungan interface dan tipe koneksi sebagai relasi tak berarah tanpa duplikasi. Satu interface hanya boleh memiliki satu koneksi aktif bertipe fisik (`ethernet`, `fiber`, `console`); tipe `wireless` dan `virtual` tidak dibatasi.
- **FR-10 Incident:** insiden memiliki severity, status, assignee, aset terkait opsional, waktu, dan event.
- **FR-11 Audit:** tindakan penting dicatat dengan aktor, aksi, objek, waktu, dan metadata aman.
- **FR-12 API:** endpoint terdokumentasi melalui OpenAPI dan memakai format error serta pagination yang konsisten.
- **FR-13 Operations:** sistem menyediakan instruksi deployment, backup, dan restore.
- **FR-14 Import CSV:** impor lokasi, aset, subnet, dan alamat IP dengan preview, validasi, laporan error, dan commit atomik.
- **FR-15 Dashboard:** ringkasan operasional dihitung dari data aktual sesuai permission pengguna.

## 8. Kebutuhan Nonfungsional

- **Security:** validasi server-side, session security, CSRF protection, permission per endpoint/objek, rate limiting untuk login dan endpoint berisiko, role database runtime berhak minimum yang terpisah dari role pemilik skema, secret tidak masuk repository/log.
- **Integrity:** foreign key, constraint, transaksi, dan penanganan race condition untuk alokasi IP.
- **Maintainability:** modular monolith, batas modul jelas, linting, formatting, dan automated tests.
- **Usability:** status loading/error/empty state, label form yang jelas, dan navigasi konsisten.
- **Reliability:** health check dan prosedur backup/restore terdokumentasi.
- **Performance:** pagination untuk daftar; optimasi dilakukan berdasarkan pengukuran, bukan asumsi.
- **Compatibility:** akses melalui browser modern pada jaringan yang diizinkan.
- **Observability:** log aplikasi tidak mengandung password, token, cookie, private key, atau secret.

## 9. Kebijakan Data

- Gunakan PostgreSQL dengan tipe `inet` untuk alamat IP dan `cidr` untuk subnet.
- **Keunikan IP:** alamat IP aktif unik per subnet `(subnet, address)`. Karena MVP hanya satu domain jaringan, subnet aktif **tidak boleh overlap**, dan alamat wajib berada di dalam subnetnya. Kedua aturan ini harus berjalan bersama; unique per subnet saja tidak cukup. Dukungan multi-VRF/domain jaringan adalah perubahan di luar MVP dan membutuhkan ADR baru.
- Gunakan transaksi dan constraint database untuk mencegah alokasi ganda dan subnet overlap.
- **Arsip:** data operasional diarsipkan dengan kolom `archived_at`. Penghapusan fisik tidak tersedia melalui UI/API biasa.
- Penghapusan atau arsip tidak boleh menghilangkan audit trail.
- **Subnet–VLAN:** satu subnet dapat dikaitkan dengan paling banyak satu VLAN; satu VLAN dapat dirujuk banyak subnet. Relasi baru hanya ke VLAN aktif.
- **Koneksi fisik:** satu interface hanya boleh memiliki satu koneksi aktif bertipe `ethernet`, `fiber`, atau `console`. Aturan ini ditegakkan di database sehingga aman terhadap request bersamaan.
- **Penjaga integritas:** aturan arsip induk–anak (lokasi, aset, interface, subnet, VLAN) ditegakkan di database, tidak hanya di service.
- **Akses database:** aplikasi berjalan dengan role runtime tanpa hak pemilik tabel, tanpa hak `DELETE`/`TRUNCATE` pada data operasional, dan tanpa hak menonaktifkan trigger.
- Semua timestamp disimpan secara timezone-aware dan ditampilkan dengan zona waktu yang ditetapkan.
- File CSV tidak boleh berisi secret atau credential perangkat, dan tidak disimpan setelah impor selesai.
- Jangan masukkan data sensitif laboratorium nyata ke development tanpa izin.

## 10. Batasan dan Asumsi

- MVP dimulai untuk satu laboratorium.
- Data awal dimasukkan manual atau melalui impor CSV yang tervalidasi.
- Deployment awal berada pada server Linux lokal/laboratorium yang telah diizinkan.
- Belum ada asumsi bahwa perangkat mendukung SNMP/API atau bahwa pengguna memiliki akses administratif ke perangkat.
- Integrasi perangkat hanya boleh dirancang setelah ada izin, kebutuhan, dan metode autentikasi yang disetujui.

## 11. Acceptance Criteria

1. Login/logout, ganti password, dan penolakan akun nonaktif diuji otomatis.
2. Uji RBAC membuktikan request tanpa izin ditolak di backend.
3. CRUD/arsip aset dan filter bekerja sesuai kontrak API.
4. Subnet dan IP tervalidasi; konflik alokasi dan subnet overlap ditolak, termasuk pada request bersamaan.
5. Interface, VLAN, relasi subnet–VLAN, dan koneksi hanya menerima relasi yang valid; koneksi duplikat (termasuk arah terbalik) dan koneksi fisik kedua pada satu interface ditolak, termasuk pada request bersamaan; VLAN yang dirujuk subnet aktif tidak dapat diarsipkan.
6. Insiden menyimpan event riwayat yang dapat ditelusuri dan dapat dikaitkan ke aset.
7. Audit log mencakup seluruh event wajib, tidak merekam secret, dan tidak dapat diubah melalui endpoint pengguna biasa.
8. API memiliki dokumentasi OpenAPI yang sesuai implementasi.
9. Impor CSV: preview tidak mengubah data, commit atomik, error dilaporkan per baris.
10. Rate limiting login aktif dan diuji.
11. Build/deployment dapat direproduksi dari dokumentasi.
12. Backup database berhasil dipulihkan pada uji restore.
13. Pengarsipan dan penulisan bersamaan pada relasi induk–anak tidak menghasilkan data yang melanggar aturan arsip; diuji dengan transaksi paralel.
14. Role runtime tidak dapat menghapus data operasional, mengubah audit, atau menonaktifkan trigger.

## 12. Risiko

| Risiko | Mitigasi |
| --- | --- |
| Scope membesar menjadi monitoring platform | Pertahankan batas MVP dan gunakan change request |
| Data IP tidak konsisten | Gunakan tipe PostgreSQL, validasi, dan constraint |
| Pengguna melewati kontrol UI | Terapkan permission di backend |
| Audit log tidak lengkap | Event wajib didefinisikan di spec dan diuji |
| Impor CSV merusak data | Preview, validasi ulang saat commit, transaksi atomik |
| Toolchain Compose tidak tersedia | Validasi provider pada fase fondasi |
| Integrasi perangkat tanpa izin | Tunda integrasi sampai otorisasi terdokumentasi |
| Backup tidak dapat dipulihkan | Lakukan restore drill berkala |
| Penulisan bersamaan melanggar aturan arsip induk–anak | Trigger penjaga dengan kunci baris induk dan uji transaksi paralel |
| Aplikasi atau akun runtime melewati trigger | Role runtime berhak minimum, terpisah dari role pemilik skema |
| Dokumen saling bertentangan | Hierarki dokumen; berhenti dan laporkan bila konflik |

## 13. Definition of Done

Fitur dinyatakan selesai bila:

- implementasi sesuai PRD dan kontrak API;
- validasi dan permission diuji;
- automated tests yang relevan lulus;
- dokumentasi diperbarui;
- tidak ada secret di repository/log;
- migrasi database dapat diterapkan secara konsisten;
- reviewer menyetujui perubahan dan acceptance criteria terpenuhi.

## 14. Catatan Revisi 1.1

- Tambah: interface CRUD, user management, relasi insiden–aset, impor CSV, dashboard, rate limiting.
- Putuskan: keunikan IP per subnet + larangan subnet overlap; arsip dengan `archived_at`; peran via Django Groups.
- Hapus ambiguitas: scope "Tidak termasuk" menyebut multi-VRF di luar MVP.

## 15. Catatan Revisi 1.2

- Putuskan: relasi opsional subnet–VLAN, satu koneksi fisik aktif per interface, gateway hanya informasi, VLAN 1002–1005 ditolak.
- Tambah: kebijakan akses database (role runtime berhak minimum), penjaga integritas database, acceptance criteria 13–14.
- Selaraskan dengan `docs/DATA_MODEL.md` versi 1.1 (versi saat revisi 1.2 dibuat).

## 16. Catatan Revisi 1.3

- Tegaskan impor CSV tidak mencakup VLAN; ganti istilah "VLAN ID" menjadi "Nomor VLAN" pada FR-08.
