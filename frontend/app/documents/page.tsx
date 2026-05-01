import { Upload } from "lucide-react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";

const documents = [
  {
    filename: "northstar-invoice.pdf",
    type: "invoice",
    status: "completed",
    confidence: "93%",
    uploaded: "2026-04-28",
  },
  {
    filename: "enterprise-contract.txt",
    type: "contract",
    status: "processing",
    confidence: "pending",
    uploaded: "2026-04-28",
  },
  {
    filename: "receipts-batch.csv",
    type: "receipt",
    status: "completed",
    confidence: "88%",
    uploaded: "2026-04-27",
  },
] as const;

export default function DocumentsPage() {
  return (
    <DashboardShell
      title="Documents"
      description="Upload PDFs, receipts, contracts, CSVs, and text files into the mock AI extraction pipeline."
      action={
        <Button>
          <Upload className="h-4 w-4" />
          Upload
        </Button>
      }
    >
      <div className="grid gap-4 xl:grid-cols-[0.9fr_1.4fr]">
        <Card>
          <CardHeader>
            <CardTitle>Upload Queue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex min-h-64 flex-col items-center justify-center rounded-lg border border-dashed bg-background/70 p-8 text-center">
              <Upload className="mb-4 h-10 w-10 text-primary" />
              <p className="font-medium">Drop documents for extraction</p>
              <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                PDF, image, CSV, and TXT files are validated before background processing starts.
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recent Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <thead>
                <tr>
                  <Th>File</Th>
                  <Th>Type</Th>
                  <Th>Status</Th>
                  <Th>Confidence</Th>
                  <Th>Uploaded</Th>
                </tr>
              </thead>
              <tbody>
                {documents.map((document) => (
                  <tr key={document.filename}>
                    <Td className="font-medium">{document.filename}</Td>
                    <Td>{document.type}</Td>
                    <Td>
                      <Badge tone={document.status}>{document.status}</Badge>
                    </Td>
                    <Td>{document.confidence}</Td>
                    <Td className="text-muted-foreground">{document.uploaded}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
