import { Activity } from "lucide-react";
import { LiveLogViewer } from "@/components/dashboard/live-log-viewer";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";

const executions = [
  {
    id: "exec_7d2",
    workflow: "Document Intake",
    status: "completed",
    duration: "812 ms",
    created: "2 min ago",
  },
  {
    id: "exec_7d1",
    workflow: "Contract Risk Review",
    status: "running",
    duration: "running",
    created: "5 min ago",
  },
  {
    id: "exec_7d0",
    workflow: "CSV Normalization",
    status: "failed",
    duration: "294 ms",
    created: "21 min ago",
  },
] as const;

export default function ExecutionsPage() {
  return (
    <DashboardShell
      title="Executions"
      description="Inspect execution history, retry behavior, live logs, duration, and operational outcomes."
      action={
        <div className="flex items-center gap-2 rounded-md border bg-card px-3 py-2 text-sm text-muted-foreground">
          <Activity className="h-4 w-4 text-primary" />
          Live stream ready
        </div>
      }
    >
      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle>Execution History</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <thead>
                <tr>
                  <Th>ID</Th>
                  <Th>Workflow</Th>
                  <Th>Status</Th>
                  <Th>Duration</Th>
                  <Th>Created</Th>
                </tr>
              </thead>
              <tbody>
                {executions.map((execution) => (
                  <tr key={execution.id}>
                    <Td className="font-mono text-xs">{execution.id}</Td>
                    <Td className="font-medium">{execution.workflow}</Td>
                    <Td>
                      <Badge tone={execution.status}>{execution.status}</Badge>
                    </Td>
                    <Td>{execution.duration}</Td>
                    <Td className="text-muted-foreground">{execution.created}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </CardContent>
        </Card>
        <LiveLogViewer />
      </div>
    </DashboardShell>
  );
}
