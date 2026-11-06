# NetLab Manager — Technical Specification

**Versi:** 1.3
**Tanggal:** 25 Oktober 2026
**Status:** Spesifikasi teknis untuk implementasi bertahap

Hierarki dokumen: `prd.md` → `design.md` → `spec.md` → `docs/`. Dokumen di `docs/` merinci kontrak (data model, RBAC, API, security, deployment, ADR) dan tidak boleh bertentangan dengan dokumen utama. Jika ada pertentangan, berhenti dan laporkan.

## 1. Stack Teknologi

| Lapisan | Teknologi | Ketentuan |
| --- | --- | --- |
| Frontend | React + TypeScript + Vite | SPA; strict TypeScript |
| Backend | Python + Django 5.2 LTS + Django REST Framework | REST API berversi |
| Database | PostgreSQL 16 | Constraint dan transaksi sebagai penjaga integritas |
| API schema | OpenAPI | Schema mengikuti implementasi |
| Authentication | Django session + CSRF | Untuk penggunaan browser pada MVP |
| Authorization | Django Groups + permission eksplisit | Matriks rinci di `docs/RBAC_MATRIX.md` |
| Deployment | Docker/Podman Compose | Pilih provider yang tersedia dan teruji |
| Reverse proxy | Nginx atau Caddy | HTTPS dan routing |
| Testing backend | Django test framework atau pytest | Unit dan integration tests |
| Testing frontend | Vitest + React Testing Library | Komponen dan alur UI |
| Quality | Ruff, formatter, ESLint, TypeScript checks | Dijalankan dalam workflow development/CI |

Versi dependency harus dipin atau dikunci melalui lockfile yang sesuai. Baseline ditetapkan: PostgreSQL 16 dan Django 5.2 LTS (ADR-021). Versi patch dan dependency lain (DRF, psycopg, dan seterusnya) dikunci pada Phase 0 setelah pemeriksaan kompatibilitas; jangan menuliskan versi yang belum diverifikasi sebagai persyaratan mutlak.

## 2. Struktur Repository

```text
netlab-manager/
├── prd.md
├── design.md
├── spec.md
├── docs/
│   ├── DATA_MODEL.md
│   ├── RBAC_MATRIX.md
│   ├── API_SPEC.md
│   ├── SECURITY.md
│   ├── DEPLOYMENT.md
│   ├── VERSIONS.md
│   └── ADR.md
├── frontend/
├── backend/
│   ├── config/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── locations/
│   │   ├── assets/
│   │   ├── ipam/
│   │   ├── vlans/
│   │   ├── connections/
│   │   ├── incidents/
│   │   ├── imports/
│   │   └── audit/
│   ├── manage.py
│   └── pyproject.toml
├── deployment/
├── compose.yaml
├── .env.example
└── README.md
```

Tiga dokumen utama berada di root; dokumen rinci berada di `docs/`. Jangan menduplikasi isi antar dokumen. Satu fakta hanya boleh ditetapkan di satu tempat, dokumen lain merujuknya. `deployment/` berisi konfigurasi dan prosedur operasional (compose, reverse proxy, backup, restore); bukan aplikasi Django.

## 3. Aturan Backend

- Prefix endpoint: `/api/v1/`.
- Format payload: JSON (kecuali unggah CSV: `multipart/form-data`).
- Gunakan serializer untuk validasi bentuk input dan service/domain logic untuk aturan bisnis lintas model.
- Gunakan permission class dan pemeriksaan akses objek.
- Terapkan pagination server-side pada endpoint koleksi (lihat bagian 5).
- Gunakan filter/search yang diizinkan dan tervalidasi.
- Gunakan transaksi untuk operasi multi-langkah.
- Terapkan constraint database bagi invariant kritis.
- Gunakan custom user model sejak migrasi pertama.
- Gunakan isolation level `READ COMMITTED` (default Django); trigger penjaga database bergantung padanya.
- Petakan error constraint database berdasarkan **nama constraint**, bukan teks pesan (`docs/DATA_MODEL.md`). Ulangi transaksi satu kali bila terjadi deadlock (`40P01`).
- Ambil kunci baris induk sebelum anak dengan urutan vlan → subnet → location → asset → interface; saat mengarsipkan aset, kunci aset lebih dulu lalu interface-nya.
- Hindari menampilkan traceback atau detail internal kepada client.
- Dokumentasikan error response dan status HTTP.
- Semua endpoint sensitif memerlukan autentikasi dan otorisasi.
- Penghapusan fisik data operasional tidak disediakan melalui API; gunakan arsip (`archived_at`).

## 4. Kontrak API Minimum

Detail request/response ada di `docs/API_SPEC.md` dan skema OpenAPI. Berikut daftar minimum endpoint.

### Authentication

- `GET /api/v1/auth/csrf/` — mengembalikan token CSRF (juga mengatur cookie CSRF).
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/` — identitas, peran, dan daftar permission efektif pengguna.
- `POST /api/v1/auth/password/change/` — ganti password sendiri; wajib password lama.

Login menggunakan mekanisme session Django yang aman. Endpoint perubahan state dilindungi CSRF; client mengirim token melalui header `X-CSRFToken` dan menyimpan token di memori aplikasi, bukan local storage. Logout mengakhiri sesi server-side. Akun nonaktif ditolak.

### Users dan Roles

- `GET /api/v1/users/`
- `POST /api/v1/users/`
- `GET /api/v1/users/{id}/`
- `PATCH /api/v1/users/{id}/` — termasuk menetapkan peran dan `is_active`.
- `POST /api/v1/users/{id}/reset-password/` — administrator menetapkan password sementara.
- `GET /api/v1/roles/` — daftar peran (read-only).

Pengguna tidak dihapus fisik; gunakan penonaktifan. Perubahan peran, penonaktifan, dan reset password menghasilkan audit event.

### Assets

- `GET /api/v1/assets/`
- `POST /api/v1/assets/`
- `GET /api/v1/assets/{id}/`
- `PATCH /api/v1/assets/{id}/`
- `POST /api/v1/assets/{id}/archive/` dan `POST /api/v1/assets/{id}/restore/`

Tidak ada `DELETE` fisik. Field awal aset:

- `id`
- `name` (wajib; unik di antara aset aktif tanpa membedakan huruf besar/kecil)
- `asset_type`
- `manufacturer` (opsional)
- `model` (opsional)
- `serial_number` (opsional; unik di antara aset aktif bila diisi)
- `status`
- `location`
- `description` (opsional)
- `archived_at`
- `created_at`, `updated_at`

### Interfaces

- `GET /api/v1/interfaces/` (filter: `asset`)
- `POST /api/v1/interfaces/`
- `GET /api/v1/interfaces/{id}/`
- `PATCH /api/v1/interfaces/{id}/`
- `POST /api/v1/interfaces/{id}/archive/` dan `/restore/`

Nama interface unik per aset di antara interface aktif. Interface yang masih memiliki koneksi atau alokasi IP aktif tidak dapat diarsipkan sebelum relasinya dilepas.

### Locations

- `GET /api/v1/locations/`
- `POST /api/v1/locations/`
- `GET /api/v1/locations/{id}/`
- `PATCH /api/v1/locations/{id}/`
- `POST /api/v1/locations/{id}/archive/` dan `/restore/`

Lokasi yang masih dipakai aset aktif tidak dapat diarsipkan.

### IPAM

- `/api/v1/subnets/` (list, create, detail, patch, `archive`, `restore`)
- `/api/v1/ip-addresses/` (list, create, detail, patch, `release`)

Subnet menyimpan CIDR, gateway opsional (hanya informasi), `vlan` opsional (`id` baris VLAN aktif, bukan `vlan_number`), deskripsi, dan status. IP address menyimpan alamat, subnet, status alokasi, serta relasi aset/interface opsional. Endpoint harus menolak alamat yang tidak sesuai subnet, alokasi ganda, dan subnet overlap (lihat bagian 7).

### VLANs

- `/api/v1/vlans/` (list, create, detail, patch, `archive`, `restore`)

Simpan nomor VLAN (`vlan_number`), nama, deskripsi, dan status. Rentang valid: 1–4094, kecuali 1002–1005 (ditolak); VLAN 1 diizinkan. Keunikan `vlan_number`: unik di antara VLAN aktif (satu domain lab pada MVP); perubahan hanya melalui ADR baru. VLAN yang masih dirujuk subnet aktif tidak dapat diarsipkan (`409 has_dependents`).

### Connections

- `/api/v1/connections/` (list, create, detail, patch, `archive`, `restore`)

Koneksi adalah relasi **tak berarah**. Client mengirim dua interface (`interface_a`, `interface_b`) dalam urutan apa pun; backend menormalisasi sehingga `interface_a_id < interface_b_id`. Tolak koneksi ke interface yang sama dan ke interface yang tidak ada atau diarsipkan. Constraint database: CHECK `interface_a_id < interface_b_id` dan unique pada pasangan aktif. Simpan juga tipe koneksi dan metadata yang relevan.

Satu interface hanya boleh memiliki satu koneksi aktif bertipe fisik (`ethernet`, `fiber`, `console`); tipe `wireless` dan `virtual` tidak dibatasi. Pelanggaran dikembalikan sebagai `409 interface_in_use`. Aturan ini ditegakkan di database (tabel klaim yang diisi trigger), bukan hanya pemeriksaan di service. Aplikasi tidak boleh menulis ke tabel klaim.

### Incidents

- `/api/v1/incidents/`
- `GET /api/v1/incidents/{id}/events/`
- `POST /api/v1/incidents/{id}/events/`

Field inti: judul, deskripsi, severity, status, assignee, aset terkait (`asset`, opsional), waktu pembuatan, waktu pembaruan. Perubahan status/assignee harus menghasilkan event historis. Event bersifat append-only bagi pengguna biasa.

### Imports (CSV)

- `POST /api/v1/imports/{resource}/` — `multipart/form-data` dengan field `file` dan `mode` (`preview` atau `commit`).

`{resource}` ∈ `locations`, `assets`, `subnets`, `ip-addresses`. Aturan impor ada di bagian 8.

### Dashboard

- `GET /api/v1/dashboard/summary/`

Mengembalikan jumlah aset, subnet, IP tercatat, dan insiden terbuka, dihitung dari data aktual dan hanya mencakup resource yang boleh dilihat pengguna. Daftar perubahan terbaru disertakan hanya bila pengguna berhak membaca audit.

### Audit

- `GET /api/v1/audit-events/`

Endpoint hanya untuk peran yang berwenang. Tidak menyediakan endpoint update/delete audit bagi pengguna biasa.

### Health

- `GET /api/v1/health/` — status layanan dan koneksi database, tanpa detail internal; dipakai health check deployment.

## 5. Format Respons, Pagination, dan Error

### Pagination dan filter

Semua endpoint koleksi memakai page-number pagination:

- Parameter: `page` (mulai 1) dan `page_size` (default 25, maksimum 100).
- Respons:

```json
{
  "count": 120,
  "next": "https://host/api/v1/assets/?page=2",
  "previous": null,
  "results": []
}
```

- Pencarian memakai `search`, pengurutan memakai `ordering` (hanya field yang diizinkan), filter memakai nama field yang didokumentasikan. Parameter tak dikenal ditolak dengan `400`, bukan diabaikan diam-diam.
- Data arsip disembunyikan secara default; gunakan `include_archived=true` (butuh permission yang sesuai).

### Error

Error menggunakan format konsisten:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Data tidak valid.",
    "details": {
      "name": ["Nama aset sudah digunakan."]
    }
  }
}
```

Pemetaan status minimum:

- `200`: sukses dengan body.
- `201`: resource dibuat.
- `204`: sukses tanpa body.
- `400`: input tidak valid.
- `401`: belum terautentikasi.
- `403`: tidak diizinkan.
- `404`: resource tidak ditemukan atau keberadaannya tidak boleh diungkap.
- `409`: konflik state/data, misalnya alokasi IP ganda, subnet overlap, koneksi fisik kedua pada interface yang sama, atau pengarsipan objek yang masih memiliki relasi aktif.
- `413`: file impor melebihi batas ukuran.
- `429`: rate limit terlampaui.

Jangan mengembalikan detail exception, query SQL, stack trace, atau secret ke client.

### Rate limiting

Kebijakan default (dapat dikonfigurasi melalui settings, bukan hard-coded di view):

| Scope | Batas default |
| --- | --- |
| Login | 5 percobaan per menit per IP, dan per username |
| Ganti/reset password | 5 per menit per pengguna |
| Impor CSV | 10 per jam per pengguna |
| Request tulis lainnya | 120 per menit per pengguna |
| Request baca | 300 per menit per pengguna |

Respons `429` menyertakan `Retry-After`. Perilaku throttle diuji otomatis untuk login.

## 6. Model Data dan Constraint

Definisi tabel, tipe, enum, indeks, dan constraint lengkap ada di `docs/DATA_MODEL.md`. Ringkasan di sini adalah persyaratan minimum.

### User / Role / Permission

Custom user model sejak migrasi pertama. Peran = Django Group; permission = permission eksplisit per aksi.

### Location

Field minimum: id, name, location_type, description, archived_at, created_at, updated_at.

### Asset

Field minimum: id, name, asset_type, manufacturer, model, serial_number, status, location_id, description, archived_at, created_at, updated_at.

### NetworkInterface

Field minimum: id, asset_id, name, mac_address opsional, description, archived_at. Unik `(asset_id, name)` pada baris aktif.

### Subnet

Field minimum: id, cidr, gateway opsional, vlan_id opsional (FK ke `vlans_vlan.id`, VLAN aktif), description, status, archived_at, created_at, updated_at. Simpan CIDR dengan tipe PostgreSQL `cidr`. Subnet aktif tidak boleh overlap (bagian 7).

### IPAddress

Field minimum: id, address (`inet`), subnet_id, status, interface_id opsional, asset_id opsional, description, archived_at. Unique `(subnet_id, address)` pada baris aktif. Pelepasan alamat mengarsipkan alokasi (`archived_at` terisi, status `released`) dan menghasilkan audit event.

### VLAN

Field minimum: id, vlan_number (nomor VLAN), name, description, status, archived_at. Unik `vlan_number` pada baris aktif; nilai 1002–1005 ditolak.

### Connection

Field minimum: id, interface_a_id, interface_b_id, connection_type, description, archived_at, created_at. CHECK `interface_a_id < interface_b_id`; unique `(interface_a_id, interface_b_id)` pada baris aktif. Klaim koneksi fisik disimpan di tabel `connections_interfaceclaim` yang hanya diisi trigger.

### Incident dan IncidentEvent

Incident menyimpan status terkini dan `asset_id` opsional; IncidentEvent menyimpan catatan historis. Perubahan status/assignee penting harus menghasilkan event.

### AuditEvent

Field minimum: id, actor_id (nullable untuk aksi sistem atau login gagal), actor_username (salinan username saat kejadian), action, object_type, object_id, timestamp, safe_metadata. Jangan menyimpan credential atau token. Tidak ada foreign key yang menghapus audit saat objek diarsipkan.

## 7. IPAM — Aturan Bisnis

1. Parse dan validasi alamat menggunakan tipe jaringan yang sesuai.
2. Pastikan alamat berada dalam subnet yang dipilih. Validasi ini dilakukan di service di dalam transaksi, karena constraint database tidak dapat merujuk tabel lain tanpa trigger.
3. Network address dan broadcast IPv4 ditolak, kecuali pada subnet `/31` dan `/32`. Alamat gateway harus berada dalam subnet. Reserved addresses lain didefinisikan di `docs/DATA_MODEL.md`.
4. IPv6 tidak boleh diproses menggunakan asumsi broadcast IPv4.
5. **Subnet overlap ditolak** di antara subnet aktif (satu domain jaringan pada MVP). Tegakkan dengan exclusion constraint PostgreSQL: GiST pada kolom `cidr` dengan operator `&&` dan operator class `inet_ops`, dibatasi `WHERE archived_at IS NULL`. Di Django gunakan `ExclusionConstraint` dengan `django.contrib.postgres`. Verifikasi dukungan operator class pada versi PostgreSQL yang dipakai. Extension `btree_gist` hanya diperlukan bila constraint kelak digabung dengan kolom berkesetaraan (misalnya kolom domain/VRF).
6. **Keunikan IP:** unik per `(subnet_id, address)` pada baris aktif. Aturan 2 dan 5 harus berlaku bersamaan: karena alamat wajib berada di subnetnya dan subnet aktif tidak overlap, alamat aktif efektif unik di seluruh lab. Unique per subnet saja tidak cukup tanpa kedua aturan tersebut.
7. Mengubah CIDR subnet yang masih memiliki alokasi aktif ditolak; subnet harus dikosongkan atau dibuat ulang. Mengubah gateway divalidasi ulang terhadap subnet.
8. Gunakan transaksi, lock baris subnet (`select_for_update`), unique index, dan trigger penjaga database untuk menangani race condition. Trigger memegang kunci `FOR SHARE` pada induk sehingga penulisan dari luar service tetap aman.
9. Konflik dikembalikan sebagai error yang konsisten dengan HTTP `409` dan kode seperti `ip_conflict` atau `subnet_overlap`.
10. Alokasi, perubahan, dan pelepasan alamat harus menghasilkan audit event.
11. Jangan menganggap alamat yang tercatat berarti host sedang aktif.
12. Dukungan multi-VRF/domain jaringan di luar MVP; menambahkannya membutuhkan ADR dan migrasi terencana.
13. Gateway subnet hanya informasi; tidak otomatis dibuat atau dianggap sebagai alokasi IP.

## 8. Impor CSV — Aturan

- Resource: `locations`, `assets`, `subnets`, `ip-addresses`. Template CSV per resource didokumentasikan di `docs/API_SPEC.md`.
- Format: UTF-8, baris pertama header, pemisah koma. Batas default: 2 MB dan 1.000 baris per file (dapat dikonfigurasi).
- Permission impor dipisah per resource dan diberikan eksplisit (lihat `docs/RBAC_MATRIX.md`).
- Urutan ketergantungan: lokasi → aset → subnet → alamat IP. Referensi antar-resource memakai nama atau kunci alami yang didefinisikan di template; referensi yang tidak ditemukan menjadi error baris. VLAN tidak dapat diimpor pada MVP; kolom `vlan` pada CSV subnet berisi `vlan_number` dari VLAN yang sudah ada dan aktif; nilai yang tidak ditemukan menjadi error baris.
- `mode=preview`: validasi semua baris dengan aturan yang sama seperti API biasa, **tanpa menyimpan**. Respons berisi ringkasan (jumlah baris, valid, error) dan daftar error per baris (nomor baris, kolom, kode, pesan).
- `mode=commit`: validasi ulang seluruh baris (preview tidak dipercaya), lalu simpan semua dalam satu transaksi. Jika ada satu error, tidak ada yang tersimpan (all-or-nothing).
- Impor memakai service modul domain, bukan menulis ke tabel langsung, sehingga constraint, validasi, dan audit identik dengan jalur API biasa.
- File tidak disimpan setelah selesai diproses. Nilai sel yang diawali `=`, `+`, `-`, atau `@` diperlakukan sebagai teks biasa dan tidak pernah dievaluasi.
- Audit: satu event `import.commit` per commit dengan metadata aman (resource, jumlah baris, hasil), ditambah audit event per objek bila kebijakan di `docs/DATA_MODEL.md` mewajibkannya.

## 9. RBAC

Peran diimplementasikan sebagai Django Groups: `administrator`, `lab_manager`, `lab_assistant`, `viewer`. Matriks di bawah adalah ringkasan; **matriks permission per aksi** (codename, object-level, dan aturan "sesuai izin") didefinisikan di `docs/RBAC_MATRIX.md`.

| Resource/aksi | Admin | Lab Manager | Lab Assistant | Viewer |
| --- | --- | --- | --- | --- |
| Melihat aset dan jaringan | Ya | Ya | Ya | Ya |
| Membuat/mengubah/mengarsipkan aset, lokasi, interface | Ya | Ya | Sesuai permission | Tidak |
| Mengelola user/role | Ya | Tidak | Tidak | Tidak |
| Mengelola IPAM/VLAN/koneksi | Ya | Ya | Sesuai permission | Tidak |
| Membuat/memperbarui insiden | Ya | Ya | Ya | Tidak |
| Impor CSV | Ya | Ya | Tidak secara default | Tidak |
| Membaca audit log | Ya | Ya | Tidak | Tidak |
| Mengubah/menghapus audit event | Tidak melalui UI/API | Tidak | Tidak | Tidak |

Aturan:

- "Sesuai permission" berarti hanya aksi yang secara eksplisit diberikan di `RBAC_MATRIX.md`; tanpa pemberian, aksi ditolak.
- Viewer melihat semua resource operasional; cakupan yang lebih sempit hanya berlaku bila ditulis eksplisit di `RBAC_MATRIX.md`.
- Pembacaan audit oleh Lab Manager adalah keputusan default dokumen ini; ubah melalui `RBAC_MATRIX.md` dan ADR bila kebijakan lab berbeda.
- Akses ke data dan aksi harus diuji melalui request API, bukan hanya melalui UI.
- Endpoint `GET /api/v1/auth/me/` mengembalikan permission efektif agar UI dapat menyesuaikan tampilan tanpa menggantikan otorisasi backend.

## 10. Audit — Event Wajib

Nama event berformat `<resource>.<aksi>`. Event berikut wajib dicatat:

| Kelompok | Event |
| --- | --- |
| Auth | `auth.login_success`, `auth.login_failed`, `auth.logout`, `auth.password_changed` |
| User | `user.created`, `user.updated`, `user.deactivated`, `user.reactivated`, `user.role_changed`, `user.password_reset` |
| Aset dan lokasi | `asset.created`, `asset.updated`, `asset.archived`, `asset.restored`; sama untuk `location.*` dan `interface.*` |
| IPAM | `subnet.created`, `subnet.updated`, `subnet.archived`, `subnet.restored`, `ip.allocated`, `ip.updated`, `ip.released` |
| VLAN dan koneksi | `vlan.*` dan `connection.*` (created, updated, archived, restored) |
| Insiden | `incident.created`, `incident.updated`, `incident.status_changed`, `incident.assigned`, `incident.event_added` |
| Impor | `import.commit` |

Ketentuan: catat aktor (kosong untuk login gagal dengan username tidak dikenal), objek, waktu, dan `safe_metadata` berisi perubahan field non-sensitif. Jangan mencatat password, token, session ID, atau isi file CSV. `incident.updated` dicatat saat judul, deskripsi, severity, atau aset terkait berubah; `safe_metadata.changed_fields` hanya berisi nama field dari himpunan `title`, `description`, `severity`, `asset`, tanpa isi judul/deskripsi. Setiap event wajib memiliki test.

## 11. Security Requirements

- Session authentication untuk browser MVP.
- CSRF protection untuk request yang mengubah state.
- Cookie `HttpOnly`; `Secure` pada HTTPS; `SameSite` sesuai deployment.
- HTTPS untuk akses melalui jaringan.
- Password hashing bawaan Django yang terkonfigurasi dengan benar, serta validator kekuatan password.
- Validasi server-side dan ORM.
- Permission pada endpoint dan object level.
- Rate limiting sesuai bagian 5.
- Secret hanya melalui environment/secret store.
- Dua role database: pemilik skema (migrasi, backup/restore) dan runtime aplikasi. Role runtime tidak memiliki tabel, tidak memiliki hak `DELETE`/`TRUNCATE` pada data operasional (kecuali tabel sesi dan relasi peran), tidak dapat mengubah `audit_auditevent` atau `incidents_incidentevent`, dan tidak dapat menonaktifkan trigger.
- `.env` tidak masuk version control; sediakan `.env.example` tanpa secret.
- Database hanya dapat diakses dari jaringan layanan yang diperlukan.
- Log tidak boleh mengandung password, token, session ID, cookie, private key, atau secret.
- Batas ukuran dan baris untuk unggahan CSV.
- Backup dibatasi aksesnya dan dilindungi sesuai risiko.
- Jangan melakukan network scanning atau remote command execution dalam MVP.

## 12. Frontend Requirements

- TypeScript strict mode.
- Struktur berbasis fitur/domain.
- API client terpusat yang menangani token CSRF, pagination, dan format error seragam.
- Tipe request/response konsisten dengan OpenAPI.
- Status loading, empty, success, dan error ditangani pada tiap alur.
- Form menampilkan error per field.
- Pagination/filter berjalan di server untuk koleksi.
- Alur impor CSV: unggah → preview dengan error per baris → konfirmasi commit.
- Permission UI membantu pengalaman pengguna tetapi tidak menggantikan backend authorization.
- Jangan menyimpan password, token, atau secret di local storage.
- Aksesibilitas dasar: label form, navigasi keyboard, fokus terlihat, dan kontras.

## 13. Testing Requirements

### Backend

- Unit tests untuk aturan domain.
- API tests untuk validasi, status HTTP, authentication, dan permission.
- Integration tests untuk relasi dan constraint database (unique parsial, exclusion subnet, CHECK koneksi).
- Concurrency test untuk alokasi IP pada database PostgreSQL yang sama dengan target.
- Concurrency test dengan dua transaksi paralel untuk: IP vs perubahan/arsip subnet, dua koneksi fisik pada satu interface, koneksi vs arsip interface, interface/IP vs arsip aset, subnet→VLAN vs arsip VLAN, aset vs arsip lokasi.
- Tests hak akses: role runtime tidak dapat `DELETE`, `TRUNCATE`, mengubah audit, atau menonaktifkan trigger.
- Tests untuk setiap audit event wajib dan larangan akses/ubah audit.
- Tests impor CSV: preview tidak menyimpan, commit atomik, validasi ulang saat commit, error per baris.
- Tests rate limiting login.

### Frontend

- Unit/component tests untuk form, tabel, state, dan error handling.
- Tests untuk alur login dan operasi CRUD utama.
- Tests untuk alur impor CSV.
- Pemeriksaan TypeScript, lint, dan build.

### Security checks

- Uji akses lintas peran.
- Uji CSRF/session behavior.
- Uji input invalid dan object ID yang tidak berhak diakses.
- Dependency scanning dan secret scanning.
- Verifikasi tidak ada secret pada log atau response error.

## 14. Deployment Requirements

- Linux server yang disetujui.
- Reverse proxy dengan HTTPS.
- Frontend statis dan backend application server.
- PostgreSQL tidak diekspos ke publik.
- Persistent volume database.
- Health check untuk layanan (`/api/v1/health/`).
- Environment terpisah untuk development dan production.
- Migrasi dijalankan secara terkontrol.
- Backup terjadwal, retensi, akses terbatas, dan restore drill.
- Migrasi dan restore dijalankan dengan role pemilik skema; aplikasi berjalan dengan role runtime.
- Verifikasi Compose provider sebelum implementasi.
- Jangan menghapus volume database pada proses rebuild/redeploy.

## 15. Environment Variables

Nama final mengikuti konfigurasi yang dibuat, tetapi minimal mencakup:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL` (role runtime) dan `DATABASE_MIGRATION_URL` (role pemilik skema, hanya untuk migrasi)
- `CSRF_TRUSTED_ORIGINS`
- `TIME_ZONE`
- batas rate limiting dan batas impor CSV (dengan nilai default dari spec ini)
- konfigurasi reverse proxy/HTTPS sesuai deployment

`.env.example` hanya berisi nilai contoh non-rahasia. Production secret harus dibuat secara aman dan tidak boleh menggunakan nilai contoh.

## 16. Quality Gates per Fase

### Phase 0 — Foundation

- `docs/DATA_MODEL.md`, `docs/RBAC_MATRIX.md`, `docs/API_SPEC.md`, `docs/ADR.md`, `docs/SECURITY.md`, `docs/DEPLOYMENT.md`, dan `docs/VERSIONS.md` selesai dan dicek konsistensinya dengan `prd.md`, `design.md`, dan `spec.md`.
- Repository dan toolchain diaudit.
- Compose provider terverifikasi.
- Baseline PostgreSQL 16 dan Django 5.2 LTS (ADR-021); versi patch dan dependency dikunci setelah pemeriksaan kompatibilitas.
- Struktur dokumen dan keputusan teknis disepakati.
- Lint/test/build minimal berjalan.

### Phase 1 — Backend foundation

- Custom user model, migrasi, dan seed peran/permission berjalan.
- Auth, CSRF, permission, error format, pagination, rate limiting, dan OpenAPI tersedia.
- Dua role database dan hak aksesnya terpasang dan diuji.
- Test akses dasar lulus.

### Phase 2 — Assets, locations, dan IPAM

- Model dan constraint tersedia (unique parsial, exclusion subnet).
- Validasi subnet/IP diuji.
- Konflik alokasi dan overlap ditangani, termasuk uji konkurensi.
- Trigger penjaga dan tabel klaim koneksi diuji dengan transaksi paralel.

### Phase 3 — VLAN, connections, incidents, audit, imports

- Relasi dan event historis tervalidasi.
- Semua audit event wajib tercatat dan diuji.
- Impor CSV (preview dan commit atomik) tervalidasi.
- Akses lintas peran diuji.

### Phase 4 — Frontend

- Alur utama berjalan dari browser ke API, termasuk dashboard dan impor CSV.
- Semua state dan error utama ditangani.
- Build production lulus.

### Phase 5 — Hardening dan release

- Test suite lulus.
- Backup/restore diverifikasi.
- Deployment dan dokumentasi pengguna selesai.
- Acceptance criteria PRD dipenuhi.

## 17. Aturan Kerja untuk Coding Agent

1. Baca `prd.md`, `design.md`, `spec.md`, dan seluruh dokumen di `docs/` sebelum mengubah kode.
2. Mulai dengan audit repository; jangan menimpa file atau konfigurasi yang sudah ada tanpa pemeriksaan.
3. Kerjakan satu fase dalam satu waktu.
4. Jangan menambahkan fitur di luar fase tanpa persetujuan.
5. Jangan mengganti stack yang disepakati tanpa mengajukan alasan dan dampak.
6. Jangan membuat credential atau data lab nyata secara asumtif.
7. Jangan menjalankan pemindaian jaringan atau mengakses perangkat nyata.
8. Tambahkan test untuk perubahan perilaku dan aturan bisnis.
9. Jalankan lint, typecheck, test, dan build yang relevan sebelum menyatakan fase selesai.
10. Laporkan file yang diubah, keputusan yang dibuat, perintah yang dijalankan, hasil test, risiko tersisa, dan blocker.
11. Jangan mengklaim test lulus jika belum dijalankan.
12. Jika spesifikasi ambigu, bertentangan antar dokumen, atau konflik dengan repository, berhenti pada titik tersebut dan laporkan opsi sebelum membuat perubahan destruktif.
13. Jangan membuat model Django atau migrasi sebelum `docs/DATA_MODEL.md` dan kebijakan IPAM final.
14. Jangan menulis langsung ke `connections_interfaceclaim`; tabel ini hanya diisi trigger.

## 18. Catatan Revisi 1.1

- Tambah endpoint: `auth/csrf`, `auth/password/change`, `users`, `roles`, `interfaces`, `imports`, `dashboard/summary`, `health`, serta aksi `archive`/`restore`/`release`.
- Tambah relasi insiden–aset, `archived_at`, dan koneksi tak berarah ternormalisasi (`interface_a`/`interface_b`).
- Tetapkan: pagination page-number, kebijakan rate limiting, daftar audit event wajib, aturan impor CSV, keunikan IP + larangan subnet overlap, RBAC via Django Groups.
- Struktur repository: tambah `locations/` dan `imports/`; tiga dokumen utama di root, dokumen rinci di `docs/`.
- Phase 0 menambah gate dokumentasi.

## 19. Catatan Revisi 1.2

- Putuskan: `subnet.vlan` opsional, satu koneksi fisik aktif per interface, `name` sebagai nama field aset, VLAN 1002–1005 ditolak, gateway hanya informasi, event audit `incident.updated`.
- Tambah: aturan isolation level, urutan kunci, pemetaan error berdasarkan nama constraint, dua role database (`DATABASE_MIGRATION_URL`), dan uji konkurensi/hak akses.

## 20. Catatan Revisi 1.3

- Ganti nama nomor VLAN menjadi `vlan_number` (database dan API); `subnet.vlan` merujuk id baris VLAN.
- Tetapkan baseline PostgreSQL 16 dan Django 5.2 LTS; patch dan dependency dikunci pada Phase 0.
- Tegaskan: VLAN tidak diimpor CSV; kolom `vlan` pada CSV subnet berisi `vlan_number`.
- Tambah `docs/VERSIONS.md` pada struktur repository dan gate Phase 0.
