# NetLab Manager — RBAC Matrix

**Versi:** 1.2 (U-04 dikonfirmasi; belum diuji)
**Tanggal:** 26 Oktober 2026
**Sumber:** `prd.md`, `design.md`, `spec.md` v1.3 (spec §9), `docs/DATA_MODEL.md` v1.2 (4.1, 9, A-12, A-18, A-19)
**Status:** Dokumentasi saja. Belum ada implementasi dan belum ada pengujian terhadap dokumen ini.

## 1. Kedudukan dokumen

Dokumen ini adalah sumber tunggal permission per aksi dan per peran. `spec.md` §9 hanya memberi ringkasan. Jika bertentangan dengan `spec.md`, laporkan dan berhenti.

Penanda:

- **D**: sudah ditetapkan dokumen utama.
- **U-xx**: keputusan dokumen ini di luar yang ditetapkan dokumen utama; statusnya ada di bagian 7.

## 2. Prinsip

1. **Deny by default.** Aksi tanpa permission eksplisit ditolak.
2. **Permission hanya pada Group, tidak pernah langsung pada pengguna.** Peran = Django Group (`administrator`, `lab_manager`, `lab_assistant`, `viewer`). Tepat satu peran per pengguna (A-12).
3. **Tidak ada permission `delete_*`.** Django membuat `delete_<model>` otomatis; tidak boleh diberikan ke Group mana pun, dan uji memastikannya (bagian 8).
4. **Penegakan di backend.** Menyembunyikan tombol di frontend bukan kontrol keamanan. `GET /api/v1/auth/me/` mengembalikan permission efektif hanya untuk tampilan.
5. **`is_superuser` tidak dipakai untuk peran.** Akun superuser hanya untuk bootstrap/darurat (DATA_MODEL bagian 9).
6. **Respons penolakan:** `401 unauthenticated` bila belum login; `403 permission_denied` bila login tetapi tidak berhak. `404 not_found` hanya untuk objek yang tidak ada (atau terarsip bagi yang tidak berhak melihat arsip, 6.2). Keberadaan resource tidak dianggap rahasia (U-06).

## 3. Daftar permission

Format `app.codename`. Permission kustom (selain `view/add/change`) didefinisikan lewat `Meta.permissions` saat implementasi.

| App | Codename | Arti |
| --- | --- | --- |
| `accounts` | `view_user` | Melihat daftar/detail pengguna dan daftar peran |
| `accounts` | `add_user` | Membuat pengguna |
| `accounts` | `change_user` | Mengubah nama, email, dan `is_active` |
| `accounts` | `change_role_user` | Menetapkan atau mengganti peran pengguna |
| `accounts` | `reset_password_user` | Mereset password pengguna lain |
| `locations` | `view_location`, `add_location`, `change_location`, `archive_location`, `restore_location` | CRUD lokasi tanpa hapus fisik |
| `assets` | `view_asset`, `add_asset`, `change_asset`, `archive_asset`, `restore_asset` | Aset |
| `assets` | `view_networkinterface`, `add_networkinterface`, `change_networkinterface`, `archive_networkinterface`, `restore_networkinterface` | Interface |
| `ipam` | `view_subnet`, `add_subnet`, `change_subnet`, `archive_subnet`, `restore_subnet` | Subnet |
| `ipam` | `view_ipaddress` | Melihat alamat IP |
| `ipam` | `add_ipaddress` | Mengalokasikan alamat IP |
| `ipam` | `change_ipaddress` | Mengubah status `allocated`/`reserved`, deskripsi, aset, interface |
| `ipam` | `release_ipaddress` | Melepas alokasi |
| `vlans` | `view_vlan`, `add_vlan`, `change_vlan`, `archive_vlan`, `restore_vlan` | VLAN |
| `connections` | `view_connection`, `add_connection`, `change_connection`, `archive_connection`, `restore_connection` | Koneksi |
| `incidents` | `view_incident` | Melihat insiden dan event-nya |
| `incidents` | `add_incident` | Membuat insiden |
| `incidents` | `change_incident` | Mengubah judul, deskripsi, severity, aset terkait |
| `incidents` | `change_status_incident` | Mengubah status insiden |
| `incidents` | `assign_incident` | Mengubah assignee |
| `incidents` | `add_incidentevent` | Menambah catatan (event `note`) |
| `audit` | `view_auditevent` | Membaca audit log |
| `imports` | `import_locations`, `import_assets`, `import_subnets`, `import_ipaddresses` | Preview dan commit impor CSV per resource |

Total 50 permission. `imports` tidak punya model; permission-nya dipasang pada model penampung tak terkelola (detail implementasi, ditentukan di Phase 1).

## 4. Matriks peran

`✓` = diberikan. `—` = tidak diberikan. Kolom "Dasar" menunjuk D (spec §9) atau usulan U-xx.

### 4.1 Akun dan audit

| Permission | administrator | lab_manager | lab_assistant | viewer | Dasar |
| --- | --- | --- | --- | --- | --- |
| `view_user`, `add_user`, `change_user`, `change_role_user`, `reset_password_user` | ✓ | — | — | — | D |
| `view_auditevent` | ✓ | ✓ | — | — | D (spec §9); U-02 |
| Mengubah/menghapus audit event | — | — | — | — | D (tidak ada permission) |

### 4.2 Data operasional

| Resource | Permission | administrator | lab_manager | lab_assistant | viewer | Dasar |
| --- | --- | --- | --- | --- | --- | --- |
| Lokasi | `view_location` | ✓ | ✓ | ✓ | ✓ | D |
| Lokasi | `add_`, `change_`, `archive_`, `restore_location` | ✓ | ✓ | — | — | D; U-01 |
| Aset | `view_asset` | ✓ | ✓ | ✓ | ✓ | D |
| Aset | `change_asset` | ✓ | ✓ | ✓ | — | U-01 |
| Aset | `add_`, `archive_`, `restore_asset` | ✓ | ✓ | — | — | D; U-01 |
| Interface | `view_networkinterface` | ✓ | ✓ | ✓ | ✓ | D |
| Interface | `change_networkinterface` | ✓ | ✓ | ✓ | — | U-01 |
| Interface | `add_`, `archive_`, `restore_networkinterface` | ✓ | ✓ | — | — | D; U-01 |
| Subnet | `view_subnet` | ✓ | ✓ | ✓ | ✓ | D |
| Subnet | `add_`, `change_`, `archive_`, `restore_subnet` | ✓ | ✓ | — | — | D; U-01 |
| Alamat IP | `view_ipaddress` | ✓ | ✓ | ✓ | ✓ | D |
| Alamat IP | `change_ipaddress` | ✓ | ✓ | ✓ | — | U-01 |
| Alamat IP | `add_ipaddress`, `release_ipaddress` | ✓ | ✓ | — | — | D; U-01 |
| VLAN | `view_vlan` | ✓ | ✓ | ✓ | ✓ | D |
| VLAN | `add_`, `change_`, `archive_`, `restore_vlan` | ✓ | ✓ | — | — | D; U-01 |
| Koneksi | `view_connection` | ✓ | ✓ | ✓ | ✓ | D |
| Koneksi | `change_connection` | ✓ | ✓ | ✓ | — | U-01 |
| Koneksi | `add_`, `archive_`, `restore_connection` | ✓ | ✓ | — | — | D; U-01 |

### 4.3 Insiden dan impor

| Permission | administrator | lab_manager | lab_assistant | viewer | Dasar |
| --- | --- | --- | --- | --- | --- |
| `view_incident` | ✓ | ✓ | ✓ | ✓ | D |
| `add_incident`, `change_incident`, `change_status_incident`, `add_incidentevent` | ✓ | ✓ | ✓ | — | D (spec §9: asisten menangani insiden) |
| `assign_incident` | ✓ | ✓ | — | — | U-04 |
| `import_locations`, `import_assets`, `import_subnets`, `import_ipaddresses` | ✓ | ✓ | — | — | D (spec §9: asisten "tidak secara default"); U-03 |

### 4.4 Jumlah

| Peran | Permission |
| --- | --- |
| administrator | 50 |
| lab_manager | 45 (semua kecuali lima permission `accounts`) |
| lab_assistant | 16 (8 `view_*` operasional, 4 `change_*` data, 4 insiden: `add_incident`, `change_incident`, `change_status_incident`, `add_incidentevent`) |
| viewer | 8 (`view_*` operasional) |

`view_*` operasional: lokasi, aset, interface, subnet, IP, VLAN, koneksi, insiden.

### 4.5 Daftar eksplisit per peran (acuan seed dan uji)

Notasi ringkas pada 4.1–4.3 (misalnya `add_`, `change_`) hanya untuk keterbacaan. **Daftar di bawah adalah acuan untuk seed Group dan uji 8.3**; bila berbeda dari 4.1–4.3, daftar ini menang dan perbedaannya dilaporkan.

**administrator (50):** semua permission di bagian 3.

**lab_manager (45):** semua permission di bagian 3 kecuali `accounts.view_user`, `accounts.add_user`, `accounts.change_user`, `accounts.change_role_user`, `accounts.reset_password_user`.

**lab_assistant (16):**
`locations.view_location`; `assets.view_asset`, `assets.change_asset`, `assets.view_networkinterface`, `assets.change_networkinterface`; `ipam.view_subnet`, `ipam.view_ipaddress`, `ipam.change_ipaddress`; `vlans.view_vlan`; `connections.view_connection`, `connections.change_connection`; `incidents.view_incident`, `incidents.add_incident`, `incidents.change_incident`, `incidents.change_status_incident`, `incidents.add_incidentevent`.

**viewer (8):**
`locations.view_location`, `assets.view_asset`, `assets.view_networkinterface`, `ipam.view_subnet`, `ipam.view_ipaddress`, `vlans.view_vlan`, `connections.view_connection`, `incidents.view_incident`.

## 5. Pemetaan aksi API ke permission

Ringkasan; kontrak lengkap di `docs/API_SPEC.md`.

| Aksi | Permission |
| --- | --- |
| `GET` koleksi/detail resource | `view_<model>` |
| `POST` koleksi | `add_<model>` (alokasi IP: `add_ipaddress`; membuat insiden: `add_incident`) |
| `PATCH` detail | `change_<model>`, dengan aturan field pada bagian 6.5 untuk insiden |
| `POST .../archive/`, `POST .../restore/` | `archive_<model>`, `restore_<model>` |
| `POST /ip-addresses/{id}/release/` | `release_ipaddress` |
| `GET/POST /incidents/{id}/events/` | `view_incident` / `add_incidentevent` |
| `POST /imports/{resource}/` (preview dan commit) | `import_<resource>` |
| `GET /audit-events/` | `view_auditevent` |
| `GET /users/`, `/roles/`, `GET /users/{id}/` | `view_user` |
| `POST /users/`, `PATCH /users/{id}/`, `POST /users/{id}/reset-password/` | `add_user`, `change_user` (+ `change_role_user` bila `role` berubah), `reset_password_user` |
| `GET /dashboard/summary/` | Pengguna terautentikasi; isi dibatasi (6.6) |
| `/auth/csrf/`, `/auth/login/`, `/health/` | Tanpa autentikasi |
| `/auth/logout/`, `/auth/me/`, `/auth/password/change/` | Pengguna terautentikasi |

## 6. Aturan khusus

### 6.1 Akun

1. Pengguna tidak dapat mengubah peran sendiri, menonaktifkan akun sendiri, atau mereset password sendiri lewat endpoint admin (gunakan ganti password). Pelanggaran: `409 self_modification_forbidden`.
2. Menonaktifkan atau menurunkan peran administrator aktif terakhir ditolak: `409 last_administrator` (A-19).
3. Akun nonaktif tidak dapat login dan sesi aktifnya tidak dihormati.
4. `reset-password` menetapkan password sementara dan `must_change_password = true`; selama flag aktif, semua endpoint kecuali `me`, `logout`, `password/change` ditolak `403 password_change_required` (U-05).
5. Pengguna dengan `change_role_user` hanya dapat menetapkan salah satu dari empat peran yang terdaftar.

### 6.2 Arsip

Baris terarsip tidak muncul pada daftar. `include_archived=true` dan akses langsung ke baris terarsip hanya untuk pengguna yang memiliki `restore_<model>` resource tersebut (U-07). Pengguna lain mendapat `404 not_found` untuk baris terarsip. IP berstatus `released` diperlakukan sebagai terarsip.

### 6.3 Audit

Tidak ada endpoint tulis untuk audit. Metode selain `GET` mengembalikan `405`. Membaca audit tidak menghasilkan event.

### 6.4 Impor CSV

Preview dan commit membutuhkan permission impor yang sama, dan permission impor **cukup** tanpa `add_<resource>` (U-03). Setiap resource dicek terpisah.

### 6.5 Insiden

Pemeriksaan permission dilakukan **per field yang berubah** pada `PATCH /incidents/{id}/`; bila satu field tidak diizinkan, seluruh request ditolak (`403`) dan tidak ada yang tersimpan:

| Field | Permission |
| --- | --- |
| `title`, `description`, `severity`, `asset` | `change_incident` |
| `status` | `change_status_incident` (dan transisi harus valid, DATA_MODEL 4.9) |
| `assignee` | `assign_incident`; assignee harus pengguna aktif yang memiliki `change_incident` (U-04) |

Insiden berstatus `closed` bersifat read-only termasuk bagi administrator, dan penambahan catatan juga ditolak (`409 incident_closed`) (U-04). Reopen tidak ada pada MVP; bila dibutuhkan kelak, reopen adalah transisi khusus dengan permission dan audit event tersendiri yang harus didefinisikan lebih dulu.

### 6.6 Dashboard

`GET /dashboard/summary/` hanya memuat hitungan untuk resource yang `view_<model>`-nya dimiliki pengguna, dan `recent_changes` hanya bila pengguna memiliki `view_auditevent`. Kunci yang tidak boleh dilihat dihilangkan, bukan dikosongkan.

## 7. Keputusan dan statusnya

Status per 26 Oktober 2026: **U-01 dan U-04 disetujui eksplisit**; U-02, U-03, U-05, U-06, dan U-07 default diterima.

**U-04 dikonfirmasi (27 Oktober 2026):** insiden `closed` read-only untuk **semua peran**, termasuk administrator dan manajer. Tidak ada kemampuan mengubah field maupun menambah catatan pada insiden `closed`. Bila fitur reopen dibutuhkan kelak, reopen diperlakukan sebagai transisi khusus dengan permission dan audit event tersendiri; itu belum didefinisikan dan tidak ada pada MVP.

| ID | Usulan | Alasan |
| --- | --- | --- |
| U-01 | `lab_assistant` hanya mendapat `view_*` operasional dan `change_*` untuk aset, interface, IP, dan koneksi; tanpa `add_*`, `archive_*`, `restore_*`, `release_*`, dan tanpa tulis ke lokasi, subnet, VLAN. Spec §9 hanya menulis "sesuai permission". Opsi tambahan yang dapat diberikan satu per satu: `add_networkinterface`, `add_ipaddress`, `release_ipaddress`, `add_connection`. | Prinsip least privilege; spec §9 menyebut asisten "memperbarui data". |
| U-02 | `lab_manager` boleh membaca audit (default spec §9: "sesuai kebijakan"). | Mengikuti tabel spec §9. |
| U-03 | Permission impor terpisah per resource dan cukup tanpa `add_*`; `lab_assistant` tanpa impor. | Impor adalah operasi massal berisiko; spec §9: tidak secara default. |
| U-04 | Permission insiden dipecah: `change_status_incident` dan `assign_incident`; assignee harus memiliki `change_incident`; insiden `closed` read-only untuk semua. | Spec hanya menyatakan asisten menangani insiden; pemisahan menjaga penugasan tetap di tangan manajer. |
| U-05 | `password_change_required` memblokir endpoint selain `me`, `logout`, `password/change`. | Menutup celah password sementara. |
| U-06 | `403` untuk pengguna terautentikasi tanpa permission, bukan `404`. | Konsistensi dengan spec §5; keberadaan resource bukan rahasia. |
| U-07 | `include_archived` dan akses baris terarsip butuh `restore_<model>`. | Spec §5 menyebut "butuh permission yang sesuai" tanpa menamainya. |

## 8. Persyaratan pengujian

1. **Matriks aksi × peran:** setiap endpoint di `API_SPEC.md` diuji untuk empat peran dan tanpa login; hasil sesuai bagian 4–6 (401/403/2xx).
2. Tidak ada Group yang memiliki permission `delete_*`; uji enumerasi seluruh permission Group.
3. Jumlah permission per Group sama dengan 4.4 dan daftar persisnya sama dengan 4.1–4.3.
4. `PATCH` insiden: uji per field per peran, termasuk penolakan atomik.
5. Uji `include_archived` dan akses langsung ke baris terarsip per peran.
6. Uji aturan akun (6.1): self-modification, administrator terakhir, `must_change_password`.
7. Uji bahwa `me` mengembalikan permission yang sama dengan Group pengguna.
8. Uji akses lewat API langsung, bukan hanya UI (spec §9).

## 9. Seed Group

Group dan permission dibuat lewat data migration setelah dokumen ini disetujui (A-18). Setiap perubahan permission butuh migrasi baru, pembaruan dokumen ini, dan pembaruan uji 8.3.

## 10. Catatan revisi

**1.2:** U-04 dikonfirmasi: `closed` read-only untuk semua peran tanpa edit atau catatan; reopen kelak = transisi khusus.

**1.1:** U-01 s.d. U-07 diputuskan (7); menambah 4.5 (daftar eksplisit per peran).

**1.0:** dokumen awal; menetapkan 50 permission dan matriks empat peran.
