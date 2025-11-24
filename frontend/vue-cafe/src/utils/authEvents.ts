export const AUTH_EVENT = 'cafe-auth-changed'

export interface AuthEventDetail {
  token?: string | null
  superuser?: boolean
  userId?: string | null
}

export function emitAuthEvent(detail: AuthEventDetail = {}) {
  if (typeof window === 'undefined') {
    return
  }

  window.dispatchEvent(new CustomEvent<AuthEventDetail>(AUTH_EVENT, { detail }))
}
