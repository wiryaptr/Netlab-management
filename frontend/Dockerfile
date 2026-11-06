# Build stage: build static React assets
FROM node:24-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Serve stage
FROM caddy:2-alpine
COPY --from=builder /app/dist /srv
