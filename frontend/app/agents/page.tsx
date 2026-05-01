import { Bot, SlidersHorizontal } from "lucide-react";
import { AgentForm } from "@/components/forms/agent-form";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const agents = [
  {
    name: "Invoice Extractor",
    role: "document_processor",
    status: "active",
    description: "Extracts invoice fields, totals, line items, and confidence scores.",
  },
  {
    name: "Workflow Router",
    role: "automation_planner",
    status: "active",
    description: "Routes uploaded assets into extraction and validation workflows.",
  },
  {
    name: "Revenue QA",
    role: "validation_agent",
    status: "inactive",
    description: "Reviews extracted results and flags missing values for operators.",
  },
] as const;

export default function AgentsPage() {
  return (
    <DashboardShell
      title="AI Agents"
      description="Configure specialized agents with roles, instructions, model settings, and execution readiness."
      action={
        <Button variant="secondary">
          <SlidersHorizontal className="h-4 w-4" />
          Filters
        </Button>
      }
    >
      <div className="space-y-4">
        <AgentForm />
        <div className="grid gap-4 lg:grid-cols-3">
          {agents.map((agent) => (
            <Card key={agent.name}>
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="rounded-md bg-primary/15 p-2 text-primary">
                      <Bot className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle>{agent.name}</CardTitle>
                      <p className="text-sm text-muted-foreground">{agent.role}</p>
                    </div>
                  </div>
                  <Badge tone={agent.status}>{agent.status}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{agent.description}</p>
                <div className="mt-4 rounded-md border bg-background p-3 text-xs text-muted-foreground">
                  model_provider=mock · temperature=0.2
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardShell>
  );
}
