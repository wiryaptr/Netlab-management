# NetLab Manager — API Specification

**Versi:** 1.2 (AP-01 s.d. AP-14 diputuskan; kontrak insiden `closed` dipertegas; belum diuji)
**Tanggal:** 26 Oktober 2026
**Sumber:** `spec.md` v1.3 (§4, §5, §8), `docs/DATA_MODEL.md` v1.2, `docs/RBAC_MATRIX.md` v1.2
**Status:** Dokumentasi saja. Skema OpenAPI yang dihasilkan implementasi harus sesuai dokumen ini; bila berbeda, laporkan dan berhenti. Belum ada bagian dokumen ini yang diuji.

Penanda **AP-xx** menunjuk asumsi/keputusan dokumen ini; statusnya ada di bagian 10.

## 1. Konvensi

| Topik | Aturan |
| --- | --- |
| Base path | `/api/v1/` |
| Format | JSON, UTF-8, nama field `snake_case`. Pengecualian: unggah CSV memakai `multipart/form-data`. |
| ID | Integer (`bigint`). Field relasi memakai nama tanpa `_id` dan berisi id (misalnya `location`, `subnet`, `vlan`). |
| Waktu | ISO 8601 dengan zona waktu (UTC `Z`). |
| Autentikasi | Session cookie. Request pengubah state wajib header `X-CSRFToken`. |
| Metode | `GET`, `POST`, `PATCH`. Tidak ada `PUT` dan tidak ada `DELETE` (AP-05). |
| Kolom umum (read-only) | `id`, `created_at`, `updated_at`, dan `archived_at` bila resource mendukung arsip. |
| Pagination | Semua koleksi: `page` (mulai 1), `page_size` (default 25, maks 100). Respons `{count, next, previous, results}`. |
| Pencarian dan urutan | `search` (field yang didokumentasikan), `ordering` (nama field, awalan `-` untuk turun). Urutan selalu diakhiri `id` sebagai tie-breaker. |
| Parameter tak dikenal | Ditolak `400 invalid_parameter`. |
| Arsip | Baris terarsip disembunyikan. `include_archived=true` hanya untuk pemilik `restore_<model>` (RBAC 6.2). |
| `PATCH` | Parsial. Field yang tidak boleh diubah (disebut "immutable") menghasilkan `400 immutable_field`. |
| Null | Relasi opsional dan identitas opsional berupa `null` bila kosong; teks bebas berupa `""`. |
| Header respons API | `Cache-Control: no-store`. |

### 1.1 Format error

```json
{
  "error": {
    "code": "validation_error",
    "message": "Data tidak valid.",
    "details": { "name": ["Nama aset sudah digunakan."] }
  }
}
```

`details` berisi daftar pesan per field, atau `{}`. Tidak ada traceback, SQL, atau secret.

### 1.2 Katalog kode error

| HTTP | `code` | Kapan |
| --- | --- | --- |
| 400 | `validation_error` | Input tidak valid, termasuk keunikan nama/serial/`vlan_number`/nama interface dan CHECK database |
| 400 | `invalid_parameter` | Parameter query tidak dikenal atau tidak valid |
| 400 | `immutable_field` | Field yang tidak boleh diubah ikut dikirim |
| 400 | `reserved_address` | Alamat network/broadcast/anycast yang dilarang (DATA_MODEL 6.4) |
| 400 | `special_use_subnet` | Subnet loopback/multicast/unspecified/link-local (DATA_MODEL 6.4) |
| 400 | `import_invalid` | Commit impor CSV mengandung error baris |
| 401 | `unauthenticated` | Belum login atau sesi tidak berlaku |
| 401 | `invalid_credentials` | Login gagal (akun tidak dikenal, password salah, atau nonaktif; pesan seragam, AP-10) |
| 403 | `permission_denied` | Tidak memiliki permission |
| 403 | `password_change_required` | `must_change_password` aktif (RBAC 6.1) |
| 404 | `not_found` | Objek tidak ada atau terarsip bagi yang tidak berhak |
| 405 | `method_not_allowed` | Metode tidak didukung |
| 409 | `has_dependents` | Arsip diblokir oleh anak aktif, atau perubahan CIDR diblokir (DATA_MODEL 8) |
| 409 | `parent_archived` | Relasi baru ke induk terarsip |
| 409 | `restore_conflict` | Restore bentrok dengan baris aktif |
| 409 | `ip_conflict` | Alokasi alamat ganda |
| 409 | `subnet_overlap` | Subnet tumpang tindih |
| 409 | `connection_duplicate` | Pasangan interface sudah terhubung (termasuk arah terbalik) |
| 409 | `interface_in_use` | Interface sudah punya koneksi fisik aktif |
| 409 | `concurrent_conflict` | Deadlock setelah satu kali percobaan ulang |
| 409 | `invalid_transition` | Transisi status insiden tidak diizinkan |
| 409 | `incident_closed` | Insiden `closed` tidak dapat diubah |
| 409 | `last_administrator` | Aksi akan menghilangkan administrator aktif terakhir |
| 409 | `self_modification_forbidden` | Mengubah peran/status/password sendiri lewat endpoint admin |
| 413 | `file_too_large` | File CSV melebihi batas ukuran |
| 415 | `unsupported_media_type` | Content-Type tidak didukung |
| 429 | `rate_limited` | Melebihi batas; menyertakan `Retry-After` |
| 500 | `internal_error` | Kesalahan server |
| 503 | `unavailable` | Hanya untuk `/health/` |

## 2. Autentikasi

| Metode dan path | Izin | Isi |
| --- | --- | --- |
| `GET /auth/csrf/` | Publik | `200 {"csrf_token": "..."}`; juga mengatur cookie CSRF (AP-09). Simpan token di memori aplikasi, bukan local storage. |
| `POST /auth/login/` | Publik | Body `{username, password}`. `200` dengan objek `me`. |
| `POST /auth/logout/` | Login | `204`. Mengakhiri sesi server-side. |
| `GET /auth/me/` | Login | `{id, username, first_name, last_name, email, role, must_change_password, permissions: ["app.codename", ...]}` |
| `POST /auth/password/change/` | Login | Body `{old_password, new_password}`. `204`. Mengosongkan `must_change_password`. |

Throttle login dan ganti password: spec §5.

## 3. Pengguna dan peran

| Metode dan path | Permission | Catatan |
| --- | --- | --- |
| `GET /users/` | `view_user` | Filter: `role`, `is_active`; `search` pada username, nama, email |
| `POST /users/` | `add_user` | Body: `username`, `password` (awal), `role`, `first_name`, `last_name`, `email`. Menetapkan `must_change_password = true`. |
| `GET /users/{id}/` | `view_user` | |
| `PATCH /users/{id}/` | `change_user` (+ `change_role_user` bila `role` berubah) | Field: `first_name`, `last_name`, `email`, `is_active`, `role`. `username` immutable. |
| `POST /users/{id}/reset-password/` | `reset_password_user` | Body `{temporary_password}`. `204`. Menetapkan `must_change_password = true`. |
| `GET /roles/` | `view_user` | Daftar `{name, label}` empat peran; tetap berpaginasi (AP-13) |

Objek pengguna: `id`, `username`, `first_name`, `last_name`, `email`, `role`, `is_active`, `must_change_password` (ro), `last_login` (ro), `date_joined` (ro). Pengguna tidak dihapus fisik. Aturan akun: RBAC 6.1.

## 4. Lokasi, aset, interface

### 4.1 Lokasi `/locations/`

| Metode dan path | Permission |
| --- | --- |
| `GET /locations/`, `GET /locations/{id}/` | `view_location` |
| `POST /locations/` | `add_location` |
| `PATCH /locations/{id}/` | `change_location` |
| `POST /locations/{id}/archive/`, `.../restore/` | `archive_location`, `restore_location` |

Field: `name` (wajib, maks 100), `location_type` (`building`, `room`, `rack`, `cabinet`, `storage`, `other`), `description`. Filter: `location_type`, `search` (name), `include_archived`. Urutan: `name`, `created_at`.

### 4.2 Aset `/assets/`

| Metode dan path | Permission |
| --- | --- |
| `GET /assets/`, `GET /assets/{id}/` | `view_asset` |
| `POST /assets/` | `add_asset` |
| `PATCH /assets/{id}/` | `change_asset` |
| `POST /assets/{id}/archive/`, `.../restore/` | `archive_asset`, `restore_asset` |

Field: `name` (wajib, unik di antara aset aktif tanpa membedakan huruf besar/kecil, maks 255), `asset_type` (`router`, `switch`, `access_point`, `firewall`, `server`, `workstation`, `patch_panel`, `other`), `manufacturer`, `model`, `serial_number` (opsional, unik di antara aset aktif), `status` (`in_use`, `spare`, `maintenance`, `retired`), `location` (id atau `null`), `description`; read-only `location_name` (AP-01). Tidak ada field `hostname`. Filter: `asset_type`, `status`, `location`, `search` (name, serial_number, manufacturer, model), `include_archived`. Urutan: `name`, `created_at`, `status`.

Arsip aset: mengikuti DATA_MODEL 8.6. Aksi `archive` mengarsipkan interface aktif yang memenuhi syarat dalam transaksi yang sama; respons `200` berisi aset. Error: `has_dependents`.

### 4.3 Interface `/interfaces/`

| Metode dan path | Permission |
| --- | --- |
| `GET /interfaces/`, `GET /interfaces/{id}/` | `view_networkinterface` |
| `POST /interfaces/` | `add_networkinterface` |
| `PATCH /interfaces/{id}/` | `change_networkinterface` |
| `POST /interfaces/{id}/archive/`, `.../restore/` | `archive_networkinterface`, `restore_networkinterface` |

Field: `asset` (wajib, immutable, AP-04), `name` (wajib, unik per aset di antara interface aktif, maks 64), `mac_address` (opsional; diterima dengan pemisah `:` atau `-`, disimpan huruf kecil berpemisah `:`; hanya EUI-48; tidak unik), `description`; read-only `asset_name`. Filter: `asset`, `search` (name, mac_address), `include_archived`.

## 5. IPAM

### 5.1 Subnet `/subnets/`

| Metode dan path | Permission |
| --- | --- |
| `GET /subnets/`, `GET /subnets/{id}/` | `view_subnet` |
| `POST /subnets/` | `add_subnet` |
| `PATCH /subnets/{id}/` | `change_subnet` |
| `POST /subnets/{id}/archive/`, `.../restore/` | `archive_subnet`, `restore_subnet` |

Field: `cidr` (wajib; IPv4/IPv6; tidak boleh overlap dengan subnet aktif; tidak dapat diubah selama ada IP aktif), `gateway` (opsional; hanya informasi; harus alamat host dalam subnet), **`vlan`** (opsional; **id baris VLAN** aktif, bukan nomor VLAN), `description`, `status` (`planned`, `active`, `deprecated`); read-only `vlan_number` dan `vlan_name` (nomor dan nama VLAN yang dirujuk, `null` bila tidak ada; AP-01). Filter: `status`, `vlan` (id), `family` (`4` atau `6`), `search` (cidr, description), `include_archived`. Error khusus: `subnet_overlap`, `special_use_subnet`, `parent_archived` (VLAN terarsip), `has_dependents`.

### 5.2 Alamat IP `/ip-addresses/`

| Metode dan path | Permission |
| --- | --- |
| `GET /ip-addresses/`, `GET /ip-addresses/{id}/` | `view_ipaddress` |
| `POST /ip-addresses/` (alokasi) | `add_ipaddress` |
| `PATCH /ip-addresses/{id}/` | `change_ipaddress` |
| `POST /ip-addresses/{id}/release/` | `release_ipaddress` |

Field: `address` (wajib; immutable), `subnet` (wajib; immutable), `status` (tulis: `allocated` atau `reserved`; baca juga `released`), `asset` (id atau `null`), `interface` (id atau `null`; bila diisi, `asset` wajib dan interface harus milik aset itu), `description`; read-only `subnet_cidr`, `asset_name`, `interface_name`. Baris `released` hanya terlihat dengan `include_archived=true`. Filter: `subnet`, `status`, `asset`, `interface`, `address` (persis), `search` (address, description), `include_archived`. Error khusus: `ip_conflict`, `reserved_address`, `parent_archived`, `validation_error` (alamat di luar subnet). `release` mengembalikan `200` objek berstatus `released`.

## 6. VLAN dan koneksi

### 6.1 VLAN `/vlans/`

| Metode dan path | Permission |
| --- | --- |
| `GET /vlans/`, `GET /vlans/{id}/` | `view_vlan` |
| `POST /vlans/` | `add_vlan` |
| `PATCH /vlans/{id}/` | `change_vlan` |
| `POST /vlans/{id}/archive/`, `.../restore/` | `archive_vlan`, `restore_vlan` |

Field: **`vlan_number`** (wajib; 1–4094 kecuali 1002–1005; unik di antara VLAN aktif), `name` (wajib, maks 100), `description`, `status` (`planned`, `active`, `deprecated`). Pada objek VLAN, `id` adalah identitas baris dan `vlan_number` adalah nomor VLAN. Filter: `status`, `vlan_number`, `search` (name, description), `include_archived`. Arsip ditolak `has_dependents` selama ada subnet aktif yang merujuk.

### 6.2 Koneksi `/connections/`

| Metode dan path | Permission |
| --- | --- |
| `GET /connections/`, `GET /connections/{id}/` | `view_connection` |
| `POST /connections/` | `add_connection` |
| `PATCH /connections/{id}/` | `change_connection` |
| `POST /connections/{id}/archive/`, `.../restore/` | `archive_connection`, `restore_connection` |

Field: `interface_a`, `interface_b` (wajib; dikirim dalam urutan apa pun; respons selalu dinormalisasi sehingga `interface_a < interface_b`), `connection_type` (`ethernet`, `fiber`, `console`, `wireless`, `virtual`), `description`; read-only `interface_a_label`, `interface_b_label` (`<nama aset>:<nama interface>`). Aturan: kedua interface berbeda dan aktif; satu interface hanya boleh punya satu koneksi aktif bertipe fisik (`ethernet`, `fiber`, `console`). Filter: `interface` (salah satu sisi), `connection_type`, `include_archived`. Error khusus: `connection_duplicate`, `interface_in_use`, `parent_archived`.

## 7. Insiden, impor, dashboard, audit, health

### 7.1 Insiden `/incidents/`

| Metode dan path | Permission |
| --- | --- |
| `GET /incidents/`, `GET /incidents/{id}/` | `view_incident` |
| `POST /incidents/` | `add_incident` |
| `PATCH /incidents/{id}/` | Per field (RBAC 6.5) |
| `GET /incidents/{id}/events/` | `view_incident` |
| `POST /incidents/{id}/events/` | `add_incidentevent` |

Field insiden: `title` (wajib, maks 200), `description`, `severity` (`low`, `medium`, `high`, `critical`), `status` (read-only saat `POST`: selalu `open`; diubah lewat `PATCH`, AP-06), `assignee` (id atau `null`), `asset` (id atau `null`); read-only `asset_name`, `assignee_username`. Setiap perubahan `status`, `assignee`, `severity`, `asset` menambah event otomatis; `PATCH` yang tidak mengubah apa pun tidak menambah event. Transisi status: DATA_MODEL 4.9; pelanggaran `invalid_transition`. Insiden `closed` menolak `PATCH` dan `POST` event dengan `409 incident_closed` untuk semua peran, tanpa pengecualian. Tidak ada reopen pada MVP; bila kelak dibutuhkan, reopen adalah transisi khusus dengan permission dan audit event tersendiri (belum didefinisikan). Filter: `status`, `severity`, `assignee`, `asset`, `search` (title), urutan `created_at`, `updated_at`, `severity`.

Event `{id, event_type, actor, actor_username, body, from_value, to_value, created_at}`. `POST` body `{body}` membuat event `note` (tidak boleh kosong). Jenis lain hanya dibuat sistem. Urutan kronologis naik; tidak ada ubah/hapus.

### 7.2 Impor CSV

`POST /imports/{resource}/`, `resource` ∈ `locations`, `assets`, `subnets`, `ip-addresses`. Permission: `import_locations`, `import_assets`, `import_subnets`, `import_ipaddresses`.

Form: `file` (CSV) dan `mode` (`preview` atau `commit`). Batas default: 2 MB dan 1.000 baris, dapat dikonfigurasi.

```json
{
  "mode": "preview",
  "resource": "subnets",
  "summary": { "rows": 3, "valid": 2, "errors": 1 },
  "errors": [
    { "row": 3, "column": "vlan", "code": "validation_error", "message": "VLAN 30 tidak ditemukan atau tidak aktif." }
  ],
  "created": 0
}
```

- `preview`: validasi semua baris tanpa menyimpan; `200` walau ada error (AP-08); `created` selalu 0.
- `commit`: validasi ulang semua baris, lalu simpan seluruhnya dalam satu transaksi. Jika ada error: `400 import_invalid` dengan struktur `errors` yang sama dan tidak ada yang tersimpan. Jika sukses: `200`, `created` terisi, audit `import.commit`.
- Hanya membuat baris baru; tidak memperbarui yang sudah ada (AP-02).
- Error umum: `413 file_too_large`, `415 unsupported_media_type`, `400 validation_error` (header salah, kolom tak dikenal, jumlah baris melebihi batas).

Template CSV dan aturan: bagian 9.

### 7.3 Dashboard `GET /dashboard/summary/`

Pengguna terautentikasi. Hanya kunci yang `view_`-nya dimiliki pengguna (RBAC 6.6):

```json
{
  "assets": { "total": 42 },
  "subnets": { "total": 6 },
  "ip_addresses": { "total": 120 },
  "incidents": { "open": 2, "in_progress": 1, "resolved": 0 },
  "recent_changes": [
    { "timestamp": "2026-10-26T03:12:00Z", "action": "asset.updated", "object_type": "asset", "object_id": 7, "actor_username": "budi.s" }
  ]
}
```

`total` menghitung baris aktif (IP berstatus `allocated` atau `reserved`). `incidents` menghitung per status selain `closed`. `recent_changes` memuat maksimal 10 event dan hanya untuk pemilik `view_auditevent` (AP-11).

### 7.4 Audit `GET /audit-events/`

Permission `view_auditevent`. Field: `id`, `actor` (id atau `null`), `actor_username`, `action`, `object_type`, `object_id`, `timestamp`, `safe_metadata`. Filter: `action`, `object_type`, `object_id`, `actor`, `timestamp_from`, `timestamp_to`. Urutan default `-timestamp`. Metode selain `GET`: `405`. Nilai `action` dan `object_type`: DATA_MODEL 4.11 dan 4.12.

### 7.5 Health `GET /health/`

Publik. `200 {"status": "ok"}` bila aplikasi dan koneksi database berfungsi; `503 {"status": "unavailable"}` bila tidak. Tanpa detail internal, versi, atau nama host.

## 8. Kontrak VLAN: `vlan` dan `vlan_number`

Dua nama yang mudah tertukar, dengan arti berbeda menurut konteks:

| Konteks | Nama | Arti | Contoh |
| --- | --- | --- | --- |
| API subnet (tulis dan baca) | `vlan` | **id baris VLAN** (`vlans_vlan.id`) | `3` |
| API subnet (baca saja) | `vlan_number` | Nomor VLAN yang dirujuk | `10` |
| API VLAN | `id` | Identitas baris | `3` |
| API VLAN | `vlan_number` | Nomor VLAN (1–4094) | `10` |
| **CSV subnet** | `vlan` | **`vlan_number`** dari VLAN aktif yang sudah ada | `10` |

Contoh API (membuat subnet yang terhubung ke VLAN nomor 10 yang memiliki `id` 3):

```json
POST /api/v1/subnets/
{ "cidr": "192.168.10.0/24", "status": "active", "vlan": 3 }

200
{ "id": 5, "cidr": "192.168.10.0/24", "gateway": null, "vlan": 3, "vlan_number": 10, "vlan_name": "Mgmt", "status": "active" }
```

Contoh CSV yang menyatakan hal yang sama (kolom `vlan` berisi **10**, bukan 3):

```csv
cidr,status,gateway,vlan,description
192.168.10.0/24,active,192.168.10.1,10,Jaringan manajemen
```

Penerjemahan nomor ke id dilakukan importer. Mengirim id baris pada kolom `vlan` CSV adalah kesalahan pengguna dan menghasilkan error baris bila tidak ada VLAN aktif bernomor itu; template dan pesan error harus menyebut "nomor VLAN".

## 9. Template CSV

Aturan umum: UTF-8 (BOM diterima), pemisah koma, kutip sesuai RFC 4180, baris pertama header persis sesuai nama kolom di bawah (urutan kolom bebas, kolom tak dikenal ditolak). Nomor baris dihitung dengan header sebagai baris 1. Nilai di-trim; sel kosong berarti `null`/kosong. Sel yang diawali `=`, `+`, `-`, atau `@` diperlakukan sebagai teks dan tidak pernah dievaluasi. Duplikat di dalam file dan duplikat terhadap data aktif dilaporkan sebagai error baris. File tidak disimpan setelah diproses. Urutan ketergantungan: lokasi → aset → subnet → alamat IP; VLAN tidak dapat diimpor (D-31) dan harus sudah ada.

### 9.1 `locations`

| Kolom | Wajib | Format |
| --- | --- | --- |
| `name` | Ya | Teks maks 100, unik di antara lokasi aktif |
| `location_type` | Ya | `building`, `room`, `rack`, `cabinet`, `storage`, `other` |
| `description` | Tidak | Teks |

```csv
name,location_type,description
Lab Jaringan A,room,Ruang praktikum utama
```

### 9.2 `assets`

| Kolom | Wajib | Format |
| --- | --- | --- |
| `name` | Ya | Teks maks 255, unik di antara aset aktif |
| `asset_type` | Ya | Enum 4.2 |
| `status` | Ya | `in_use`, `spare`, `maintenance`, `retired` |
| `manufacturer`, `model`, `serial_number` | Tidak | Teks; `serial_number` unik di antara aset aktif |
| `location` | Tidak | **Nama** lokasi aktif yang sudah ada |
| `description` | Tidak | Teks |

```csv
name,asset_type,status,manufacturer,model,serial_number,location,description
R1,router,in_use,MikroTik,RB4011,SN-0001,Lab Jaringan A,Router utama
```

### 9.3 `subnets`

| Kolom | Wajib | Format |
| --- | --- | --- |
| `cidr` | Ya | CIDR IPv4/IPv6, tanpa bit host |
| `status` | Ya | `planned`, `active`, `deprecated` |
| `gateway` | Tidak | Alamat host dalam subnet |
| `vlan` | Tidak | **`vlan_number`** dari VLAN aktif yang sudah ada |
| `description` | Tidak | Teks |

Contoh: lihat bagian 8.

### 9.4 `ip-addresses`

| Kolom | Wajib | Format |
| --- | --- | --- |
| `address` | Ya | Alamat IPv4/IPv6 tanpa mask |
| `subnet` | Ya | **CIDR** subnet aktif yang sudah ada |
| `status` | Ya | `allocated` atau `reserved` |
| `asset` | Tidak | **Nama** aset aktif yang sudah ada |
| `interface` | Tidak | **Nama** interface milik aset di kolom `asset` (wajib bila `interface` diisi) |
| `description` | Tidak | Teks |

```csv
address,subnet,status,asset,interface,description
192.168.10.1,192.168.10.0/24,allocated,R1,Gi0/1,Gateway
```

## 10. Asumsi API dan statusnya

Status per 26 Oktober 2026: **AP-02 disetujui eksplisit** (impor CSV create-only, tanpa upsert); AP-01 dan AP-03 s.d. AP-14 default diterima.

| ID | Asumsi |
| --- | --- |
| AP-01 | Field read-only turunan: `location_name`, `asset_name`, `subnet_cidr`, `interface_name`, `vlan_number`, `vlan_name`, `interface_a_label`, `interface_b_label`, `assignee_username`, `asset_name` (insiden). Tidak dapat ditulis. |
| AP-02 | Impor CSV hanya membuat baris baru; tidak ada pembaruan (upsert) pada MVP. |
| AP-03 | Semua `POST` aksi (`archive`, `restore`, `release`) tanpa body dan mengembalikan `200` objek terbaru. |
| AP-04 | `interface.asset` dan `ip.address`/`ip.subnet` immutable setelah dibuat. |
| AP-05 | Tidak ada `PUT`; `PATCH` parsial saja. |
| AP-06 | Perubahan status dan assignee insiden lewat `PATCH /incidents/{id}/` dengan pemeriksaan permission per field, bukan endpoint terpisah. |
| AP-07 | Nama kode error yang tidak berasal dari DATA_MODEL 6.6 (`invalid_parameter`, `immutable_field`, `import_invalid`, `invalid_transition`, `incident_closed`, `last_administrator`, `self_modification_forbidden`, `password_change_required`, `unavailable`, dan lainnya di 1.2) adalah usulan. |
| AP-08 | Preview impor mengembalikan `200` walau ada error baris; commit dengan error mengembalikan `400 import_invalid`. |
| AP-09 | `GET /auth/csrf/` mengembalikan token di body dan mengatur cookie CSRF. |
| AP-10 | Login gagal selalu `401 invalid_credentials` dengan pesan yang sama, tanpa membedakan penyebab. |
| AP-11 | Bentuk respons dashboard di 7.3; "insiden terbuka" dihitung per status selain `closed`. |
| AP-12 | `include_archived` dan akses baris terarsip butuh `restore_<model>` (RBAC U-07). |
| AP-13 | `GET /roles/` tetap berpaginasi demi konsistensi. |
| AP-14 | Nomor baris pada laporan error CSV dihitung dengan header sebagai baris 1 (bagian 9). |

## 11. Hubungan dengan OpenAPI

Skema OpenAPI dibuat otomatis dari implementasi (spec §1) dan harus memuat: seluruh endpoint di atas, enum dari DATA_MODEL bagian 4, format error 1.1, dan keterangan `vlan` vs `vlan_number`. Uji kontrak membandingkan skema yang dihasilkan dengan dokumen ini sebelum fase dinyatakan selesai.

## 12. Catatan revisi

**1.2:** kontrak insiden `closed` dipertegas sesuai U-04 (RBAC).

**1.1:** AP-01 s.d. AP-14 diputuskan.

**1.0:** dokumen awal.
