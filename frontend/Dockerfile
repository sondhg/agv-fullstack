# Stage 1: Build the application
FROM node:20.11.1-alpine AS builder

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY ["package.json", "package-lock.json*", "./"]

# Install dependencies, including devDependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application (TypeScript and Vite)
RUN npm run build

# Stage 2: Serve the application
FROM node:20.11.1-alpine

# Set the working directory
WORKDIR /usr/src/app

# Copy only the production-ready files from the build stage
COPY --from=builder /usr/src/app/dist ./dist

# Install a lightweight web server
RUN npm install -g serve

# Expose the port the app runs on
EXPOSE 5173

# Command to run the app
CMD ["serve", "-s", "dist", "-l", "5173"]
