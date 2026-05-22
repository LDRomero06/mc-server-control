# Stage 1: Build the React application
FROM node:18-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy code and build production assets
COPY . .
RUN npm run build
