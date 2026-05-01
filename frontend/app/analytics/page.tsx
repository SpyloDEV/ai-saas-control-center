import { ExecutionChart } from "@/components/charts/execution-chart";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AnalyticsPage() {
  return (
    <DashboardShell
      title="Analytics"
      description="Track AI SaaS health across throughput, success rate, failures, processing speed, and adoption."
    >
      <div className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Success rate" value="98.4%" delta="+1.2%" />
          <KpiCard label="Failed executions" value={7} delta="-22%" />
          <KpiCard label="Avg processing" value="712 ms" delta="-84 ms" />
          <KpiCard label="Docs processed" value={842} delta="+18%" />
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Execution Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <ExecutionChart />
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
