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
  - Toolchain audit (podman-compose 1.6.0, Node 22, Python 3.14 / py312 compat)
  - Struktur repo (`docs/`, `backend/`, `frontend/`, `deployment/`)
  - Dependencies dikunci (`pyproject.toml`, lockfile frontend)
  - PostgreSQL 16 dan Django 5.2.18 baseline
  - Compose provider terverifikasi (Podman)
- **Phase 1 (Backend Foundation):** Selesai / Terverifikasi
  - Custom user model `accounts.User(AbstractUser)` dengan validator username, properti `role` dan `permissions`
  - Data migration `0002_seed_roles` (4 grup: administrator, lab_manager, lab_assistant, viewer)
  - Konfigurasi Django: settings, urls, middleware (`AuthenticationMiddleware` aktif), REST Framework settings
  - Exception handler konsisten (`custom_exception_handler`) sesuai API spec
  - Endpoint Auth & Users aktif: `csrf`, `login`, `logout`, `me`, `password/change`, `users/`
- **Phase 2 (Assets, Locations, dan IPAM):** Selesai / Terverifikasi
  - **Locations:** Model `Location` dengan pilihan tipe, `archived_at`, dukungan soft-delete
  - **Assets:** Model `Asset` dengan jenis perangkat, status, lokasi FK, constraint unique nama aktif dan serial aktif; **NetworkInterface** berelasi ke Asset, MAC address validator, unique constraint per asset
  - **IPAM & VLANs:** Model `Subnet` dengan CIDR, gateway informasi, FK opsional ke `VLAN`; Model `IPAddress` dengan status `allocated/reserved/released`, constraint keunikan `(subnet, address)` aktif, relasi ke Asset/Interface; Model `VLAN` dengan rentang 1–4094 (kecuali 1002–1005), unique nomor aktif
- **Phase 3 (VLAN, Connections, Incidents, Audit, Imports):** Selesai / Terverifikasi
  - **VLANs:** `apps.vlans.models.VLAN` dengan unique constraint nomor aktif
  - **Connections:** `apps.connections.models.Connection` dengan CHECK `interface_a_id < interface_b_id`, unique constraint pasangan aktif
  - **Incidents:** `apps.incidents.models.Incident` & `IncidentEvent` (riwayat append-only)
  - **Audit:** `apps.audit.models.AuditEvent` & `service.record_audit()`
  - **Impor CSV:** `apps.imports.service` (preview dan commit atomik) + endpoint `POST /api/v1/imports/`
- **Phase 4 (Frontend):** Selesai / Terverifikasi
  - SPA React 19 + TypeScript + Vite (`frontend/`)
  - Konfigurasi Vite dev proxy ke backend
  - Alur UI terhubung ke API: Login, Dashboard info peran pengguna, Impor CSV (Preview & Commit)
  - Build production (`npm run build`) lulus tanpa error (`dist/` dihasilkan)
- **Phase 5 (Hardening & Release):** Sedang Dikerjakan / Baseline Terverifikasi
  - Test suite dasar terpasang dan lulus pada PostgreSQL 16 container (`python3 manage.py test` → 1 test OK)
  - Migrasi seluruh app diterapkan secara konsisten
  - Kontainer database PostgreSQL 16 lokal terkonfirmasi berjalan

## Arsitektur
- **Backend:** Python + Django 5.2 LTS + Django REST Framework (modular monolith)
- **Database:** PostgreSQL 16 (tipe `inet`/`cidr`, GiST exclusion constraint, trigger penjaga integritas)
- **Auth:** Django session + CSRF (browser MVP, tanpa bearer token)
- **Frontend:** React + TypeScript + Vite
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

# 3. Jalankan compose
podman compose up -d

# 4. Jalankan migrasi dan seed role
podman compose exec backend python manage.py migrate

# 5. Buat administrator pertama
podman compose exec backend python manage.py createsuperuser

# 6. Akses di http://localhost
```
