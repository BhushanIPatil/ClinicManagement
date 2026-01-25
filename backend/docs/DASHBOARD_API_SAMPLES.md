# Dashboard API Examples

This document provides example JSON responses for all role-based dashboard endpoints.

## Endpoints

All dashboard endpoints follow the pattern: `GET /api/v1/dashboard/{role}`

- `/api/v1/dashboard/admin` - Admin dashboard
- `/api/v1/dashboard/doctor` - Doctor dashboard
- `/api/v1/dashboard/doctor/{doctor_id}` - Specific doctor dashboard (admin/HR only)
- `/api/v1/dashboard/nurse` - Nurse dashboard
- `/api/v1/dashboard/receptionist` - Receptionist dashboard
- `/api/v1/dashboard/accountant` - Accountant dashboard
- `/api/v1/dashboard/hr` - HR dashboard

## Example Responses

### Admin Dashboard

```json
{
  "role": "ADMIN",
  "generated_at": "2024-01-23T10:00:00Z",
  "widgets": [
    {
      "id": "recent_appointments",
      "type": "TABLE",
      "title": "Recent Appointments",
      "data": {
        "items": [
          {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "appointment_number": "APT-2024-001",
            "appointment_date": "2024-01-23T14:30:00Z",
            "status": "SCHEDULED"
          }
        ]
      },
      "position": 1,
      "size": "LARGE"
    },
    {
      "id": "revenue_chart",
      "type": "TREND_CHART",
      "title": "Revenue Trend",
      "data": {
        "trend": {
          "title": "Revenue Trend",
          "metric": "REVENUE",
          "period": "DAY",
          "data": [
            {
              "date": "2024-01-17",
              "value": "1500.00",
              "label": null
            },
            {
              "date": "2024-01-18",
              "value": "2300.00",
              "label": null
            }
          ],
          "unit": "USD"
        }
      },
      "position": 2,
      "size": "MEDIUM"
    }
  ],
  "stats": {
    "total_patients": {
      "title": "Total Patients",
      "value": 1250,
      "change": null,
      "trend": null,
      "icon": "users",
      "color": "blue"
    },
    "appointments_today": {
      "title": "Appointments Today",
      "value": 45,
      "change": 12.5,
      "trend": "UP",
      "icon": "calendar",
      "color": "green"
    },
    "revenue_today": {
      "title": "Revenue Today",
      "value": "8500.00",
      "change": 8.3,
      "trend": "UP",
      "icon": "dollar-sign",
      "color": "green"
    },
    "pending_invoices": {
      "title": "Pending Invoices",
      "value": 23,
      "change": null,
      "trend": null,
      "icon": "file-text",
      "color": "orange"
    },
    "active_doctors": {
      "title": "Active Doctors",
      "value": 15,
      "change": null,
      "trend": null,
      "icon": "user-md",
      "color": "blue"
    },
    "pending_queue": {
      "title": "Pending Tasks",
      "value": 8,
      "change": null,
      "trend": null,
      "icon": "list",
      "color": "red"
    }
  },
  "summary_counts": [
    {
      "label": "Total Appointments",
      "count": 450,
      "icon": "calendar",
      "color": null
    },
    {
      "label": "Total Revenue",
      "count": 125000,
      "icon": "dollar-sign",
      "color": null
    },
    {
      "label": "New Patients",
      "count": 85,
      "icon": "user-plus",
      "color": null
    },
    {
      "label": "Completed Appointments",
      "count": 420,
      "icon": "check-circle",
      "color": null
    }
  ],
  "trends": [
    {
      "title": "Appointments Trend",
      "metric": "APPOINTMENTS",
      "period": "DAY",
      "data": [
        {
          "date": "2024-01-17",
          "value": 38,
          "label": null
        },
        {
          "date": "2024-01-18",
          "value": 42,
          "label": null
        },
        {
          "date": "2024-01-19",
          "value": 45,
          "label": null
        }
      ],
      "unit": null
    },
    {
      "title": "Revenue Trend",
      "metric": "REVENUE",
      "period": "DAY",
      "data": [
        {
          "date": "2024-01-17",
          "value": "1500.00",
          "label": null
        },
        {
          "date": "2024-01-18",
          "value": "2300.00",
          "label": null
        },
        {
          "date": "2024-01-19",
          "value": "2800.00",
          "label": null
        }
      ],
      "unit": "USD"
    }
  ]
}
```

### Doctor Dashboard

```json
{
  "role": "DOCTOR",
  "generated_at": "2024-01-23T10:00:00Z",
  "doctor_id": "123e4567-e89b-12d3-a456-426614174000",
  "widgets": [
    {
      "id": "upcoming_appointments",
      "type": "TABLE",
      "title": "Upcoming Appointments",
      "data": {
        "items": [
          {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "appointment_number": "APT-2024-002",
            "appointment_date": "2024-01-23T11:00:00Z",
            "status": "SCHEDULED"
          },
          {
            "id": "123e4567-e89b-12d3-a456-426614174002",
            "appointment_number": "APT-2024-003",
            "appointment_date": "2024-01-23T14:00:00Z",
            "status": "SCHEDULED"
          }
        ]
      },
      "position": 1,
      "size": "LARGE"
    }
  ],
  "stats": {
    "appointments_today": {
      "title": "Appointments Today",
      "value": 8,
      "change": 14.3,
      "trend": "UP",
      "icon": "calendar",
      "color": "blue"
    },
    "patients_today": {
      "title": "Patients Today",
      "value": 6,
      "change": null,
      "trend": null,
      "icon": "users",
      "color": "green"
    }
  },
  "summary_counts": [
    {
      "label": "This Week",
      "count": 35,
      "icon": "calendar",
      "color": null
    },
    {
      "label": "This Month",
      "count": 145,
      "icon": "calendar",
      "color": null
    }
  ],
  "trends": [
    {
      "title": "My Appointments Trend",
      "metric": "APPOINTMENTS",
      "period": "DAY",
      "data": [
        {
          "date": "2024-01-17",
          "value": 6,
          "label": null
        },
        {
          "date": "2024-01-18",
          "value": 7,
          "label": null
        },
        {
          "date": "2024-01-19",
          "value": 8,
          "label": null
        }
      ],
      "unit": null
    }
  ]
}
```

### Receptionist Dashboard

```json
{
  "role": "RECEPTIONIST",
  "generated_at": "2024-01-23T10:00:00Z",
  "widgets": [
    {
      "id": "today_appointments",
      "type": "TABLE",
      "title": "Today's Appointments",
      "data": {
        "items": [
          {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "appointment_number": "APT-2024-001",
            "appointment_date": "2024-01-23T09:00:00Z",
            "status": "SCHEDULED"
          },
          {
            "id": "123e4567-e89b-12d3-a456-426614174002",
            "appointment_number": "APT-2024-002",
            "appointment_date": "2024-01-23T10:30:00Z",
            "status": "SCHEDULED"
          }
        ]
      },
      "position": 1,
      "size": "LARGE"
    }
  ],
  "stats": {
    "appointments_today": {
      "title": "Appointments Today",
      "value": 45,
      "change": null,
      "trend": null,
      "icon": "calendar",
      "color": "blue"
    },
    "new_patients_today": {
      "title": "New Patients Today",
      "value": 5,
      "change": null,
      "trend": null,
      "icon": "user-plus",
      "color": "green"
    },
    "pending_queue": {
      "title": "Pending Tasks",
      "value": 3,
      "change": null,
      "trend": null,
      "icon": "list",
      "color": "orange"
    }
  },
  "summary_counts": [
    {
      "label": "Upcoming Appointments",
      "count": 12,
      "icon": "calendar",
      "color": null
    }
  ],
  "trends": []
}
```

### Accountant Dashboard

```json
{
  "role": "ACCOUNTANT",
  "generated_at": "2024-01-23T10:00:00Z",
  "widgets": [
    {
      "id": "recent_payments",
      "type": "TABLE",
      "title": "Recent Payments",
      "data": {
        "items": [
          {
            "id": "123e4567-e89b-12d3-a456-426614174010",
            "payment_number": "PAY-2024-001",
            "amount": 500.0,
            "payment_date": "2024-01-23T09:15:00Z",
            "status": "COMPLETED"
          },
          {
            "id": "123e4567-e89b-12d3-a456-426614174011",
            "payment_number": "PAY-2024-002",
            "amount": 750.0,
            "payment_date": "2024-01-23T10:30:00Z",
            "status": "COMPLETED"
          }
        ]
      },
      "position": 1,
      "size": "LARGE"
    }
  ],
  "stats": {
    "revenue_today": {
      "title": "Revenue Today",
      "value": "8500.00",
      "change": null,
      "trend": null,
      "icon": "dollar-sign",
      "color": "green"
    },
    "pending_invoices": {
      "title": "Pending Invoices",
      "value": 23,
      "change": null,
      "trend": null,
      "icon": "file-text",
      "color": "orange"
    },
    "total_revenue_month": {
      "title": "Monthly Revenue",
      "value": "125000.00",
      "change": null,
      "trend": null,
      "icon": "dollar-sign",
      "color": "blue"
    }
  },
  "summary_counts": [
    {
      "label": "Paid Invoices",
      "count": 420,
      "icon": "check",
      "color": null
    },
    {
      "label": "Pending Payments",
      "count": 15,
      "icon": "clock",
      "color": null
    }
  ],
  "trends": [
    {
      "title": "Revenue Trend",
      "metric": "REVENUE",
      "period": "DAY",
      "data": [
        {
          "date": "2024-01-01",
          "value": "3500.00",
          "label": null
        },
        {
          "date": "2024-01-02",
          "value": "4200.00",
          "label": null
        }
      ],
      "unit": "USD"
    }
  ]
}
```

### Nurse Dashboard

```json
{
  "role": "NURSE",
  "generated_at": "2024-01-23T10:00:00Z",
  "widgets": [],
  "stats": {
    "patients_today": {
      "title": "Patients Today",
      "value": 35,
      "change": null,
      "trend": null,
      "icon": "users",
      "color": "blue"
    },
    "pending_tasks": {
      "title": "Pending Tasks",
      "value": 5,
      "change": null,
      "trend": null,
      "icon": "list",
      "color": "orange"
    }
  },
  "summary_counts": [
    {
      "label": "Today's Appointments",
      "count": 45,
      "icon": "calendar",
      "color": null
    }
  ],
  "trends": []
}
```

### HR Dashboard

```json
{
  "role": "HR",
  "generated_at": "2024-01-23T10:00:00Z",
  "widgets": [],
  "stats": {
    "total_employees": {
      "title": "Total Employees",
      "value": 85,
      "change": null,
      "trend": null,
      "icon": "users",
      "color": "blue"
    },
    "active_doctors": {
      "title": "Active Doctors",
      "value": 15,
      "change": null,
      "trend": null,
      "icon": "user-md",
      "color": "green"
    }
  },
  "summary_counts": [
    {
      "label": "Total Staff",
      "count": 85,
      "icon": "users",
      "color": null
    }
  ],
  "trends": []
}
```

## Cache Headers

All endpoints return cache-friendly headers:

- `Cache-Control: public, max-age=60` (default, 60 seconds)
- `Cache-Control: public, max-age=30` (receptionist - more frequent updates)
- `Cache-Control: public, max-age=300` (HR - less frequent updates)
- `ETag` header for conditional requests

## Performance Notes

- Single optimized endpoint per role
- Parallel database queries where possible
- Aggregated data to minimize database round trips
- Cache-friendly responses with appropriate TTL
- Fast response times (< 200ms typical)
