export default defineNuxtRouteMiddleware((to) => {
  const auth = useCookie('kanban_auth')
  
  // They are trying to visit a protected page while NOT logged in
  if (!auth.value && to.path !== '/login') {
    return navigateTo('/login')
  }
  
  // They are trying to visit login while ALREADY logged in
  if (auth.value && to.path === '/login') {
    return navigateTo('/')
  }
})
