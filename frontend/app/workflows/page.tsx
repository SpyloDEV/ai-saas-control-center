import { Play, Workflow } from "lucide-react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const workflows = [
  {
    name: "Document Intake",
    status: "active",
    steps: ["Document uploaded", "AI extraction", "Validation", "Notification"],
  },
  {
    name: "Contract Risk Review",
    status: "draft",
    steps: ["Text parser", "Risk classifier", "Operator review"],
  },
  {
    name: "CSV Normalization",
    status: "paused",
    steps: ["CSV parser", "Schema mapper", "Export"],
  },
] as const;

export default function WorkflowsPage() {
  return (
    <DashboardShell
      title="Workflows"
      description="Build automation sequences that connect document events, AI actions, validation, notifications, and logs."
      action={
        <Button>
          <Workflow className="h-4 w-4" />
          New Workflow
        </Button>
      }
    >
      <div className="grid gap-4 lg:grid-cols-3">
        {workflows.map((workflow) => (
          <Card key={workflow.name}>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle>{workflow.name}</CardTitle>
                <Badge tone={workflow.status}>{workflow.status}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <ol className="space-y-3">
                {workflow.steps.map((step, index) => (
                  <li key={step} className="flex items-center gap-3 text-sm">
                    <span className="flex h-7 w-7 items-center justify-center rounded-full border bg-background text-xs text-muted-foreground">
                      {index + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>
              <Button variant="secondary" className="mt-5 w-full">
                <Play className="h-4 w-4" />
                Run
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </DashboardShell>
  );
}
