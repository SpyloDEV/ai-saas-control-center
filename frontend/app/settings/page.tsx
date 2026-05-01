import { ShieldCheck, Users } from "lucide-react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function SettingsPage() {
  return (
    <DashboardShell
      title="Settings"
      description="Manage workspace profile, team roles, mock invite flow, and security controls."
    >
      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Workspace</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input defaultValue="Acme AI" aria-label="Workspace name" />
            <Input defaultValue="acme-ai" aria-label="Workspace slug" />
            <Button>Save Workspace</Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Team Access</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3 rounded-md border bg-background p-3">
              <Users className="h-5 w-5 text-primary" />
              <div>
                <p className="text-sm font-medium">Invite member</p>
                <p className="text-xs text-muted-foreground">Mock invite flow for owners and admins.</p>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-md border bg-background p-3">
              <ShieldCheck className="h-5 w-5 text-emerald-300" />
              <div>
                <p className="text-sm font-medium">Workspace permissions</p>
                <p className="text-xs text-muted-foreground">owner · admin · member</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
