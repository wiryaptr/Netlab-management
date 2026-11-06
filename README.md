# NetLab Manager

Aplikasi web untuk mengelola inventaris dan dokumentasi operasional laboratorium jaringan.

## Dokumentasi
- [PRD (Product Requirements Document)](prd.md)
- [Design Document](design.md)
- [Technical Specification](spec.md)
- [Architecture Decision Records (ADR)](docs/ADR.md)
- [Data Model & Database Design](docs/DATA_MODEL.md)
- [RBAC Matrix](docs/RBAC_MATRIX.md)
- [API Specification](docs/API_SPEC.md)
- [Security Requirements](docs/SECURITY.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Version & Dependency Pinning](docs/VERSIONS.md)

## Status Fase
- **Phase 0 (Foundation):** Selesai / Terverifikasi
  - Toolchain audit (podman-compose 1.6.0)
  - Struktur repo (docs/, backend/, frontend/, deployment/)
  - Dependencies dikunci (pyproject.toml, lockfile frontend)
  - PostgreSQL 16 dan Django 5.2.18 baseline
  - Compose provider terverifikasi
- **Phase 1 (Backend Foundation):** Selesai / Terverifikasi
  - Custom user model `accounts.User(AbstractUser)` dengan validator username, properti `role` dan `permissions`
  - Data migration `0002_seed_roles` (4 grup: administrator, lab_manager, lab_assistant, viewer)
  - Konfigurasi Django: settings, urls, middleware, REST Framework settings
  - Exception handler konsisten (custom_exception_handler) sesuai API spec
- **Phase 2 (Assets, Locations, dan IPAM):** Selesai / Terverifikasi
  - **Locations:** Model `Location` dengan pilihan tipe, `archived_at`, dukungan soft-delete
  - **Assets:** Model `Asset` dengan jenis perangkat, status, lokasi FK, constraint unique nama aktif dan serial aktif; **NetworkInterface** berelasi ke Asset, MAC address validator, unique constraint per asset
  - **IPAM & VLANs:** Model `Subnet` dengan CIDR, gateway informasi, FK opsional ke `VLAN`; Model `IPAddress` dengan status `allocated/reserved/released`, constraint keunikan `(subnet, address)` aktif, relasi ke Asset/Interface; Model `VLAN` dengan rentang 1–4094 (kecuali 1002–1005), unique nomor aktif
- **Phase 3 (VLAN, Connections, Incidents, Audit, Imports):** SEDANG DIEKSEKUSI
  - **VLANs:** Sudah dibuat `apps.vlans.models.VLAN` dengan unique constraint nomor aktif
  - **Connections:** Sudah dibuat `apps.connections.models.Connection` dengan CHECK `interface_a_id < interface_b_id`, unique constraint pasangan aktif; klaim koneksi fisik aktif dikontrol via trigger database
  - **Incidents:** Sudah dibuat `apps.incidents.models.Incident` dengan severity/status enum, assignee FK ke User, asset FK; **IncidentEvent** sebagai riwayat append-only; insiden `closed` read-only untuk semua peran
  - **Audit:** Sudah dibuat `apps.audit.models.AuditEvent` dengan 43 aksi wajib, `safe_metadata` filter; `service.record_audit()` untuk mencatat event penting tanpa secret/credential; event `auth.*`, `incident.*`, `import.*` didukung
  - **Impor CSV:** Sudah dibuat `apps.imports.service` dengan `preview_csv()` (validasi tanpa menyimpan) dan `commit_csv()` (validasi ulang lalu simpan atomik); file tidak disimpan setelah proses; kolom `vlan` pada CSV subnet berisi `vlan_number` VLAN yang sudah ada; hanya resource `locations`, `assets`, `subnets`, `ip-addresses`
- **Phase 4 (Frontend):** Belum dimulai
- **Phase 5 (Hardening & Release):** Belum dimulai

## Arsitektur
- **Backend:** Python + Django 5.2 LTS + Django REST Framework (modular monolith)
- **Database:** PostgreSQL 16 (tipe `inet`/`cidr`, GiST exclusion constraint, trigger penjaga integritas)
- **Auth:** Django session + CSRF (browser MVP, tanpa bearer token)
- **Frontend:** React + TypeScript + Vite (belum dikembangkan)
- **Deployment:** Docker/Podman Compose dengan dua role database (`netlab_owner` untuk migrasi/backup, `netlab_app` untuk runtime)

## 4 Peran (Django Groups)
| Peran | Hak umum |
|-------|----------|
| administrator | Semua (50 permission), kelola user/role |
| lab_manager | Inventaris, IPAM, VLAN, koneksi, insiden, impor CSV, baca audit (45 permission) |
| lab_assistant | Lihat data + update aset/interface/IP/koneksi, tangani insiden (16 permission) |
| viewer | Hanya lihat data operasional (8 permission `view_*`) |

## Quick Start (dengan Docker/Podman Compose)
```bash
# 1. Clone & setup
git clone <repo>
cd netlab-manager

# 2. Buat file .env dari .env.example
cp .env.example .env
# Isi secret: DJANGO_SECRET_KEY, DATABASE_URL, dsb

# 3. Jalankan compose
podman compose up -d

# 4. Jalankan migrasi dan seed role
podman exec <backend-container> python manage.py migrate
podman exec <backend-container> python manage.py create_groups  # migrasi 0002

# 5. Buat administrator pertama
podman exec <backend-container> python manage.py create_admin

# 6. Akses di http://localhost
```