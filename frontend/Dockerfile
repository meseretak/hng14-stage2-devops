# syntax=docker/dockerfile:1
FROM node:20-alpine AS builder

WORKDIR /build
COPY package*.json ./
RUN npm ci --omit=dev

# ---- final stage ----
FROM node:20-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app
COPY --from=builder /build/node_modules ./node_modules
COPY app.js package.json ./
COPY views ./views

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
