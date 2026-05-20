FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy frontend source files
COPY . .

# Build the React application
RUN npm run build

# Expose port for frontend
EXPOSE 3000

# Serve static files
CMD ["npx", "serve", "-s", "build", "-p", "3000"]
