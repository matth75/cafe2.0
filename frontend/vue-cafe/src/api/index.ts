// src/api/index.ts
import axios from "axios";

const { VITE_API_BASE, VITE_CAL_BASE } = import.meta.env;

export const API_BASE = (VITE_API_BASE as string | undefined) ?? "/api/v1";
export const CAL_BASE = (VITE_CAL_BASE as string | undefined) ?? "";

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

/* ---- Helpers / URLs ---- */
export function calendarIcsUrl(slug: string) {
  if (CAL_BASE) return `${CAL_BASE.replace(/\/$/, "")}/${slug}.ics`;
  // fallback: suppose API exposes /calendar/:slug.ics on root domain
  return `${API_BASE.replace(/\/api\/v?\d*$/, "")}/calendar/${slug}.ics`;
}

/* ---- API functions (exemples) ---- */

export interface RegisterPayload {
  login: string;
  email: string;
  nom: string;
  prenom: string;
  hpwd: string;
  superuser: boolean;
  owner: boolean;
  noteKfet: string;
}
export async function registerUser(payload: RegisterPayload) {
  const { data } = await client.post("/users/create", payload);
  return data;
}


export interface LoginPayload {
  login: string;
  hpwd: string;
}
export async function loginUser(payload: LoginPayload) {
  const { data } = await client.post("/token/login", payload);
  return data;
}

export async function getUsersInfo() {
  const { data } = await client.get("/users/info");
  return data;
}

export async function createUser(payload: { name: string; qty: number; mdp: string; mail: string }) {
  const { data } = await client.post("/users/create", payload);
  return data;
}

export async function getCalendars(params?: Record<string, any>) {
  const { data } = await client.get("/calendars", { params });
  return data;
}

export async function getEvents(calendarId: number | string, start?: string, end?: string) {
  const { data } = await client.get(`/calendars/${calendarId}/events`, { params: { start, end } });
  return data;
}

/* Export default pour facilité d'import */
export default {
  client,
  API_BASE,
  calendarIcsUrl,
  registerUser,
  loginUser,
  getUsersInfo,
  createUser,
  getCalendars,
  getEvents,
};
