import { DashboardOverview } from "@/components/dashboard/dashboard-overview";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <DashboardShell
      title="Operations Dashboard"
      description="Monitor AI agents, document pipelines, workflow executions, and workspace activity from one control plane."
      action={<Button>Run Workflow</Button>}
    >
      <DashboardOverview />
    </DashboardShell>
  );
}
