FROM node:20

# Set working directory
WORKDIR /app


# Copy only package files first
COPY package*.json ./

# Install dependencies fresh in Linux container
RUN npm ci --include=optional

# Copy everything from the current folder (hospitaliq)
COPY . .

# Set env vars at build time
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}

# Build the Next.js app
RUN npm run build 


# Expose the port
EXPOSE 3000

# Start the app (you can use `start` for production or `dev` for development)
CMD ["npm", "run", "dev"]
