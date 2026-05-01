import { KeyRound, Plus } from "lucide-react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";

const keys = [
  { name: "Backend SDK", prefix: "sk_live_X9d2...", status: "active", created: "Apr 28" },
  { name: "Ops Dashboard", prefix: "sk_live_K2fa...", status: "active", created: "Apr 26" },
  { name: "Legacy ETL", prefix: "sk_live_7Qa1...", status: "revoked", created: "Apr 18" },
] as const;

export default function ApiKeysPage() {
  return (
    <DashboardShell
      title="API Keys"
      description="Issue and revoke workspace API keys while storing only hashed secrets in the backend."
      action={
        <Button>
          <Plus className="h-4 w-4" />
          Create Key
        </Button>
      }
    >
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <KeyRound className="h-5 w-5 text-primary" />
            <CardTitle>Workspace Keys</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <thead>
              <tr>
                <Th>Name</Th>
                <Th>Prefix</Th>
                <Th>Status</Th>
                <Th>Created</Th>
                <Th>Action</Th>
              </tr>
            </thead>
            <tbody>
              {keys.map((key) => (
                <tr key={key.name}>
                  <Td className="font-medium">{key.name}</Td>
                  <Td className="font-mono text-xs">{key.prefix}</Td>
                  <Td>
                    <Badge tone={key.status}>{key.status}</Badge>
                  </Td>
                  <Td className="text-muted-foreground">{key.created}</Td>
                  <Td>
                    <Button variant="ghost" className="h-8 px-2">
                      Revoke
                    </Button>
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
        </CardContent>
      </Card>
    </DashboardShell>
  );
}
