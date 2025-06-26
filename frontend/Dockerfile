FROM node:18

WORKDIR /app

# Copy only the Next.js app folder
COPY hospitaliq ./hospitaliq

# Set working dir inside the hospitaliq folder
WORKDIR /app/hospitaliq

RUN npm install

COPY . .

# Set env vars at build time (Next.js requires this for static builds)
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}

RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "dev"]
