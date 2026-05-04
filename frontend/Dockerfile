FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY public ./public
COPY src ./src

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Serve with simple HTTP server or nginx would be used in production
# For development:
CMD ["npm", "start"]
