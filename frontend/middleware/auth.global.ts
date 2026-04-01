export default defineNuxtRouteMiddleware((to) => {
  const auth = useCookie('kanban_auth')

  // UI-only gate: the cookie value is not cryptographically validated.
  // Backend endpoints do not enforce auth. Local MVP only.
  if (!auth.value && to.path !== '/login') {
    return navigateTo('/login')
  }
  
  // They are trying to visit login while ALREADY logged in
  if (auth.value && to.path === '/login') {
    return navigateTo('/')
  }
})
