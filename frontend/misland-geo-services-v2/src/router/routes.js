
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { name:'home',path: '', component: () => import('src/pages/Home.vue') },
      { name:'geoservice', path: '/geoservice/:type?/:id?', component: () => import('pages/GeoService.vue') },
      { name:'dashboard', path: '/dashboard', component: () => import('pages/Dashboard.vue') },
      { name:'mapographics', path: '/mapographics', component: () => import('pages/Mapographics.vue') },
      { name:'login', path: '/login', component: () => import('src/pages/Auth/Login.vue') },
      { name:'signup', path: '/register', component: () => import('src/pages/Auth/Register.vue') },
      { name:'forgot password', path: '/forgot-password/:code?/:token?', component: () => import('src/pages/Auth/ForgotPassword.vue') },
      { name:'reset password', path: '/geoservice/forgotpassword/:code?/:token?', component: () => import('src/pages/Auth/ResetPassword.vue') },
      { name:'account-activation', path: '/geoservice/:action/:code/:token', component: () => import('layouts/MainLayout.vue') },
      { name:'profile', path: '/profile/:component?/:id?', component: () => import('src/pages/Profile.vue') },
      { name:'privacy-policy', path: '/privacy-policy', component: () => import('src/pages/PrivacyPolicy.vue') },
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
