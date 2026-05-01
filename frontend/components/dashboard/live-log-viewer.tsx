import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const logs = [
  "[10:42:01] workflow started: document-intake",
  "[10:42:02] ai_extraction completed confidence=0.92",
  "[10:42:02] validation completed warnings=0",
  "[10:42:03] notification delivered channel=operations",
];

export function LiveLogViewer() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Live Execution Logs</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border bg-slate-950 p-4 font-mono text-xs text-cyan-100">
          {logs.map((line) => (
            <p key={line} className="py-1">
              {line}
            </p>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
