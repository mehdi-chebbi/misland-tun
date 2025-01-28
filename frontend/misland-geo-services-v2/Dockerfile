# Use a Node.js base image
FROM node:16

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install -g @quasar/cli # Install Quasar CLI globally
RUN npm install

# Copy the entire app into the container
COPY . .


# Start the Quasar development server
CMD ["quasar", "dev"]
