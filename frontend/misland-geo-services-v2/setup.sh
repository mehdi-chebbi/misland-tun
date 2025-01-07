#!/bin/bash
npm i
npm run build

pm2 stop dashboard

pm2 start server.js --name dashboard
