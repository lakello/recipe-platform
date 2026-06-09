import { useState } from 'react'
import { AdminLayout } from '@/widgets/admin-layout'
import { useAdminReports, useReviewReport, useDismissReport } from '@/features/admin/hooks/useAdmin'
import type { Report } from '@/features/admin/api/adminApi'
import { Button } from '@/shared/ui/Button'

const STATUS_LABELS: Record<string, string> = {
  pending: 'На рассмотрении',
  reviewed: 'Принята',
  dismissed: 'Отклонена',
}

const REASON_LABELS: Record<string, string> = {
  spam: 'Спам',
  offensive: 'Оскорбительный контент',
  misinformation: 'Дезинформация',
  other: 'Другое',
}

function ReportRow({ report }: { report: Report }) {
  const { mutate: review, isPending: isReviewing } = useReviewReport()
  const { mutate: dismiss, isPending: isDismissing } = useDismissReport()

  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="py-3 pr-4">
        <p className="text-sm font-medium text-gray-800">
          {REASON_LABELS[report.reason] ?? report.reason}
        </p>
        {report.description && (
          <p className="text-xs text-gray-500 mt-0.5 max-w-xs truncate">
            {report.description}
          </p>
        )}
        <p className="text-xs text-gray-400 mt-0.5">
          {report.target_type}: {report.target_id.slice(0, 8)}…
        </p>
      </td>
      <td className="py-3 pr-4">
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            report.status === 'pending'
              ? 'bg-yellow-100 text-yellow-700'
              : report.status === 'reviewed'
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-500'
          }`}
        >
          {STATUS_LABELS[report.status] ?? report.status}
        </span>
      </td>
      <td className="py-3 pr-4 text-xs text-gray-400">
        {new Date(report.created_at).toLocaleDateString('ru-RU')}
      </td>
      <td className="py-3 text-right">
        {report.status === 'pending' && (
          <div className="flex gap-2 justify-end">
            <Button
              loading={isReviewing}
              onClick={() => review(report.id)}
            >
              Принять
            </Button>
            <Button
              variant="secondary"
              loading={isDismissing}
              onClick={() => dismiss(report.id)}
            >
              Отклонить
            </Button>
          </div>
        )}
      </td>
    </tr>
  )
}

export function AdminReportsPage() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)
  const { data, isPending, error } = useAdminReports(page, statusFilter)

  return (
    <AdminLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Жалобы</h1>
        <div className="flex gap-2">
          {[undefined, 'pending', 'reviewed', 'dismissed'].map((s) => (
            <button
              key={String(s)}
              onClick={() => { setStatusFilter(s); setPage(1) }}
              className={`px-3 py-1.5 text-sm rounded-lg font-medium transition-colors ${
                statusFilter === s
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {s === undefined ? 'Все' : STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      </div>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {data && (
        <>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-4 py-3">Жалоба</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Дата</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="px-4">
                {data.items.map((r) => (
                  <ReportRow key={r.id} report={r} />
                ))}
              </tbody>
            </table>
            {data.items.length === 0 && (
              <p className="text-center text-gray-500 py-8">Жалоб нет.</p>
            )}
          </div>

          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-500">Всего: {data.total}</p>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 1}
              >
                ←
              </Button>
              <span className="text-sm text-gray-600 self-center">стр. {page}</span>
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.has_more}
              >
                →
              </Button>
            </div>
          </div>
        </>
      )}
    </AdminLayout>
  )
}
