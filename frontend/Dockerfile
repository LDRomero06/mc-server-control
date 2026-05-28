# Stage 1: Build the React application
FROM node:22-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy code and build production assets
COPY . .
RUN npm run build

# Expose the port used by Vite preview
EXPOSE 3000

# Start the application using Vite's built-in preview server
CMD ["npx", "vite", "preview", "--port", "3000", "--host"]
