import { useEffect, useState } from 'react'
import { superAdminService, type ClinicDto, type ClinicUserDto } from '@/services/super-admin.service'
import { Building2, Users } from 'lucide-react'

export default function SuperAdminClinics() {
  const [count, setCount] = useState<number | null>(null)
  const [clinics, setClinics] = useState<ClinicDto[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [usersByClinic, setUsersByClinic] = useState<Record<string, ClinicUserDto[]>>({})
  const [expandedId, setExpandedId] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      try {
        const [countRes, listRes] = await Promise.all([
          superAdminService.getClinicsCount(),
          superAdminService.listClinics(0, 100),
        ])
        if (!cancelled) {
          setCount(countRes.count)
          setClinics(listRes.items)
          setTotal(listRes.total)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  async function loadUsers(clinicId: string) {
    if (usersByClinic[clinicId]) {
          setExpandedId(expandedId === clinicId ? null : clinicId)
          return
        }
    try {
      const { users } = await superAdminService.listClinicUsers(clinicId)
      setUsersByClinic((prev) => ({ ...prev, [clinicId]: users }))
      setExpandedId(clinicId)
    } catch {
      setUsersByClinic((prev) => ({ ...prev, [clinicId]: [] }))
      setExpandedId(clinicId)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Super Admin – Clinics</h1>
      <div className="rounded-lg bg-white/5 border border-white/10 p-4">
        <div className="flex items-center gap-2">
          <Building2 className="w-6 h-6 text-primary" />
          <span className="text-lg font-semibold">Onboarded clinics</span>
          <span className="text-2xl font-bold text-primary">{count ?? 0}</span>
        </div>
      </div>
      <div className="rounded-lg bg-white/5 border border-white/10 overflow-hidden">
        <div className="px-4 py-3 border-b border-white/10 font-medium">Clinic list</div>
        <ul className="divide-y divide-white/10">
          {clinics.length === 0 ? (
            <li className="px-4 py-8 text-center text-muted-foreground">No clinics yet</li>
          ) : (
            clinics.map((c) => (
              <li key={c.id} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{c.name}</div>
                    <div className="text-sm text-muted-foreground">{c.code} {c.address && ` · ${c.address}`}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => loadUsers(c.id)}
                    className="flex items-center gap-1 text-sm text-primary hover:underline"
                  >
                    <Users className="w-4 h-4" />
                    {expandedId === c.id ? 'Hide users' : 'Users'}
                  </button>
                </div>
                {expandedId === c.id && usersByClinic[c.id] !== undefined && (
                  <div className="mt-3 pl-4 border-l-2 border-primary/30">
                    <div className="text-sm font-medium text-muted-foreground mb-1">Users</div>
                    {usersByClinic[c.id].length === 0 ? (
                      <div className="text-sm text-muted-foreground">No users linked</div>
                    ) : (
                      <ul className="space-y-1 text-sm">
                        {usersByClinic[c.id].map((u) => (
                          <li key={u.id}>
                            {u.first_name} {u.last_name} ({u.email}) – {u.clinic_role}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  )
}
