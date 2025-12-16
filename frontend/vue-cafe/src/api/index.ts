// src/api/index.ts
import axios from "axios";

const { VITE_API_BASE, VITE_CAL_BASE } = import.meta.env;

export const API_BASE = (VITE_API_BASE as string | undefined) ?? "/api/v1";


/** Axios client centralisé */
export const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  withCredentials: true, // si vous utilisez cookies de session
  headers: { "Content-Type": "application/json" },
});

/* Interceptors simples (log / gestion 401 exemple) */
client.interceptors.response.use(
  (resp) => resp,
  (err) => {
    // exemple: si 401 -> rediriger vers login (ou gérer le refresh)
    if (err.response?.status === 401) {
      // console.warn("Unauthorized - token expired?");
      // Optional: router.push('/login')
    }
    return Promise.reject(err);
  }
);

/* ---- API functions ---- */

// ----- Register ---- 
export interface UserProfile {
  login: string
  nom: string
  prenom: string
  email: string
  hpwd: string
  birthday: string 
  promo_id: string | false
  superuser: boolean
  teacher: boolean
  noteKfet: string
}
export async function registerUser(payload: UserProfile) {
  const { data } = await client.post("/users/create", payload);
  return data;
}

// ----- Login ----
// @ token/login 
// application/x-www-form-urlencoded
export async function loginUser({ username, password }: { username: string; password: string }) {
  const body = new URLSearchParams({
    grant_type: "password",
    username,
    password,
    // scope 
  });
  // Axios sets the header automatically for URLSearchParams,
  // but adding it is fine and explicit:
  return client.post("/token", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
}




// ----- Get Users INFO----
// JWTokens 
export async function getUsersInfo(token?: string) {
  const headers = token
    ? { Authorization: `Bearer ${token}` }
    : undefined;

  const { data } = await client.get("/users/me", { headers });
  return data;
}

// GET available calendars for the user
export async function getUserCalendars(token?: string) {
  const headers = token
    ? { Authorization: `Bearer ${token}` }
    : undefined;

  const { data } = await client.get("/calendars/available", { headers });
  return data;
}

// GET users list (admin)
export async function getUsersList(token:string){
  const headers = token
    ? { Authorization: `Bearer ${token}` }
    : undefined;

  const { data } = await client.get("/users/all", { headers });
  return data;
}



// ----- Modify User INFO ----
// modify API db user with frontend user
export async function modifyUserInfo(payload: Partial<UserProfile>, token?: string) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const { data } = await client.post("/users/modify", payload, { headers });
  return data;
}

export async function saveFavoriteCalendar(
  promo_id : string,
  token?: string,
) {
  return modifyUserInfo(
    { promo_id } as Partial<UserProfile>,
    token,
  );
}


function toBoolStr(v: unknown): boolean {
  // L’API renvoie "True"/"False" (strings)
  return String(v).toLowerCase() === 'true'
}

export function mapApiUser(u: any): UserProfile {
  // 
  return {
    login: u.login ?? '',
    nom: u.nom ?? '',
    prenom: u.prenom ?? '',
    email: u.email ?? '',
    birthday: u.birthday ?? '',      // ex: "2000-1-1"
    superuser: toBoolStr(u.superuser),
    teacher: toBoolStr(u.teacher),
    promo_id: String(u.promo_id),
    hpwd: '', // ne pas exposer le mot de passe
    noteKfet: u.noteKfet ?? '',
  }
}

// -----------------Gestion ICS---------------------------

// attraper ics pour une promo
export async function getICS(promo_id:string){
  console.log("Fetching ICS for promo_id:", promo_id);
  const { data } = await client.get(`/ics/${promo_id}`, {
    // On ajoute un timestamp pour éviter tout cache navigateur/proxy
    params: { t: Date.now() },
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      Pragma: 'no-cache',
    },
  });
  return data;
}

export async function deleteEvent(event_id:string){  
  const { data } = await client.get(`/ics/delete?uid_str=${event_id}`);
  return data;
}

export interface EventDetail {
  start: string
  end: string
  matiere: string
  type_cours: string
  infos_sup?: string
  classroom_str?: string
  user_id?: string | number
  promo_str?: string
}

export async function addEventToICS(payload: EventDetail) {
  const body = new URLSearchParams()
  body.set('start', payload.start)
  body.set('end', payload.end)
  body.set('matiere', payload.matiere)
  body.set('type_cours', payload.type_cours)
  if (payload.infos_sup) body.set('infos_sup', payload.infos_sup)
  if (payload.classroom_str) body.set('classroom_str', payload.classroom_str)
  if (payload.user_id !== undefined && payload.user_id !== null) {
    body.set('user_id', String(payload.user_id))
  }
  if (payload.promo_str) body.set('promo_str', payload.promo_str)

  const { data } = await client.post(`/ics/insert`, body, {
    headers: { 'Content-Type': 'application/json' },
  })
  return data
}


//import all classroom dispo
export async function getClassrooms(){  
  const { data } = await client.get(`/classrooms/all`);
  return data;
}

export async function getCSV(promo_id:string){
  const { data } = await client.get(`/csv/?promo_str=${promo_id}`, {
    responseType: 'blob',
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      Pragma: 'no-cache',
    },
  });
  return data;
}
