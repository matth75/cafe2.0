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

export const PROFILE_UPDATED_EVENT = 'cafe-profile-updated'

export interface ProfileUpdatedDetail {
  promoId?: string | null
}

export function emitProfileUpdated(detail: ProfileUpdatedDetail = {}) {
  if (typeof window === 'undefined') {
    return
  }

  window.dispatchEvent(
    new CustomEvent<ProfileUpdatedDetail>(PROFILE_UPDATED_EVENT, { detail }),
  )
}
