module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://192.168.127.133:8000',  // Django backend URL
        changeOrigin: true,
        secure: false,  // For development purposes, disable SSL verification (if using HTTP)
      },
    },
  },
};
