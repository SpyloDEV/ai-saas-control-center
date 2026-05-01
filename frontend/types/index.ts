export type Status = "active" | "inactive" | "processing" | "completed" | "failed";

export type Agent = {
  id: string;
  name: string;
  description: string;
  role: string;
  model: string;
  status: "active" | "inactive";
  temperature: number;
};

export type DocumentRecord = {
  id: string;
  filename: string;
  status: "uploaded" | "processing" | "completed" | "failed";
  documentType: string;
  confidence: number;
  uploadedAt: string;
};

export type Workflow = {
  id: string;
  name: string;
  status: "draft" | "active" | "paused";
  steps: string[];
  lastRun: string;
};

export type Execution = {
  id: string;
  workflow: string;
  status: "queued" | "running" | "completed" | "failed";
  durationMs: number;
  createdAt: string;
};
