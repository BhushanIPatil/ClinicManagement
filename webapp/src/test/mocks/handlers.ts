/**
 * MSW (Mock Service Worker) request handlers
 * 
 * Mock API responses for testing.
 */

import { http, HttpResponse } from 'msw'

const API_BASE = 'http://localhost:8000/api/v1'

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/auth/login`, () => {
    return HttpResponse.json({
      user: {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
        first_name: 'Test',
        last_name: 'User',
        role_names: ['ADMIN'],
      },
      tokens: {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
      },
    })
  }),

  http.get(`${API_BASE}/auth/me`, () => {
    return HttpResponse.json({
      id: '1',
      email: 'test@example.com',
      username: 'testuser',
      first_name: 'Test',
      last_name: 'User',
      role_names: ['ADMIN'],
    })
  }),

  // Appointments endpoints
  http.get(`${API_BASE}/appointments`, () => {
    return HttpResponse.json([])
  }),

  http.post(`${API_BASE}/appointments`, () => {
    return HttpResponse.json({
      id: '1',
      appointment_number: 'APT001',
      patient_id: '1',
      doctor_id: '1',
      appointment_date: '2025-01-25T10:00:00Z',
      status: 'SCHEDULED',
    }, { status: 201 })
  }),

  // Patients endpoints
  http.get(`${API_BASE}/patients`, () => {
    return HttpResponse.json({
      patients: [],
      total: 0,
      page: 1,
      page_size: 20,
    })
  }),
]
