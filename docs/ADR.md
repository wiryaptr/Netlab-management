# NetLab Manager — Architecture Decision Records

**Versi:** 1.0
**Tanggal:** 26 Oktober 2026
**Sumber:** `design.md` v1.3 §13, `spec.md` v1.3, `docs/DATA_MODEL.md` v1.2
**Status:** Konsolidasi. Tidak ada keputusan yang diubah; isi tiap ADR hanya merangkum keputusan yang sudah disepakati. Perubahan keputusan memerlukan ADR baru yang menggantikan ADR lama (status **Superseded**), bukan penyuntingan ADR ini.

Semua ADR berstatus **Accepted** pada tanggal dokumen ini. Kolom "Sumber" menunjuk dokumen yang menetapkan keputusan.

## Indeks

| ADR | Judul |
| --- | --- |
| 001 | Modular monolith |
| 002 | React + TypeScript + Vite untuk frontend |
| 003 | Django REST Framework untuk backend |
| 004 | PostgreSQL sebagai database |
| 005 | Session authentication untuk browser MVP |
| 006 | Input manual dan impor CSV sebelum integrasi otomatis |
| 007 | Compose untuk deployment awal |
| 008 | Tanpa network scanning atau remote configuration pada MVP |
| 009 | Keunikan IP per subnet dengan larangan subnet overlap |
| 010 | Arsip dengan `archived_at`, tanpa penghapusan fisik |
| 011 | RBAC dengan Django Groups dan permission eksplisit |
| 012 | Koneksi sebagai pasangan tak berarah ternormalisasi |
| 013 | Impor CSV masuk MVP dengan preview dan commit atomik |
| 014 | Pagination page-number, format error seragam, rate limiting |
| 015 | `locations` sebagai aplikasi backend tersendiri |
| 016 | Custom user model sejak migrasi pertama |
| 017 | Satu koneksi aktif per interface fisik lewat tabel klaim |
| 018 | Relasi opsional subnet–VLAN |
| 019 | Trigger penjaga integritas dan role database berhak minimum |
| 020 | VLAN 1002–1005 ditolak; gateway hanya informasi |
| 021 | Baseline PostgreSQL 16 dan Django 5.2 LTS |
| 022 | Nomor VLAN disimpan di `vlan_number` |

## ADR-001 — Modular monolith

- **Konteks:** Satu laboratorium, tim kecil, kebutuhan deployment sederhana.
- **Keputusan:** Satu aplikasi backend berbentuk modular monolith, bukan microservices. Setiap domain adalah Django app dengan model, serializer, view, permission, service, dan test sendiri.
- **Konsekuensi:** Satu unit deployment; batas modul dijaga lewat service layer. Perpecahan menjadi layanan terpisah membutuhkan ADR baru.
- **Sumber:** design §13; spec §1.

## ADR-002 — React + TypeScript + Vite untuk frontend

- **Konteks:** Dashboard dengan banyak form dan tabel.
- **Keputusan:** SPA dengan React, TypeScript (strict), dan Vite; struktur berbasis fitur/domain.
- **Konsekuensi:** Frontend disajikan sebagai aset statis lewat reverse proxy. Versi dikunci di `docs/VERSIONS.md`.
- **Sumber:** design §13, §8; spec §1, §12.

## ADR-003 — Django REST Framework untuk backend

- **Konteks:** Butuh ORM, migrasi, autentikasi, dan permission matang.
- **Keputusan:** Django + Django REST Framework, REST API berversi `/api/v1/`.
- **Konsekuensi:** Mengikuti baseline versi ADR-021.
- **Sumber:** design §13; spec §1, §3.

## ADR-004 — PostgreSQL sebagai database

- **Konteks:** Perlu tipe `inet`/`cidr`, exclusion constraint, constraint parsial, dan transaksi.
- **Keputusan:** PostgreSQL sebagai satu-satunya database.
- **Konsekuensi:** Integritas IPAM bertumpu pada fitur PostgreSQL (DATA_MODEL). Mengganti database membutuhkan ADR baru.
- **Sumber:** design §13; PRD §9; spec §1.

## ADR-005 — Session authentication untuk browser MVP

- **Konteks:** Satu origin, pengguna browser.
- **Keputusan:** Django session + CSRF; tanpa token bearer pada MVP.
- **Konsekuensi:** Cookie `HttpOnly`/`Secure`/`SameSite`; satu origin agar CORS tidak diperlukan.
- **Sumber:** design §13, §11; spec §1, §4, §11.

## ADR-006 — Input manual dan impor CSV sebelum integrasi otomatis

- **Konteks:** Data awal tersebar di spreadsheet; integrasi perangkat belum diizinkan.
- **Keputusan:** Data masuk lewat input manual dan impor CSV tervalidasi; integrasi otomatis ditunda.
- **Konsekuensi:** Tidak ada SNMP/SSH/API perangkat pada MVP.
- **Sumber:** design §13; PRD §10.

## ADR-007 — Compose untuk deployment awal

- **Konteks:** Deployment lokal pada satu server Linux.
- **Keputusan:** Orkestrasi dengan Compose (Docker atau Podman Compose); provider diverifikasi sebelum implementasi.
- **Konsekuensi:** Tidak ada Kubernetes pada MVP. Pemilihan provider tercatat di `docs/DEPLOYMENT.md`.
- **Sumber:** design §13, §12; spec §1, §14.

## ADR-008 — Tanpa network scanning atau remote configuration pada MVP

- **Konteks:** Tidak ada izin dan metode autentikasi untuk mengakses perangkat.
- **Keputusan:** Sistem tidak melakukan pemindaian, remote command execution, atau perubahan konfigurasi perangkat.
- **Konsekuensi:** Data bersifat dokumentasi; keberadaan alamat tidak berarti host aktif.
- **Sumber:** design §13, §2; PRD §5; spec §11, §17.

## ADR-009 — Keunikan IP per subnet dengan larangan subnet overlap

- **Konteks:** Satu domain jaringan pada MVP.
- **Keputusan:** Alamat IP aktif unik per `(subnet, address)`; subnet aktif tidak boleh overlap (exclusion constraint); alamat wajib berada di subnetnya. Ketiganya berlaku bersamaan. Multi-VRF di luar MVP.
- **Konsekuensi:** Alamat aktif efektif unik di seluruh lab; domain/VRF membutuhkan ADR dan migrasi baru.
- **Sumber:** design §13; spec §7; DATA_MODEL 6.1–6.3, D-03, D-04.

## ADR-010 — Arsip dengan `archived_at`, tanpa penghapusan fisik

- **Konteks:** Riwayat operasional dan audit harus tetap utuh.
- **Keputusan:** Data operasional diarsipkan dengan `archived_at`; tidak ada `DELETE` lewat UI/API; semua FK memakai `RESTRICT`.
- **Konsekuensi:** Keunikan "aktif" memakai partial unique index; role runtime tanpa hak `DELETE` (ADR-019).
- **Sumber:** design §13; PRD §9; spec §3; DATA_MODEL D-01, bagian 8.

## ADR-011 — RBAC dengan Django Groups dan permission eksplisit

- **Konteks:** Empat peran dengan hak berbeda.
- **Keputusan:** Peran = Django Group (`administrator`, `lab_manager`, `lab_assistant`, `viewer`); permission eksplisit pada Group, tidak pada pengguna; tepat satu peran per pengguna.
- **Konsekuensi:** Rincian permission di `docs/RBAC_MATRIX.md`; Group dibuat lewat data migration.
- **Sumber:** design §13; spec §9; DATA_MODEL D-09, A-12, A-18.

## ADR-012 — Koneksi sebagai pasangan tak berarah ternormalisasi

- **Konteks:** Koneksi (A,B) dan (B,A) adalah hal yang sama.
- **Keputusan:** Simpan dengan `interface_a_id < interface_b_id` (CHECK) dan unik pada pasangan aktif.
- **Konsekuensi:** Service menormalisasi urutan; API selalu mengembalikan bentuk ternormalisasi.
- **Sumber:** design §13, §10; spec §4, §6; DATA_MODEL D-07.

## ADR-013 — Impor CSV masuk MVP dengan preview dan commit atomik

- **Konteks:** Perpindahan data dari spreadsheet.
- **Keputusan:** Impor untuk lokasi, aset, subnet, dan alamat IP: preview tanpa menyimpan, commit divalidasi ulang dan atomik; VLAN tidak diimpor; kolom `vlan` pada CSV subnet berisi `vlan_number`.
- **Konsekuensi:** Impor memakai service domain (constraint dan audit identik dengan API); file tidak disimpan.
- **Sumber:** design §13; spec §8; DATA_MODEL D-31.

## ADR-014 — Pagination page-number, format error seragam, rate limiting

- **Konteks:** Kontrak API konsisten bagi frontend dan uji.
- **Keputusan:** Page-number pagination (`page`, `page_size`); format error `{error: {code, message, details}}`; kebijakan rate limiting default di spec §5.
- **Konsekuensi:** Kode error dikatalogkan di `docs/API_SPEC.md`; batas dapat dikonfigurasi lewat settings.
- **Sumber:** design §13; spec §5.

## ADR-015 — `locations` sebagai aplikasi backend tersendiri

- **Konteks:** Lokasi dipakai banyak domain.
- **Keputusan:** App `locations` terpisah dari `assets`.
- **Konsekuensi:** Aset merujuk lokasi lewat FK opsional.
- **Sumber:** design §13, §4; spec §2.

## ADR-016 — Custom user model sejak migrasi pertama

- **Konteks:** Mengganti model user setelah migrasi sangat mahal.
- **Keputusan:** `accounts.User(AbstractUser)` dan `AUTH_USER_MODEL` ditetapkan sebelum `makemigrations`/`migrate` pertama di environment mana pun.
- **Konsekuensi:** Strategi lengkap di DATA_MODEL bagian 9.
- **Sumber:** design §13; spec §3; DATA_MODEL D-08, A-12.

## ADR-017 — Satu koneksi aktif per interface fisik lewat tabel klaim

- **Konteks:** Satu port fisik hanya memiliki satu kabel; unique index pada pasangan tidak mencegah interface muncul sekali sebagai A dan sekali sebagai B.
- **Keputusan:** Koneksi bertipe `ethernet`, `fiber`, `console` mengklaim interface lewat tabel `connections_interfaceclaim` yang diisi trigger; `wireless` dan `virtual` tidak dibatasi.
- **Konsekuensi:** Aman terhadap request bersamaan; pelanggaran menjadi `409 interface_in_use`; aplikasi tidak menulis tabel klaim.
- **Sumber:** design §13; spec §4; DATA_MODEL 5.12, D-19.

## ADR-018 — Relasi opsional subnet–VLAN

- **Konteks:** PRD mensyaratkan relasi VLAN yang valid.
- **Keputusan:** `ipam_subnet.vlan_id` FK opsional ke VLAN aktif; satu VLAN dapat dirujuk banyak subnet; VLAN yang dirujuk subnet aktif tidak dapat diarsipkan.
- **Konsekuensi:** Restore subnet mensyaratkan VLAN aktif.
- **Sumber:** design §13; spec §4, §6; DATA_MODEL D-20.

## ADR-019 — Trigger penjaga integritas dan role database berhak minimum

- **Konteks:** FK `RESTRICT` dan pemeriksaan service tidak cukup untuk penulisan bersamaan; trigger lama tanpa kunci terbukti memiliki celah race.
- **Keputusan:** Trigger penjaga dua arah dengan kunci `FOR SHARE` pada induk; trigger append-only untuk audit dan event insiden; dua role database (`netlab_owner` untuk migrasi dan restore, `netlab_app` untuk runtime tanpa hak pemilik, `DELETE`, `TRUNCATE`, atau penonaktifan trigger).
- **Konsekuensi:** Bergantung pada `READ COMMITTED`; pemilik skema/DBA tetap dapat melewati trigger (R-01); trigger dan grant dibuat lewat `RunSQL`.
- **Sumber:** design §13, §11; spec §3, §11; DATA_MODEL 8.5–8.7, D-06.

## ADR-020 — VLAN 1002–1005 ditolak; gateway hanya informasi

- **Konteks:** Rentang VLAN legacy dan kebijakan alamat gateway belum ditetapkan.
- **Keputusan:** Nomor VLAN 1–4094 diterima kecuali 1002–1005 (VLAN 1 diizinkan); `gateway` pada subnet hanya informasi dan tidak otomatis menjadi baris IP.
- **Konsekuensi:** Alamat gateway diperlakukan seperti alamat biasa saat dialokasikan.
- **Sumber:** spec §4, §7.13; DATA_MODEL D-22, D-23.

## ADR-021 — Baseline PostgreSQL 16 dan Django 5.2 LTS

- **Konteks:** Spec menunda penetapan versi ke saat implementasi.
- **Keputusan:** Baseline PostgreSQL 16 dan Django 5.2 LTS. Versi patch dan dependency dikunci pada Phase 0 setelah pemeriksaan kompatibilitas; kandidat dan bukti ada di `docs/VERSIONS.md`.
- **Konsekuensi:** Django 5.2 LTS berada pada fase dukungan lanjutan (perbaikan keamanan dan kehilangan data) sampai April 2028, dan PostgreSQL 16 sampai November 2028 (`docs/VERSIONS.md`); rencana peningkatan perlu dibuat sebelum itu.
- **Sumber:** keputusan OD-12 A; DATA_MODEL D-30.

## ADR-022 — Nomor VLAN disimpan di `vlan_number`

- **Konteks:** Nama `vlan_id` bermakna ganda (nomor VLAN dan FK subnet).
- **Keputusan:** Nomor VLAN disimpan di `vlans_vlan.vlan_number` pada database dan API; `ipam_subnet.vlan_id` tetap FK ke `vlans_vlan.id`; API subnet memakai field `vlan` (id baris), sedangkan CSV subnet memakai kolom `vlan` berisi `vlan_number`.
- **Konsekuensi:** Perbedaan arti `vlan` pada API dan CSV harus tampak jelas di spesifikasi dan contoh (`docs/API_SPEC.md` bagian 8).
- **Sumber:** keputusan OD-11 B; DATA_MODEL D-29.

## Catatan revisi

**1.0:** konsolidasi ADR-001 s.d. ADR-022 tanpa perubahan keputusan.
