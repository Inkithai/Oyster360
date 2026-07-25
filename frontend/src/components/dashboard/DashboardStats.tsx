'use client'

export function DashboardStats() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {[
        { label: "Active Batches", value: "24" },
        { label: "This Month Yield", value: "184 kg" },
        { label: "Success Rate", value: "87%" },
        { label: "Avg. Colonization", value: "18 days" },
      ].map((stat, index) => (
        <div key={index} className="rounded-xl border bg-card p-6">
          <div className="text-sm text-muted-foreground">{stat.label}</div>
          <div className="text-3xl font-semibold mt-2">{stat.value}</div>
        </div>
      ))}
    </div>
  )
}